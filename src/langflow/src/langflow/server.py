import asyncio
import requests
import json
import os
from uuid import uuid4
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio
from datetime import datetime
from typing import Optional, Dict, Any
# Store notes as a simple key-value dict to demonstrate state management
notes: dict[str, str] = {}

server = Server("langflow")

LANGFLOW_API_URL = "http://localhost:7860/api/v1/flows/"

def extract_component_info(component_data: dict) -> tuple[Optional[dict], Optional[str], Optional[dict]]:
    try:
        nodes = component_data.get("data", {}).get("nodes", [])
        if not nodes:
            return None, None, None
            
        node = nodes[0]
        node_data = node.get("data", {})
        
        component_type = node_data.get("type", "")
        if not component_type:
            return None, None, None
            
        return node_data.get("node", {}), component_type, node
        
    except Exception as e:
        print(f"Error extracting component info: {str(e)}")
        return None, None, None
    
@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available note resources.
    Each note is exposed as a resource with a custom note:// URI scheme.
    """
    return [
        types.Resource(
            uri=AnyUrl(f"note://internal/{name}"),
            name=f"Note: {name}",
            description=f"A simple note named {name}",
            mimeType="text/plain",
        )
        for name in notes
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific note's content by its URI.
    The note name is extracted from the URI host component.
    """
    if uri.scheme != "note":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    name = uri.path
    if name is not None:
        name = name.lstrip("/")
        return notes[name]
    raise ValueError(f"Note not found: {name}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts.
    Each prompt can have optional arguments to customize its behavior.
    """
    return [
        types.Prompt(
            name="summarize-notes",
            description="Creates a summary of all notes",
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
    The prompt includes all current notes and can be customized via arguments.
    """
    if name != "summarize-notes":
        raise ValueError(f"Unknown prompt: {name}")

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

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools for flow management.
    """
    return [
        types.Tool(
            name="list-flows",
            description="List available flows",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter_name": {"type": "string", "description": "Optional flow name to filter"},
                },
                "required": [],
            },
        ),
        types.Tool(
            name="create-flow",
            description="Create a new flow",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Name of the new flow"},
                    "description": {"type": "string", "description": "Description of the flow"},
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="delete-flow",
            description="Delete a specific flow by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "flow_id": {"type": "string", "description": "ID of the flow to delete"},
                },
                "required": ["flow_id"],
            },
        ),
        types.Tool(
            name="upload-saved-component",
            description="Upload a saved flow component from JSON file",
            inputSchema={
                "type": "object",
                "properties": {
                    "json_file_path": {"type": "string", "description": "Full path to the JSON flow file"},
                },
                "required": ["json_file_path"],
            },
        ),
        types.Tool(
            name="add-component-to-flow",
            description="Add a component to an existing flow",
            inputSchema={
                "type": "object",
                "properties": {
                    "component_path": {"type": "string", "description": "Full path to the component JSON file"},
                    "flow_id": {"type": "string", "description": "ID of the flow to add the component to"},
                    "x": {"type": "integer", "description": "X coordinate for component placement", "default": 100},
                    "y": {"type": "integer", "description": "Y coordinate for component placement", "default": 100},
                },
                "required": ["component_path", "flow_id"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests for flow management.
    """
    try:
        base_url = LANGFLOW_API_URL
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if name == "list-flows":
            url = base_url
            filter_name = arguments.get("filter_name") if arguments else None
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            flows = response.json()

            if filter_name:
                flows = [flow for flow in flows if flow['name'] == filter_name]

            flow_info = []
            for flow in flows:
                flow_info.append(f"ID: {flow['id']}, Name: {flow['name']}")

            return [
                types.TextContent(
                    type="text",
                    text="\n".join(flow_info) if flow_info else "No flows found."
                )
            ]

        elif name == "create-flow":
            if not arguments or not arguments.get("name"):
                raise ValueError("Flow name is required")

            payload = {
                "name": arguments["name"],
                "description": arguments.get("description", ""),
                "data": {
                    "nodes": [],
                    "edges": []
                }
            }

            response = requests.post(base_url, 
                                     headers=headers, 
                                     data=json.dumps(payload))
            response.raise_for_status()

            return [
                types.TextContent(
                    type="text",
                    text=f"Flow created successfully: {response.text}"
                )
            ]

        elif name == "delete-flow":
            if not arguments or not arguments.get("flow_id"):
                raise ValueError("Flow ID is required")

            url = f"{base_url}{arguments['flow_id']}"
            response = requests.delete(url, headers=headers)
            response.raise_for_status()

            return [
                types.TextContent(
                    type="text",
                    text=f"Flow deleted successfully: {response.text}"
                )
            ]

        elif name == "upload-saved-component":
            if not arguments or not arguments.get("json_file_path"):
                raise ValueError("JSON file path is required")

            json_file_path = arguments["json_file_path"]
            
            try:
                with open(json_file_path, 'r') as file:
                    flow_data = json.load(file)
                
                response = requests.post(
                    base_url,
                    json=flow_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                response.raise_for_status()
                result = response.json()

                return [
                    types.TextContent(
                        type="text",
                        text=f"Flow uploaded successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" +
                             "\n".join(f"{key}: {value}" for key, value in result.items())
                    )
                ]
            
            except FileNotFoundError:
                raise ValueError(f"The file {json_file_path} was not found.")
            except json.JSONDecodeError:
                raise ValueError(f"The file {json_file_path} is not a valid JSON file.")
            except requests.exceptions.RequestException as e:
                raise ValueError(f"Error making the request to Langflow API: {str(e)}")

        if name == "add-component-to-flow":
            if not arguments or not arguments.get("component_path") or not arguments.get("flow_id"):
                raise ValueError("Component path and flow ID are required")

            component_path = arguments["component_path"]
            flow_id = arguments["flow_id"]
            position = {
                "x": arguments.get("x", 100),
                "y": arguments.get("y", 100)
            }

            # First, get the existing flow
            flow_endpoint = f"{base_url.rstrip('/')}/{flow_id}"
            response = requests.get(flow_endpoint)
            response.raise_for_status()
            flow_data = response.json()
            
            # Read the component JSON
            with open(component_path, 'r') as file:
                component_data = json.load(file)
            
            # Extract component info
            component_node, component_type, node_template = extract_component_info(component_data)
            if not component_node or not component_type or not node_template:
                raise ValueError("Could not extract component information")
            
            # Create node in the format expected by Langflow
            new_id = f"{component_type}-{str(uuid4())[:6]}"
            
            # Start with the template from the component
            new_node = {
                "id": new_id,
                "type": "genericNode",
                "position": position,
                "data": {
                    "node": component_node,
                    "id": new_id,
                    "type": component_type
                }
            }
            
            # Copy additional fields from the template
            for field in ["selected", "width", "height", "dragging", "positionAbsolute"]:
                if field in node_template:
                    new_node[field] = node_template[field]
                    
            # Copy additional data fields from the template
            for field in ["value", "showNode", "display_name", "description"]:
                if field in node_template.get("data", {}):
                    new_node["data"][field] = node_template["data"][field]
            
            # Add the component to the flow's data
            if "data" in flow_data and "nodes" in flow_data["data"]:
                flow_data["data"]["nodes"].append(new_node)
            else:
                raise ValueError("Invalid flow data structure")
            
            # Update the flow with the new component
            update_endpoint = f"{base_url.rstrip('/')}/{flow_id}"
            update_response = requests.patch(
                update_endpoint,
                json=flow_data,
                headers={'Content-Type': 'application/json'}
            )
            
            update_response.raise_for_status()
            result = update_response.json()

            return [
                types.TextContent(
                    type="text",
                    text=f"Component added successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" +
                         "\n".join(f"{key}: {value}" for key, value in result.items())
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except (requests.RequestException, ValueError) as e:
        return [
            types.TextContent(
                type="text",
                text=f"Error in flow operation: {str(e)}"
            )
        ]
    
async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="langflow",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )