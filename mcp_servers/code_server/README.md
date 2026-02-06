# Code Server (MCP)

This is a Model Context Protocol (MCP) server that provides tools for code execution and file management within a secure sandbox environment.

## Features

- **Persistent Terminal Sessions**: Execute commands in a long-running PowerShell (Windows) or Bash (Unix) process. Environment changes (like `cd` or `conda activate`) persist across tool calls.
- **File Management**: Create, read, and list files within a designated sandbox directory.
- **Security Auditing**: Built-in auditing for terminal commands, Python code, and file path access to prevent malicious operations.
- **Cross-Platform Support**: Optimized for both Windows and Linux environments.

## Installation

Ensure you have Python 3.9+ installed.

```bash
pip install mcp
```

## Usage

The server requires an absolute path to a sandbox directory where all file operations and command executions will take place.

### Running Manually

```bash
python server.py --sandbox-path /path/to/your/sandbox
```

### Configuration in MCP Clients

To use this server with a client (like Claude Desktop or a custom Agent), configure it to run with the following parameters:

- **Command**: `python`
- **Arguments**: `["/path/to/code_server/server.py", "--sandbox-path", "/path/to/sandbox"]`

## Available Tools

- `get_system_info`: Get OS type, architecture, and sandbox details.
- `write_file`: Write content to a file (relative to sandbox).
- `read_file`: Read content from a file (relative to sandbox).
- `list_files`: List directory contents.
- `run_terminal_command`: Execute a command in a persistent terminal session. Supports custom `session_id` and `shell_type` (powershell/bash).

## Security Note

This server includes an `audit` module that checks for dangerous patterns such as `rm -rf`, system directory access (e.g., `/etc`, `C:\Windows`), and sensitive Python operations. Always run the server with the minimum necessary permissions.
