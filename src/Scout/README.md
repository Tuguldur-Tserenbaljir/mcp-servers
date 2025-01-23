# Scout MCP server

Scout is an advanced, modular server built using the MCP framework, designed for seamless integration with OpenAI's API. It offers web scraping functionality alongside state management for search results and notes. With Scout, you can perform web searches, store results, and interact with the data using a user-friendly prompt and tool system.


### Server Overview
Scout is built on the MCP Server framework, providing a robust infrastructure for handling resources, tools, and prompts. It features:

- Web Scraping: Performs searches via OpenAI's API and stores results for further analysis.
- State Management: Uses key-value dictionaries for managing notes and search results.
- Extensibility: Supports custom prompts and tools to adapt to diverse application needs.
  
The server is configured to use OpenAI's GPT models, ensuring powerful and accurate natural language interactions.

### Tools

1. web-search
```bash
Purpose: Perform web searches using OpenAI’s API with the following parameters.

Input:

query: The search query string (required).
name: A unique identifier for saving the search result (required).
max_results: Maximum number of search results to return (default: 5, range: 1-10).
```

## Configuration

The server relies on a JSON-based configuration file to retrieve OpenAI credentials and settings. Ensure that the configuration file includes:

- OPENAI_API_KEY: Your OpenAI API key.
- OPENAI_MODEL: The OpenAI model to use (defaults to gpt-4 if not specified).
- Need to import neccessary libraries to .venv\Lib\site-packages

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "Scout": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\Users\btuud\Scout",
        "run",
        "Scout"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "Scout": {
      "command": "uvx",
      "args": [
        "Scout"
      ]
    }
  }
  ```
</details>

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory C:\Users\btuud\Scout run scout
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
