import os
import sys
import platform
import argparse
from mcp.server.fastmcp import FastMCP, Context
from src import terminal, files

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="MCP Code Server")
    parser.add_argument("--sandbox-path", required=True, help="Absolute path to the code execution sandbox")
    return parser.parse_args()

args = parse_args()
SANDBOX_PATH = os.path.abspath(args.sandbox_path)

# Initialize MCP server
mcp = FastMCP("code_server")

import src
print(f"DEBUG: src module location: {src.__file__}", file=sys.stderr)
print("DEBUG: Code Server Loaded (with borders)", file=sys.stderr)

# Initialize Terminal Manager
terminal_manager = terminal.TerminalSessionManager()

# --- 1. System Info Tools ---

@mcp.tool()
async def get_system_info() -> str:
    """
    Get detailed information about the current system environment.
    Includes OS type, architecture, sandbox path, Python interpreter path, version, etc.
    This helps verify if the Conda environment is successfully activated or troubleshoot path issues.
    """
    info = {
        "os": platform.system(),
        "release": platform.release(),
        "architecture": platform.machine(),
        "sandbox_path": SANDBOX_PATH,
        "path_separator": os.sep,
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "recommended_shell": "PowerShell" if platform.system() == "Windows" else "Bash"
    }
    return f"System Info: {info}"

# --- 2. File Operation Tools ---

@mcp.tool()
async def write_file(path: str, content: str, ctx: Context = None) -> str:
    """
    Write content to a specified file path.
    Note:
    1. If a relative path is input (not starting with a drive letter or /), it will be automatically relative to the sandbox directory. No need to manually prepend 'sandbox_path/'.
    2. If the file already exists, it will be overwritten.
    """
    # Remove 'sandbox_path/' prefix string that models might incorrectly add
    if path.startswith("sandbox_path/"):
        path = path.replace("sandbox_path/", "", 1)
    
    if not os.path.isabs(path):
        path = os.path.join(SANDBOX_PATH, path)
        
    log_func = ctx.info if ctx else None
    return files.write_file_content(path, content, log_func=log_func)

@mcp.tool()
async def read_file(path: str, ctx: Context = None) -> str:
    """Read content from a specified file path."""
    if not os.path.isabs(path):
        path = os.path.join(SANDBOX_PATH, path)
    log_func = ctx.info if ctx else None
    return files.read_file_content(path, log_func=log_func)

@mcp.tool()
async def list_files(path: str = ".", ctx: Context = None) -> str:
    """List files and folders in a specified directory."""
    if not os.path.isabs(path):
        path = os.path.join(SANDBOX_PATH, path)
    log_func = ctx.info if ctx else None
    return files.list_directory(path, log_func=log_func)

# --- 3. Terminal Execution Tools ---

@mcp.tool()
async def run_terminal_command(command: str, session_id: str = "default", shell_type: str = None, ctx: Context = None) -> str:
    """
    Execute arbitrary commands in a persistent terminal session.
    Important Instructions:
    1. This is a persistent PowerShell (Windows) or Bash process. Environment changes (e.g., cd, conda activate) will persist.
    2. Please send commands directly (e.g., `pip install sklearn`), avoiding `powershell -Command "..."` which starts a subprocess and loses environment state.
    3. For Conda environments, if `conda activate` is unsuccessful, try running Python using the absolute path of the environment.
    4. You can specify the Shell type for a new session (e.g., 'powershell' or 'bash') via `shell_type`. This only takes effect when session_id is first created.
    """
    log_func = ctx.info if ctx else None
    return terminal.execute_shell(terminal_manager, command, session_id, cwd=SANDBOX_PATH, shell_type=shell_type, log_func=log_func)

@mcp.tool()
async def get_terminal_history(session_id: str = "default", lines: int = None) -> str:
    """
    Get the complete history of a terminal session from its log file.
    
    Returns all previous commands and their outputs.
    Useful for reviewing what was executed or checking previous results.
    
    Parameters:
    - session_id: The terminal session ID (default: "default")
    - lines: Optional, number of recent lines to return (None = all history)
    """
    return terminal_manager.get_history(session_id, lines, cwd=SANDBOX_PATH)

@mcp.tool()
async def close_terminal_session(session_id: str = "default") -> str:
    """
    Close a terminal session and clean up resources.
    
    This will terminate the PowerShell/Bash process for the specified session
    and remove it from the session manager. Use this when you're done with
    a terminal session to keep things clean.
    
    The AI terminal window will be closed when this is called.
    
    Parameters:
    - session_id: The terminal session ID to close (default: "default")
    """
    return terminal_manager.close_session(session_id)

if __name__ == "__main__":
    mcp.run(transport="stdio")
