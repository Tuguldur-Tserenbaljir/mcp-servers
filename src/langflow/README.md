# langflow MCP server

MCP tools are designed to integrate seamlessly with Langflow, enabling streamlined workflows and enhanced functionality. By leveraging Langflow's capabilities, MCP tools can effectively process and manage tasks in a structured and efficient manner. This integration ensures that the tools work cohesively, providing users with a powerful and reliable solution for their needs.

### Tools

1. list-flows
```bash
Purpose: Retrieve a list of flows from the Langflow API, with optional filtering by name.

Input:
filter_name: (Optional) A string to filter flows by their name.

Output:
A list of flow IDs and names, or a message indicating no flows were found.
```

2. delete-flow
```bash
Purpose: Delete an existing flow from the Langflow API.

Input:
flow_id: The ID of the flow to delete (required).

Output:
A message indicating the flow was successfully deleted.
```

3. create-flow
```bash
Purpose: Create a new flow in the Langflow API.

Input:
name: The name of the flow (required).
description: A description for the flow (optional).

Output:
A message indicating the flow was successfully created.
```

4. upload-saved-component
```bash
Purpose: Upload a JSON file containing saved components to the Langflow API

Input:
json_file_path: The file path to the JSON file (required).

Output:
A message confirming the component was successfully uploaded, along with the upload timestamp and response details.
```

5. add-component-to-flow
```bash
Purpose: Add a component from a JSON file to an existing flow.

Input:
component_path: The file path to the component JSON file (required).
flow_id: The ID of the flow to which the component will be added (required).
x: The x-coordinate for positioning the component (optional, default: 100).
y: The y-coordinate for positioning the component (optional, default: 100).

Output:
A message confirming the component was successfully added, along with the update timestamp and response details.
```

## Configuration

The tool is built on Langflow, so a functioning open-source version of Langflow is required. The Langflow instance on Datastax may need an API or an additional configuration layer to work seamlessly. For this version, I have simply utilized my local Docker container to set it up.

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "langflow": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\Users\btuud\langflow",
        "run",
        "langflow"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "langflow": {
      "command": "uvx",
      "args": [
        "langflow"
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
npx @modelcontextprotocol/inspector uv --directory C:\Users\btuud\langflow run langflow
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
