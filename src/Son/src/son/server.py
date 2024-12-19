import asyncio
import json
import os
from typing import Any, Dict, List, Optional
import requests

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

from qdrant_client import QdrantClient, models
from qdrant_client.http import models as rest
from qdrant_client.models import Distance, VectorParams
# Store notes as a simple key-value dict to demonstrate state management
notes: dict[str, str] = {}
search_results: dict[str, str] = {}  # Store search results

server = Server("Scout")

def get_qdrant_client():
    return QdrantClient(
        url="http://localhost:6333",
        api_key="A1B2C3D4E5"  # Configure with your API key
    )

def get_collection_list(client) -> List[str]:
    """Helper function to get list of collections"""
    try:
        collections = client.get_collections()
        return [collection.name for collection in collections.collections]
    except Exception:
        return []
    
@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available Qdrant collections as resources.
    Each collection is exposed as a resource with a custom URI scheme.
    """
    client = get_qdrant_client()
    collections = get_collection_list(client)
    
    collection_resources = [
        types.Resource(
            uri=AnyUrl(f"qdrant://collection/{name}"),
            name=f"Collection: {name}",
            description=f"Qdrant vector collection: {name}",
            mimeType="application/json",
        )
        for name in collections
    ]
    
    return collection_resources

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific collection's information by its URI.
    """
    if uri.scheme == "qdrant":
        client = get_qdrant_client()
        collection_name = uri.path.lstrip("/")
        
        try:
            collection_info = client.get_collection(collection_name)
            info_dict = {
                "name": collection_name,
                "status": str(collection_info.status),
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "segments_count": collection_info.segments_count,
                "optimizer_status": str(collection_info.optimizer_status),
                "vector_config": {
                    "size": collection_info.config.params.vectors.size,
                    "distance": str(collection_info.config.params.vectors.distance)
                }
            }
            return json.dumps(info_dict, indent=2)
        except Exception as e:
            raise ValueError(f"Error reading collection: {str(e)}")
    
    raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts for Qdrant collection management.
    """
    return [
        types.Prompt(
            name="qdrant-system",
            description="Manage and analyze Qdrant vector collections",
            arguments=[
                types.PromptArgument(
                    name="action",
                    description="Action to perform (create/read/delete/analyze)",
                    required=True,
                ),
                types.PromptArgument(
                    name="collection_name",
                    description="Name of the collection to work with",
                    required=True,
                ),
                types.PromptArgument(
                    name="detail_level",
                    description="Level of detail in analysis (brief/detailed)",
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
    Generate prompts for Qdrant collection management and analysis.
    """
    if name == "qdrant-system":
        if not arguments:
            raise ValueError("Arguments required for qdrant-system prompt")
        
        action = arguments.get("action")
        collection_name = arguments.get("collection_name")
        detail_level = arguments.get("detail_level", "brief")
        
        if not action or not collection_name:
            raise ValueError("Action and collection_name are required")
        
        client = get_qdrant_client()
        
        if action == "analyze":
            try:
                collection_info = client.get_collection(collection_name)
                detail_prompt = " Provide extensive analysis." if detail_level == "detailed" else ""
                
                return types.GetPromptResult(
                    description=f"Analyze Qdrant collection: {collection_name}",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"Please analyze this Qdrant collection:{detail_prompt}\n\n"
                                     f"Collection: {collection_name}\n"
                                     f"Status: {collection_info.status}\n"
                                     f"Vectors: {collection_info.vectors_count}\n"
                                     f"Points: {collection_info.points_count}\n"
                                     f"Segments: {collection_info.segments_count}\n"
                                     f"Vector Size: {collection_info.config.params.vectors.size}\n"
                                     f"Distance: {collection_info.config.params.vectors.distance}"
                            ),
                        )
                    ],
                )
            except Exception as e:
                raise ValueError(f"Error analyzing collection: {str(e)}")
        
        return types.GetPromptResult(
            description=f"Manage Qdrant collection: {collection_name}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Please help me {action} the Qdrant collection named '{collection_name}'."
                    ),
                )
            ],
        )
    
    raise ValueError(f"Unknown prompt: {name}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools for Qdrant vector database management.
    """
    return [
        types.Tool(
            name="qdrant-write-collection",
            description="Create a new Qdrant collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_name": {"type": "string"},
                    "vector_size": {"type": "integer", "minimum": 1, "default": 384},
                    "distance": {
                        "type": "string", 
                        "enum": ["Cosine", "Euclidean", "Dot"],
                        "default": "Cosine"
                    }
                },
                "required": ["collection_name"]
            },
        ),
        types.Tool(
            name="qdrant-read-collection",
            description="Read information about a Qdrant collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_name": {"type": "string"}
                },
                "required": ["collection_name"]
            },
        ),
        types.Tool(
            name="qdrant-delete-collection",
            description="Delete a Qdrant collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_name": {"type": "string"}
                },
                "required": ["collection_name"]
            },
        ),
        types.Tool(
            name="qdrant-list-collections",
            description="List all available Qdrant collections",
            inputSchema={
                "type": "object",
                "properties": {}
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests for Qdrant collection management.
    """
    client = get_qdrant_client()
    
    if name == "qdrant-list-collections":
        try:
            collections = client.get_collections()
            if collections.collections:
                collection_names = [col.name for col in collections.collections]
                return [
                    types.TextContent(
                        type="text",
                        text=f"Available collections:\n{', '.join(collection_names)}"
                    )
                ]
            else:
                return [
                    types.TextContent(
                        type="text",
                        text="No collections currently exist."
                    )
                ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error listing collections: {str(e)}"
                )
            ]
        
    elif name == "qdrant-write-collection":
        collection_name = arguments.get("collection_name")
        vector_size = arguments.get("vector_size", 384)  # Default to 384 as per your curl example
        distance = arguments.get("distance", "Cosine")

        if not collection_name:
            raise ValueError("Collection name is required")

        # Map distance string to Qdrant Distance enum
        distance_map = {
            "Cosine": Distance.COSINE,
            "Euclidean": Distance.EUCLID,
            "Dot": Distance.DOT
        }

        try:
            # Create collection with vector configuration
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=distance_map.get(distance, Distance.COSINE)
                )
            )
            
            return [
                types.TextContent(
                    type="text",
                    text=f"Created collection '{collection_name}' with vector size {vector_size} and {distance} distance"
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text", 
                    text=f"Error creating collection: {str(e)}"
                )
            ]
    
    elif name == "qdrant-read-collection":
        collection_name = arguments.get("collection_name")
        
        if not collection_name:
            raise ValueError("Collection name is required")

        try:
            collection_info = client.get_collection(collection_name)
            return [
                types.TextContent(
                    type="text",
                    text=f"Collection Details:\n"
                         f"Name: {collection_name}\n"
                         f"Status: {collection_info.status}\n"
                         f"Vectors Count: {collection_info.vectors_count}\n"
                         f"Points Count: {collection_info.points_count}\n"
                         f"Segments Count: {collection_info.segments_count}\n"
                         f"Optimization Status: {collection_info.optimizer_status}\n"
                         f"Vector Configuration: {collection_info.config.params.vectors}"
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text", 
                    text=f"Error reading collection '{collection_name}': {str(e)}"
                )
            ]

    elif name == "qdrant-delete-collection":
        collection_name = arguments.get("collection_name")
        
        if not collection_name:
            raise ValueError("Collection name is required")

        try:
            # Check if the collection exists
            collections = client.get_collections()
            if collection_name not in [col.name for col in collections.collections]:
                return [
                    types.TextContent(
                        type="text",
                        text=f"Collection '{collection_name}' does not exist. Nothing to delete."
                    )
                ]

            client.delete_collection(collection_name)
            return [
                types.TextContent(
                    type="text",
                    text=f"Successfully deleted collection '{collection_name}'"
                )
            ]
        except Exception as e:
            return [
                types.TextContent(
                    type="text", 
                    text=f"Error deleting collection '{collection_name}': {str(e)}"
                )
            ]

    raise ValueError(f"Unknown tool: {name}")

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