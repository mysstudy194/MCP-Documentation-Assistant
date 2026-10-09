# MCP Documentation Assistant

An AI-powered documentation assistant built with Python and the Model Context Protocol (MCP). This project integrates an MCP server with Claude Desktop and a custom Python client to search technical documentation, retrieve relevant web content, and generate documentation-grounded answers using an LLM.

## Overview

Finding accurate information in technical documentation can be time-consuming. This project simplifies the process by exposing documentation retrieval as an MCP tool.

The server searches configured documentation sources using the Serper API, fetches relevant web pages, extracts readable text, and returns the content with source URLs.

The project supports two workflows:

* **Claude Desktop integration:** Claude can discover and call the MCP server's documentation retrieval tool.
* **Custom Python client:** A Python MCP client retrieves documentation and passes it to an LLM to generate an answer.

## Features

* **MCP Server:** Implements a documentation retrieval tool using FastMCP.
* **Claude Desktop Integration:** Connects Claude Desktop to the MCP server through standard input/output (stdio).
* **Documentation Search:** Searches relevant pages using the Serper Google Search API.
* **Web Content Retrieval:** Fetches web pages asynchronously using HTTPX.
* **HTML Content Cleaning:** Converts HTML into readable text using a custom utility.
* **LLM Integration:** Generates answers using an LLM configured in the custom client.
* **Source URLs:** Includes source links with retrieved documentation.
* **Environment Configuration:** Loads local environment variables using python-dotenv.
* **Modern Python Tooling:** Uses uv for dependency management and execution.

## Tech Stack

| Technology                   | Purpose                                    |
| ---------------------------- | ------------------------------------------ |
| Python                       | Core programming language                  |
| Model Context Protocol (MCP) | Communication between AI clients and tools |
| FastMCP                      | MCP server implementation                  |
| Claude Desktop               | MCP-enabled AI client                      |
| Serper API                   | Web search                                 |
| HTTPX                        | Asynchronous HTTP requests                 |
| python-dotenv                | Environment variable management            |
| uv                           | Python package and project management      |
| LLM API                      | Documentation-based answer generation      |

## Architecture

```text
                  Claude Desktop
                        |
                        | MCP over stdio
                        v
                 FastMCP Server
                        |
                        v
                  get_docs Tool
                        |
                        v
                  Serper Search
                        |
                        v
                Documentation URLs
                        |
                        v
                 HTTPX Web Fetch
                        |
                        v
                HTML Text Cleaning
                        |
                        v
                Retrieved Documents
                        |
                        v
                  Claude's Answer
```

The custom Python client follows a separate flow:

```text
Python Client
     |
     v
MCP Server
     |
     v
get_docs Tool
     |
     v
Retrieved Documentation
     |
     v
LLM configured in utils.py
     |
     v
Documentation-Grounded Answer
```

## Project Structure

```text
MCP SERVER/
├── mcp_server.py       # MCP server and documentation retrieval tool
├── client.py           # Custom MCP client and LLM integration
├── utils.py            # HTML cleaning and LLM helper functions
├── pyproject.toml      # Project dependencies and configuration
├── uv.lock             # Locked dependency versions
├── .python-version     # Python version configuration
├── .env                # Local environment variables (not committed)
├── .env.example        # Example environment variable names
├── .gitignore          # Files excluded from Git
└── README.md           # Project documentation
```

## How It Works

### 1. MCP Server Initialization

The server is created using FastMCP:

```python
mcp = FastMCP("docs")
```

It runs with the stdio transport, allowing compatible clients to communicate with it through standard input and output.

### 2. Documentation Search

The `get_docs` tool accepts two arguments:

* `query`: The user's documentation question.
* `library`: The configured documentation source.

The server constructs a site-restricted search query and sends it to the Serper API.

### 3. Web Page Retrieval

The server extracts URLs from search results and fetches their content using HTTPX. The `clean_html_to_txt()` utility converts HTML into readable text.

### 4. MCP Tool Response

The server combines the retrieved text with source URLs and returns the documentation to the calling client.

### 5. Answer Generation

In the custom Python client, the retrieved content is passed to an LLM using `get_response_from_llm()` from `utils.py`.

The system prompt instructs the model to answer using only the supplied documentation and preserve source lines.

When Claude Desktop invokes the tool, Claude uses the returned documentation in its own response-generation workflow.

## Available MCP Tool

### `get_docs(query, library)`

Searches configured documentation websites and retrieves relevant page content.

| Argument  | Description                                      |
| --------- | ------------------------------------------------ |
| `query`   | Technical question or documentation search query |
| `library` | Key identifying the documentation source         |

Example:

```python
query = "Publish a package on GitLab using uv"
library = "uv"
```

The tool returns extracted documentation text together with source URLs.

## Configured Documentation Sources

The `docs_urls` dictionary in `mcp_server.py` defines the currently configured sources:

| Library key | Purpose                                |
| ----------- | -------------------------------------- |
| `langchain` | LangChain documentation searches       |
| `openai`    | OpenAI platform documentation searches |
| `uv`        | uv documentation searches              |

The actual URLs in `docs_urls` determine which domains are searched. Ensure each entry points to the intended official documentation domain.

## Installation and Setup

### Prerequisites

* Python version compatible with the project dependencies
* uv package manager
* A Serper API key
* LLM credentials required by `utils.py`
* Claude Desktop, if using Claude integration

### 1. Clone the repository

```bash
git clone https://github.com/mysstudy194/MCP-Documentation-Assistant.git
cd MCP-Documentation-Assistant
```

### 2. Install dependencies

```bash
uv sync
```

This installs the project dependencies defined in `pyproject.toml` and uses the lockfile when applicable.

### 3. Configure environment variables

Create a local `.env` file in the project root:

```env
SERPER_API_KEY=your_serper_api_key
```

Add any additional LLM API credentials required by `utils.py`.

Never commit `.env` or expose API keys in source code.

## Claude Desktop Integration

This project can expose its documentation retrieval functionality to Claude Desktop through MCP.

### 1. Locate the project directory

Find the absolute path to the folder containing `mcp_server.py`.

For example:

```text
C:\Users\YourUsername\Desktop\MCP SERVER\MCP SERVER
```

Use your actual project path.

### 2. Configure Claude Desktop

Open the Claude Desktop MCP configuration file and add the following entry to its existing `mcpServers` object:

```json
{
  "mcpServers": {
    "docs": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\YourUsername\\Desktop\\MCP SERVER\\MCP SERVER",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

Replace `YourUsername` with your Windows username.

If you already have other MCP servers configured, preserve their existing entries instead of replacing the entire configuration.

### 3. Restart Claude Desktop

Restart Claude Desktop after saving the configuration.

Check the available connectors or MCP tools in Claude Desktop and verify that the `docs` server connects successfully and exposes the `get_docs` tool.

### 4. Test the integration

Try a question such as:

```text
Find the official uv documentation explaining how to publish a package on GitLab.
```

When the integration is working, Claude can invoke `get_docs`, retrieve relevant documentation, and use the returned content to formulate an answer.

**Note:** The configuration assumes that `uv` is available in the environment Claude Desktop uses. If it cannot locate `uv`, use its absolute executable path. The server also needs access to its `.env` file and installed dependencies.

## Running the Custom Python Client

The project also includes a standalone MCP client that calls the server and sends the retrieved context to an LLM.

Run:

```bash
uv run client.py
```

The client:

1. Starts `mcp_server.py` through uv.
2. Initializes an MCP session.
3. Lists the tools exposed by the server.
4. Calls `get_docs` with a documentation query.
5. Extracts text from the MCP response.
6. Passes the context to the configured LLM.
7. Prints the generated answer.

The example query is configured in `client.py` and can be changed as needed.

## Error Handling and Limitations

* Search results depend on the Serper API and the configured domains.
* Some pages may block automated requests or require JavaScript rendering.
* HTML extraction quality depends on the implementation of `clean_html_to_txt()`.
* Retrieved documentation may be incomplete or irrelevant to the query.
* The system prompt guides the LLM to use supplied documentation, but it does not guarantee that every generated statement is correct.
* API keys must be configured correctly for search and answer generation.
* The current server returns extracted page content; it does not implement a dedicated vector database or semantic retrieval pipeline.

## Future Improvements

* Add more official documentation sources.
* Improve domain validation and URL filtering.
* Add caching, retries, and rate limiting.
* Improve source-level citations in generated answers.
* Add automated tests and structured logging.
* Add content ranking and better handling of large documents.
* Implement evaluation to measure retrieval quality and answer accuracy.
* Add support for more MCP-compatible AI clients.

## Learning Outcomes

This project demonstrates practical experience with:

* MCP servers and clients
* Tool discovery and tool invocation
* Claude Desktop integration
* Asynchronous HTTP requests
* External search APIs
* Web content extraction
* LLM context construction
* Documentation-grounded question answering
* Python dependency management with uv
