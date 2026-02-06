import subprocess
import os
import tempfile
import time
import uuid
import re
import base64
from .audit import audit_command

class BaseTerminalSession:
    def __init__(self, cwd=None, shell_command=None, encoding='utf-8'):
        self.id = str(uuid.uuid4())[:8]
        self.log_file = os.path.join(tempfile.gettempdir(), f"mcp_terminal_{self.id}.log")
        self.last_timed_out = False
        self.cwd = cwd
        self.encoding = encoding
        self.shell_command = shell_command

        # Determine sandbox path
        if cwd and not os.path.exists(cwd):
            os.makedirs(cwd, exist_ok=True)

        self._init_log_file(shell_command or "Unknown Shell", cwd)

        # Start the shell process
        # Use simple 'ab' mode and buffering=0 for direct binary writes
        self.log_handle = open(self.log_file, "ab", buffering=0)
        
        # Use shell_command if provided, otherwise fail early (subclasses should provide it)
        if not self.shell_command:
            raise ValueError("shell_command must be provided")

        self.proc = subprocess.Popen(
            self.shell_command.split(),
            stdin=subprocess.PIPE,
            stdout=self.log_handle,
            stderr=subprocess.STDOUT,
            encoding='utf-8', 
            bufsize=1,
            env=os.environ,
            cwd=cwd
        )
        
        self._inject_shell_integration()
        self._start_log_watcher()

    def _init_log_file(self, shell_type, cwd):
        with open(self.log_file, "w", encoding=self.encoding, errors="replace") as f:
            f.write(f"--- Terminal Session {self.id} Started ({shell_type}) ---\n")
            if cwd:
                f.write(f"--- Working Directory: {cwd} ---\n")

    def _inject_shell_integration(self):
        raise NotImplementedError

    def _start_log_watcher(self):
        pass

    def _send_command(self, command, cmd_id, prefix=""):
        raise NotImplementedError

    def execute(self, command: str, timeout: int = 300) -> str:
        if self.proc.poll() is not None:
            return "Error: Terminal process has exited."

        cmd_id = str(uuid.uuid4())[:8]
        start_marker_pattern = f"\x1b]633;P;McpStart={cmd_id}\x07"
        
        prefix = "\x03" if self.last_timed_out else ""
        
        self._send_command(command, cmd_id, prefix)
        
        start_pos = os.path.getsize(self.log_file)
        self.proc.stdin.flush()
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self._check_log_for_completion(start_pos, start_marker_pattern)
            if result is not None:
                self.last_timed_out = False
                return result
            # Using 0.2s pause for balance between responsiveness and CPU
            time.sleep(0.2)
            
        self.last_timed_out = True
        return self._handle_timeout(start_pos, timeout)

    def _check_log_for_completion(self, start_pos, start_marker_pattern):
        if not os.path.exists(self.log_file):
            return None

        content = ""
        try:
            with open(self.log_file, "rb") as f:
                f.seek(start_pos)
                raw = f.read()
                content = raw.decode(self.encoding, errors='replace')
        except Exception:
            return None

        if start_marker_pattern not in content:
            return None

        parts = content.split(start_marker_pattern, 1)
        if len(parts) < 2:
            return None
        
        post_start_content = parts[1]
        
        # Look for end marker
        match = re.search(r'\x1b]633;P;McpEnd=(-?\d+)(?:\x07|\s|\r|\n|$)', post_start_content)
        if match:
            raw_command_output = post_start_content[:match.start()]
            exit_code = match.group(1)
            return self._clean_output(raw_command_output, exit_code)
        
        return None

    def _clean_output(self, raw_output, exit_code):
        clean = re.sub(r'\x1b\[[0-9;]*m', '', raw_output)
        clean = re.sub(r'\x1b].*?\x07', '', clean)
        clean = clean.strip()
        
        if exit_code != "0":
            return f"[Exit Code: {exit_code}] {clean}"
        return clean if clean else "Command executed successfully (no output)."

    def _handle_timeout(self, start_pos, timeout):
        try:
            with open(self.log_file, "rb") as f:
                f.seek(start_pos)
                raw_data = f.read()
                partial = raw_data.decode(self.encoding, errors="replace")
                partial = re.sub(r'\x1b\[[0-9;]*m', '', partial)
        except Exception:
            partial = "(read failed)"
            
        return f"Error: Command timed out after {timeout} seconds. Sent ^C.\nPartial logs:\n{partial}"

    def __del__(self):
        if hasattr(self, "proc") and self.proc:
            self.proc.terminate()
        if hasattr(self, "log_handle") and self.log_handle:
            self.log_handle.close()

class PowerShellSession(BaseTerminalSession):
    def __init__(self, cwd=None, shell_command=None):
        cmd = shell_command or "powershell.exe -ExecutionPolicy Bypass -NoProfile"
        super().__init__(cwd, shell_command=cmd, encoding="gbk")

    def _inject_shell_integration(self):
        init_cmd = (
            "$OutputEncoding = [System.Text.Encoding]::UTF8; "
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            "[Console]::InputEncoding = [System.Text.Encoding]::UTF8; "
            "chcp 65001; "
            "function global:Write-McpMarker($type, $pay) { "
            "  [Console]::Out.Write(\"$([char]27)]633;P;Mcp${type}=$pay$([char]7)\"); "
            "}; "
            "$function:Prompt = { "
            "  $code = $LASTEXITCODE; "
            "  Write-McpMarker 'End' $code; "
            "  return \"PS $($ExecutionContext.SessionState.Path.CurrentLocation) > \" "
            "}; "
            "Clear-Host\r\n"
        )
        self.proc.stdin.write(init_cmd)
        self.proc.stdin.flush()

    def _start_log_watcher(self):
        if os.name == "nt":
            title = f"MCP_Terminal_{self.id}"
            watch_cmd = f"powershell -NoExit -Command \"Write-Host 'Watching terminal session {self.id}...'; Get-Content -Path '{self.log_file}' -Wait\""
            subprocess.Popen(f"start \"{title}\" cmd /c \"{watch_cmd}\"", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _send_command(self, command, cmd_id, prefix=""):
        full_command_str = f"{prefix}Write-McpMarker 'Start' '{cmd_id}'; {command}"
        b64_cmd = base64.b64encode(full_command_str.encode('utf-8')).decode('ascii')
        wrapper_cmd = f"iex ([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('{b64_cmd}')))\r\n"
        self.proc.stdin.write(wrapper_cmd)


class BashSession(BaseTerminalSession):
    def __init__(self, cwd=None, shell_command=None):
        cmd = shell_command or "bash"
        super().__init__(cwd, shell_command=cmd, encoding="utf-8")

    def _inject_shell_integration(self):
        init_cmd = (
            "export LANG=en_US.UTF-8; "
            "write_mcp_marker() { printf \"\\033]633;P;Mcp$1=$2\\007\"; }; "
            "export PROMPT_COMMAND='code=$?; write_mcp_marker End $code'; "
            "export PS1='> '; "
            "clear\n"
        )
        self.proc.stdin.write(init_cmd)
        self.proc.stdin.flush()
        
    def _send_command(self, command, cmd_id, prefix=""):
        full_command = f"{prefix}write_mcp_marker Start {cmd_id}; {command}\n"
        self.proc.stdin.write(full_command)
        
class TerminalSessionManager:
    """Manages multiple terminal sessions."""
    def __init__(self):
        self._sessions = {}

    def get_or_create_session(self, session_id: str, shell_type: str = None, cwd: str = None) -> BaseTerminalSession:
        if session_id not in self._sessions:
            if shell_type:
                is_powershell = "powershell" in shell_type.lower() or "pwsh" in shell_type.lower()
                if is_powershell:
                    self._sessions[session_id] = PowerShellSession(cwd, shell_command=shell_type)
                else:
                    self._sessions[session_id] = BashSession(cwd, shell_command=shell_type)
            else:
                # Auto-detect
                if os.name == "nt":
                    self._sessions[session_id] = PowerShellSession(cwd)
                else:
                    self._sessions[session_id] = BashSession(cwd)
        return self._sessions[session_id]

    def execute(self, session_id: str, command: str, timeout: int = 60, shell_type: str = None, cwd: str = None) -> str:
        session = self.get_or_create_session(session_id, shell_type, cwd)
        return session.execute(command, timeout)

def execute_shell(manager: TerminalSessionManager, command: str, session_id: str = "default", timeout: int = 60, cwd: str = None, shell_type: str = None) -> str:
    """Execute a terminal command and return the output."""
    # Safety audit
    is_safe, message = audit_command(command)
    if not is_safe:
        return message

    try:
        return manager.execute(session_id, command, timeout, shell_type, cwd)
    except Exception as e:
        return f"Error executing terminal command in session {session_id}: {str(e)}"
