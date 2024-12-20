# Son MCP server

Son is an efficient and versatile server designed to interface with Qdrant, a high-performance vector database optimized for neural search applications. This server leverages the Message Communication Protocol (MCP) framework to facilitate seamless management and exploration of vector collections in Qdrant.


### Server Overview
Son offers a robust set of tools and prompts to streamline operations on Qdrant collections, including creating, reading, deleting, and listing collections. By leveraging MCP's capabilities, Scout ensures efficient state management and supports advanced vector database workflows.

Key features:
  
- Collection Management: Create, read, delete, and list Qdrant collections effortlessly.
- Custom Prompts: Interactive prompts for managing and analyzing vector collections.
- Tool Support: Tools designed for intuitive interaction with Qdrant's vector collections.
- MCP Compatibility: Full integration with MCP for stateful operations and efficient resource handling.
  
Son is built using Python and integrates with the QdrantClient library for interacting with Qdrant instances.

### Resources

This Qdrant MCP server implementation leverages the following libraries and frameworks:

- [Qdrant](https://qdrant.tech/): A high-performance vector database for storing and searching through vector embeddings. The server interacts with Qdrant using the qdrant-client Python library.
  
- [MCP Framework](https://www.anthropic.com/news/model-context-protocol): Provides the structure for implementing the server, including tools, prompts, and resource management. (Replace with the actual URL if applicable.)
  
- [Pydantic](https://docs.pydantic.dev/latest/): Used for data validation and management, especially for defining the schema of resources, tools, and prompts.
  
- [Python Asyncio](https://www.geeksforgeeks.org/asyncio-in-python/): Supports asynchronous operations for efficient server handling and interaction with Qdrant.
  
- [JSON](https://www.w3schools.com/js/js_json_intro.asp): For structuring data and communicating with the server and Qdrant API.

### Prompts
Son supports a qdrant-system prompt, enabling users to manage and analyze Qdrant collections interactively.

- action (required): The action to perform (create, read, delete, or analyze).
- collection_name (required): The name of the collection to manage.
- detail_level (optional): Level of detail for analysis (brief or detailed).

### Tools
Son provides a range of tools to interact with Qdrant's vector collections. Each tool is designed to perform a specific task, as described below:

1. qdrant-write-collection
```bash
Purpose: Create a new Qdrant collection.

- collection_name (string, required): The name of the new collection.
- vector_size (integer, optional): The size of vectors in the collection (default: 384).
- distance (string, optional): The distance metric (Cosine, Euclidean, or Dot; default: Cosine).

```

2. qdrant-read-collection
```bash
Purpose: Description: Retrieve information about a specific Qdrant collection.

- collection_name (string, required): The name of the collection.
```

3. qdrant-delete-collection
```bash
Purpose: Description: Delete an existing Qdrant collection.

- collection_name (string, required): The name of the collection to delete.
```

4. qdrant-list-collections
```bash
Purpose: Description: List all available Qdrant collections.

```

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "Son": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\Users\btuud\Son",
        "run",
        "Son"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "Son": {
      "command": "uvx",
      "args": [
        "Son"
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
npx @modelcontextprotocol/inspector uv --directory C:\Users\btuud\Son run son
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
