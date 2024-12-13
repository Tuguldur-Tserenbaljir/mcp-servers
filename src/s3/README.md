# s3 MCP server
This MinIO Integration Tool is a powerful Python-based server designed to provide seamless interaction with MinIO object storage systems. Built using the MCP (Multimodal Content Protocol) server framework, this tool offers a comprehensive set of capabilities for managing and manipulating MinIO buckets and objects. It leverages dynamic configuration loading from a user-specific JSON configuration file, enabling flexible and secure connections to MinIO servers. The tool supports a wide range of operations including listing buckets, reading resources, uploading and downloading files, managing bucket contents, and providing intelligent prompts for object and bucket analysis. With built-in error handling, logging, and a robust set of tools, this integration simplifies complex object storage tasks and provides a standardized interface for interacting with MinIO infrastructures.

### Prompts

The tool provides versatile prompts to help users explore and understand their MinIO storage. The prompt here is not as important as the call_tool() or list_tools. Therefore, I leave it to be basic and same as the previous less smarter versionz.

### Tools

## 1) Bucket Management

#### 1.1) List Buckets (list_buckets): Enumerate all available buckets in the MinIO server.
#### 1.2) Create Bucket (make_bucket): Dynamically create new buckets with error handling for existing buckets.
#### 1.3) Remove Bucket (remove_bucket): Safely remove buckets, including automatic deletion of all contained objects.

## 2) Object Exploration

#### 2.1) List Objects (list_objects): Explore bucket contents with support for nested folder structures.
#### 2.2) Read Bucket (read_bucket): Retrieve a detailed list of objects within a specific bucket.

## 3) Storage Analysis

#### 3.1) Calculate Bucket Size (bucket_size): Determine total storage utilization, providing object count and size in bytes and megabytes.

## 4) File Transfer

#### 4.1) Upload File (fput_object):

    - Intelligent file uploading with optional prefix
    - Automatic filename handling
    - Supports custom object naming
    - Provides detailed upload confirmation


#### 5) Download File (fget_object):

    - Flexible download options
    - Can retrieve Specific objects, Entire folder prefixes, Complete bucket contents
    - Maintains original folder structure
    - Generates comprehensive download reports

## Configuration



#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "s3": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\Users\btuud\s3",
        "run",
        "s3"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "s3": {
      "command": "uvx",
      "args": [
        "s3"
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
npx @modelcontextprotocol/inspector uv --directory C:\Users\btuud\s3 run s3
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
