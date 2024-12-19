import asyncio
import json
import os
import aiohttp
import logging
from typing import Any, Dict, List, Optional

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

# Store notes as a simple key-value dict to demonstrate state management
logger = logging.getLogger(__name__)
notes: dict[str, str] = {}
search_results: dict[str, str] = {}  # Store search results

server = Server("Scout")

CONFIG_FILE_PATH = os.path.expanduser(r"C:\Users\btuud\AppData\Roaming\Claude\claude_desktop_config.json")


def load_openai_config() -> Dict[str, Any]:
    """
    Load OpenAI configuration from the claude desktop config file.
    Returns a dictionary with openai_api_key and openai_model.
    """
    try:
        logger.info(f"Reading configuration from: {CONFIG_FILE_PATH}")
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            config = json.load(config_file)
        
        # Navigate through the correct config structure
        if 'mcpServers' not in config:
            raise ValueError("Missing 'mcpServers' section in config file")
            
        if 'Scout' not in config['mcpServers']:
            raise ValueError("Missing 'Scout' section in mcpServers config")
            
        if 'env' not in config['mcpServers']['Scout']:
            raise ValueError("Missing 'env' section in Scout config")
            
        env_config = config['mcpServers']['Scout']['env']
        
        # Check for required fields
        if 'OPENAI_API_KEY' not in env_config:
            raise ValueError("Missing OPENAI_API_KEY in configuration")
            
        if 'OPENAI_MODEL' not in env_config:
            logger.warning("OPENAI_MODEL not specified, defaulting to gpt-4")
            env_config['OPENAI_MODEL'] = 'gpt-4'

        return {
            "openai_api_key": env_config['OPENAI_API_KEY'],
            "openai_model": env_config['OPENAI_MODEL']
        }
        
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {CONFIG_FILE_PATH}")
        raise ValueError(f"Configuration file not found: {CONFIG_FILE_PATH}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {CONFIG_FILE_PATH}")
        raise ValueError(f"Invalid JSON in configuration file: {str(e)}")
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        raise ValueError(f"Error loading configuration: {str(e)}")



@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available note and search resources.
    Each note and search result is exposed as a resource with a custom URI scheme.
    """
    note_resources = [
        types.Resource(
            uri=AnyUrl(f"note://internal/{name}"),
            name=f"Note: {name}",
            description=f"A simple note named {name}",
            mimeType="text/plain",
        )
        for name in notes
    ]
    
    search_resources = [
        types.Resource(
            uri=AnyUrl(f"search://result/{name}"),
            name=f"Search: {name}",
            description=f"Web search result for query '{name}'",
            mimeType="text/plain",
        )
        for name in search_results
    ]
    
    return note_resources + search_resources

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific note or search result's content by its URI.
    """
    if uri.scheme == "search":
        name = uri.path.lstrip("/")
        if name in search_results:
            return search_results[name]
        raise ValueError(f"Search result not found: {name}")
    
    raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts for notes and search results.
    """
    return [
        types.Prompt(
            name="summarize-search",
            description="Creates a summary of search results",
            arguments=[
                types.PromptArgument(
                    name="style",
                    description="Style of the summary (brief/detailed)",
                    required=False,
                )
            ],
        )
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a prompt by combining arguments with server state.
    Supports prompts for notes and search results.
    """
    if name == "summarize-notes":
        style = (arguments or {}).get("style", "brief")
        detail_prompt = " Give extensive details." if style == "detailed" else ""

        return types.GetPromptResult(
            description="Summarize the current notes",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Here are the current notes to summarize:{detail_prompt}\n\n"
                        + "\n".join(
                            f"- {name}: {content}"
                            for name, content in notes.items()
                        ),
                    ),
                )
            ],
        )
    
    elif name == "summarize-search":
        style = (arguments or {}).get("style", "brief")
        detail_prompt = " Give extensive details." if style == "detailed" else ""

        return types.GetPromptResult(
            description="Summarize the current search results",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Here are the current search results to summarize:{detail_prompt}\n\n"
                        + "\n".join(
                            f"- {name}: {content}"
                            for name, content in search_results.items()
                        ),
                    ),
                )
            ],
        )
    
    raise ValueError(f"Unknown prompt: {name}")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available tools, including web search and note management.
    """
    return [
        types.Tool(
            name="web-search",
            description="Perform a web search using OpenAI's API",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "name": {"type": "string", "description": "Name to save the search result"},
                    "max_results": {
                        "type": "integer", 
                        "description": "Maximum number of search results",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 5
                    }
                },
                "required": ["query", "name"]
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, 
    arguments: Optional[dict]
) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests for adding notes and web searching.
    """

    try:
        if name != "web-search":
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

        if not arguments:
            return [types.TextContent(type="text", text="Arguments are required")]

        # Convert max_results from string to int if needed
        if 'max_results' in arguments:
            try:
                arguments['max_results'] = int(arguments['max_results'])
            except (ValueError, TypeError):
                arguments['max_results'] = 5

        # Load configuration
        try:
            config = load_openai_config()
        except Exception as e:
            logger.error(f"Failed to load OpenAI config: {str(e)}")
            return [types.TextContent(type="text", text=f"Configuration error: {str(e)}")]
        
        # Validate OpenAI configuration
        openai_api_key = config.get('openai_api_key')
        if not openai_api_key:
            return [types.TextContent(type="text", text="OpenAI API key not found in configuration")]

        openai_model = config.get('openai_model', 'gpt-3.5-turbo')

        # Validate required arguments
        if 'query' not in arguments:
            return [types.TextContent(type="text", text="Search query is required")]
        if 'name' not in arguments:
            return [types.TextContent(type="text", text="Name is required")]

        query = arguments['query']
        name = arguments['name']
        max_results = arguments.get('max_results', 5)

        # Perform web search using OpenAI API
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": openai_model,
                "messages": [
                    {
                        "role": "user", 
                        "content": f"Web search results for: {query}. "
                                 f"Provide {max_results} concise, relevant results."
                    }
                ],
                "max_tokens": 1000
            }
            
            async with session.post(
                "https://api.openai.com/v1/chat/completions", 
                headers=headers, 
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return [types.TextContent(type="text", text=f"OpenAI API error: {error_text}")]
                
                result = await response.json()
                search_content = result['choices'][0]['message']['content']
                
                # Store search results in the global dictionary
                global search_results
                search_results[name] = search_content

                # Notify clients that resources have changed
                if hasattr(server.request_context.session, 'send_resource_list_changed'):
                    await server.request_context.session.send_resource_list_changed()

                return [types.TextContent(
                    type="text",
                    text=f"Saved search results for '{name}': {search_content}"
                )]

    except Exception as e:
        logger.error(f"Error in web search tool: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

# Rest of the existing main function remains the same
async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="Scout",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
