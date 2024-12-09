# notes MCP server
This project provides an extensible MCP (Modular Content Processing) server framework that enables the management of textual content and facilitates interactions with tools for text manipulation, organization, and integration with external services like YouTube. Below is an overview of the server's functionality and its available tools.

# Server Overview
The MCP server is designed to manage content effectively using a set of tools. These tools are modular and follow JSON Schema validation for inputs, ensuring easy integration and extensibility. The core functionality includes creating, modifying, and analyzing textual content and interfacing with third-party APIs for additional insights.

### Prompts

The server provides a single prompt:
- summarize-notes: Creates summaries of all stored notes
  - Optional "style" argument to control detail level (brief/detailed)
  - Generates prompt combining all current notes with style preference

### Tools
1. Add Note
```bash
Purpose: Create a new note with a specified name and content.

Input:

name: Name of the note (string, required).
content: Text content of the note (string, required).
Behavior: The server saves the note and notifies clients of the new resource.
```

2. Randomize Note
```bash
Purpose: Generate a randomized version of an existing note. Also, to test custom server tools. 
Input:

note_name: Name of the note to randomize (string, required).
randomization_type: The type of randomization to apply (string, required).
Options: "shuffle", "reverse", "uppercase", "lowercase".
```

3. Get YouTube Transcript
```bash
Purpose: Fetch the transcript of a YouTube video. Test mcp server to work with python packages/libraries. 

Input:
video_id: YouTube video ID (string, required).
```

## Configuration

Download the necessary libraries and add them to the project ".venv\Lib\site-packages" folder. However, you can now download the new mcp server youtube-transcript online. I think it is good practice to make your own server and work with a python environment and packages. 

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "notes": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\Users\btuud\notes",
        "run",
        "notes"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "notes": {
      "command": "uvx",
      "args": [
        "notes"
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
npx @modelcontextprotocol/inspector uv --directory C:\Users\btuud\notes run notes
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
