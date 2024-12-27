import asyncio
import signal
import sys
from typing import List, Dict, Any
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from .handlers import DockerHandlers
from pydantic import AnyUrl
import mcp.types as types
import os
import yaml

server = Server("docker-mcp")

@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """
    List available resources like template files and documentation.
    Returns a list of Resource objects with URIs and descriptions.
    """
    return [
        types.Resource(
            name="web-stack-template",
            uri="docker://templates/compose/web-stack.yml",
            description="Basic web application stack template with nginx and backend service"
        ),
        types.Resource(
            name="database-template",
            uri="docker://templates/compose/database.yml",
            description="Database service template with volume persistence"
        ),
        types.Resource(
            name="nginx-config",
            uri="docker://templates/container/nginx.json",
            description="Nginx container configuration template"
        ),
        types.Resource(
            name="deployment-guide",
            uri="docker://docs/deployment-guide.md",
            description="Best practices for Docker deployments"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read and return the content of a requested resource.
    Handles different resource types (templates, docs) based on URI.
    """
    # Convert URI to path segments
    path_parts = str(uri).replace("docker://", "").split("/")
    
    # Define template contents
    templates = {
        "templates/compose/web-stack.yml": """
version: '3.8'
services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    depends_on:
      - backend
  backend:
    image: python:3.9-slim
    environment:
      - DATABASE_URL=postgres://db:5432
    depends_on:
      - db
  db:
    image: postgres:13
    environment:
      - POSTGRES_PASSWORD=example
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
""",
        "templates/compose/database.yml": """
version: '3.8'
services:
  db:
    image: postgres:13
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  db_data:
    driver: local
""",
        "templates/container/nginx.json": """
{
    "image": "nginx:latest",
    "name": "web-server",
    "ports": {
        "80": "80",
        "443": "443"
    },
    "environment": {
        "NGINX_HOST": "localhost",
        "NGINX_PORT": "80"
    },
    "volumes": [
        "/etc/nginx/conf.d:/etc/nginx/conf.d"
    ]
}
""",
        "docs/deployment-guide.md": """
# Docker Deployment Best Practices

## Container Guidelines
1. Use specific version tags for images
2. Implement health checks
3. Set resource limits

## Compose Guidelines
1. Use version 3.8 or higher
2. Define networks explicitly
3. Use secrets for sensitive data

## Security Guidelines
1. Run containers as non-root
2. Scan images for vulnerabilities
3. Use read-only root filesystem
"""
    }

    # Convert path parts to resource path
    resource_path = "/".join(path_parts)
    
    if resource_path in templates:
        return templates[resource_path]
    else:
        raise ValueError(f"Resource not found: {uri}")

@server.list_prompts()
async def handle_list_prompts() -> List[types.Prompt]:
    return [
        types.Prompt(
            name="deploy-stack",
            description="Generate and deploy a Docker stack based on requirements",
            arguments=[
                types.PromptArgument(
                    name="requirements",
                    description="Description of the desired Docker stack",
                    required=True
                ),
                types.PromptArgument(
                    name="project_name",
                    description="Name for the Docker Compose project",
                    required=True
                )
            ]
        )
    ]


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: Dict[str, str] | None) -> types.GetPromptResult:
    if name != "deploy-stack":
        raise ValueError(f"Unknown prompt: {name}")

    if not arguments or "requirements" not in arguments or "project_name" not in arguments:
        raise ValueError("Missing required arguments")

    system_message = (
        "You are a Docker deployment specialist. Generate appropriate Docker Compose YAML or "
        "container configurations based on user requirements. For simple single-container "
        "deployments, use the create-container tool. For multi-container deployments, generate "
        "a docker-compose.yml and use the deploy-compose tool. To access logs, first use the "
        "list-containers tool to discover running containers, then use the get-logs tool to "
        "retrieve logs for a specific container."
    )

    user_message = f"""Please help me deploy the following stack:
Requirements: {arguments['requirements']}
Project name: {arguments['project_name']}

Analyze if this needs a single container or multiple containers. Then:
1. For single container: Use the create-container tool with format:
{{
    "image": "image-name",
    "name": "container-name",
    "ports": {{"80": "80"}},
    "environment": {{"ENV_VAR": "value"}}
}}

2. For multiple containers: Use the deploy-compose tool with format:
{{
    "project_name": "example-stack",
    "compose_yaml": "version: '3.8'\\nservices:\\n  service1:\\n    image: image1:latest\\n    ports:\\n      - '8080:80'"
}}"""

    return types.GetPromptResult(
        description="Generate and deploy a Docker stack",
        messages=[
            types.PromptMessage(
                role="system",
                content=types.TextContent(
                    type="text",
                    text=system_message
                )
            ),
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=user_message
                )
            )
        ]
    )

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name="create-container",
            description="Create a new standalone Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "image": {"type": "string"},
                    "name": {"type": "string"},
                    "ports": {
                        "type": "object",
                        "additionalProperties": {"type": "string"}
                    },
                    "environment": {
                        "type": "object",
                        "additionalProperties": {"type": "string"}
                    }
                },
                "required": ["image"]
            }
        ),
        types.Tool(
            name="deploy-compose",
            description="Deploy a Docker Compose stack",
            inputSchema={
                "type": "object",
                "properties": {
                    "compose_yaml": {"type": "string"},
                    "project_name": {"type": "string"}
                },
                "required": ["compose_yaml", "project_name"]
            }
        ),
        types.Tool(
            name="get-logs",
            description="Retrieve the latest logs for a specified Docker container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_name": {"type": "string"}
                },
                "required": ["container_name"]
            }
        ),
        types.Tool(
            name="list-containers",
            description="List all Docker containers",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any] | None) -> List[types.TextContent]:
    if not arguments and name != "list-containers":
        raise ValueError("Missing arguments")

    try:
        if name == "create-container":
            return await DockerHandlers.handle_create_container(arguments)
        elif name == "deploy-compose":
            return await DockerHandlers.handle_deploy_compose(arguments)
        elif name == "get-logs":
            return await DockerHandlers.handle_get_logs(arguments)
        elif name == "list-containers":
            return await DockerHandlers.handle_list_containers(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)} | Arguments: {arguments}")]


async def main():
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="docker-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def handle_shutdown(signum, frame):
    print("Shutting down gracefully...")
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())