import os
import sys
import os
import platform
import argparse
from mcp.server.fastmcp import FastMCP
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
async def write_file(path: str, content: str) -> str:
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
    return files.write_file_content(path, content)

@mcp.tool()
async def read_file(path: str) -> str:
    """Read content from a specified file path."""
    if not os.path.isabs(path):
        path = os.path.join(SANDBOX_PATH, path)
    return files.read_file_content(path)

@mcp.tool()
async def list_files(path: str = ".") -> str:
    """List files and folders in a specified directory."""
    if not os.path.isabs(path):
        path = os.path.join(SANDBOX_PATH, path)
    return files.list_directory(path)

# --- 3. Terminal Execution Tools ---

@mcp.tool()
async def run_terminal_command(command: str, session_id: str = "default", shell_type: str = None) -> str:
    """
    Execute arbitrary commands in a persistent terminal session.
    Important Instructions:
    1. This is a persistent PowerShell (Windows) or Bash process. Environment changes (e.g., cd, conda activate) will persist.
    2. Please send commands directly (e.g., `pip install sklearn`), avoiding `powershell -Command "..."` which starts a subprocess and loses environment state.
    3. For Conda environments, if `conda activate` is unsuccessful, try running Python using the absolute path of the environment.
    4. You can specify the Shell type for a new session (e.g., 'powershell' or 'bash') via `shell_type`. This only takes effect when session_id is first created.
    """
    return terminal.execute_shell(terminal_manager, command, session_id, cwd=SANDBOX_PATH, shell_type=shell_type)

if __name__ == "__main__":
    mcp.run(transport="stdio")
