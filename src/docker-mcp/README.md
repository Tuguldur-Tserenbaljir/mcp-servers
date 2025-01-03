# 🐳 docker-mcp

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![smithery badge](https://smithery.ai/badge/docker-mcp)](https://smithery.ai/protocol/docker-mcp)

A powerful Model Context Protocol (MCP) server for Docker operations, enabling seamless container and compose stack management through Claude AI.

### 🎬 Demos
#### Deploying a Docker Compose Stack


https://github.com/user-attachments/assets/b5f6e40a-542b-4a39-ba12-7fdf803ee278



#### Analyzing Container Logs



https://github.com/user-attachments/assets/da386eea-2fab-4835-82ae-896de955d934



## 🚀 Quickstart

To try this in Claude Desktop app, add this to your claude config files:
```json
{
  "mcpServers": {
        "docker-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\btuud\\docker-mcp",
        "run",
        "docker-mcp",
        "C:\\Users\\btuud\\AppData\\Local\\Docker"
      ]
    }
  }
}
```

### Installing via Smithery

To install Docker MCP for Claude Desktop automatically via [Smithery](https://smithery.ai/protocol/docker-mcp):

```bash
npx @smithery/cli install docker-mcp --client claude
```

### Prerequisites

- UV (package manager)
- Python 3.12+
- Docker Desktop or Docker Engine
- Claude Desktop

### Installation

#### Claude Desktop Configuration

Add the server configuration to your Claude Desktop config file:

**MacOS**: `~/Library/Application\ Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>💻 Development Configuration</summary>

```json
{
  "mcpServers": {
    "docker-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "<path-to-docker-mcp>",
        "run",
        "docker-mcp"
      ]
    }
  }
}
```
</details>

<details>
  <summary>🚀 Production Configuration</summary>

```json
{
  "mcpServers": {
    "docker-mcp": {
      "command": "uvx",
      "args": [
        "docker-mcp"
      ]
    }
  }
}
```
</details>

## 🛠️ Development

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/QuantGeekDev/docker-mcp.git
cd docker-mcp
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
uv sync
```

### 🔍 Debugging

Launch the MCP Inspector for debugging:

```bash
npx @modelcontextprotocol/inspector uv --directory <path-to-docker-mcp> run docker-mcp
```

The Inspector will provide a URL to access the debugging interface.

# 🔨 Tools

### Containers

- `list_containers`
- `create_container`
- `run_container`
- `recreate_container`
- `start_container`
- `fetch_container_logs`
- `stop_container`
- `remove_container`

### Images

- `list_images`
- `pull_image`
- `push_image`
- `build_image`
- `remove_image`

### Networks

- `list_networks`
- `create_network`
- `remove_network`

### Volumes

- `list_volumes`
- `create_volume`
- `remove_volume`


## 🚧 Current Limitations

- No built-in environment variable support for containers
- No volume management
- No network management
- No container health checks
- No container restart policies
- No container resource limits

## 🤝 Contributing

1. Fork the repository from [docker-mcp](https://github.com/QuantGeekDev/docker-mcp)
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ✨ Authors

- **Alex Andru** - *Initial work | Core contributor* - [@QuantGeekDev](https://github.com/QuantGeekDev)
- **Ali Sadykov** - *Initial work  | Core contributor* - [@md-archive](https://github.com/md-archive)

---
Made with ❤️
