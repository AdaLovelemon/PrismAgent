import subprocess
import sys
import os
import tempfile
import time
import uuid
import re
import base64
from .audit import audit_command

def _safe_log(msg):
    try:
        print(msg, file=sys.stderr, flush=True)
    except UnicodeEncodeError:
        try:
            encoding = sys.stderr.encoding or 'utf-8'
            encoded = msg.encode(encoding, errors='replace')
            if hasattr(sys.stderr, 'buffer'):
                sys.stderr.buffer.write(encoded + b'\n')
                sys.stderr.buffer.flush()
            else:
                print(encoded.decode(encoding), file=sys.stderr, flush=True)
        except Exception:
            pass

class BaseTerminalSession:
    def __init__(self, cwd=None, shell_command=None, verbose=False, encoding="utf-8"):
        self.id = str(uuid.uuid4())[:8]
        self.log_file = os.path.join(tempfile.gettempdir(), f"mcp_terminal_{self.id}.log")
        self.last_timed_out = False
        self.cwd = cwd
        self.verbose = verbose
        self.encoding = encoding
        self.shell_command = shell_command

        # Determine sandbox path
        if cwd and not os.path.exists(cwd):
            os.makedirs(cwd, exist_ok=True)

        self._init_log_file(shell_command or "Unknown Shell", cwd)

        # 以二进制模式打开日志文件，避免 Python 文本层干扰
        self.log_handle = open(self.log_file, "ab", buffering=0)

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        # 设置 Python 和系统编码环境变量
        env["PYTHONLEGACYWINDOWSSTDIO"] = "0"  # 使用新的 UTF-8 模式
        
        # 确保shell_command已设置
        if not self.shell_command:
            raise ValueError("shell_command must be provided")

        # 使用二进制模式启动进程
        self.proc = subprocess.Popen(
            self.shell_command.split(),
            stdin=subprocess.PIPE,
            stdout=self.log_handle,
            stderr=subprocess.STDOUT,
            text=False,  # 二进制模式
            bufsize=0,   # 无缓冲
            env=env,
            cwd=cwd
        )
        
        self._inject_shell_integration()
        self._start_log_watcher()

    def _init_log_file(self, shell_type, cwd):
        # 初始化日志文件，写入 UTF-8 BOM 和头部信息
        with open(self.log_file, "wb") as f:
            # 写入 BOM 有助某些查看器识别，但这里我们读取时使用 utf-8-sig 兼容
            header = f"--- Meta: Session {self.id} Started ({shell_type}) ---\n"
            if cwd:
                header += f"--- Meta: Working Directory: {cwd} ---\n"
            f.write(header.encode('utf-8'))

    def _inject_shell_integration(self):
        raise NotImplementedError

    def _start_log_watcher(self):
        pass

    def _send_command(self, command, cmd_id, prefix=""):
        raise NotImplementedError

    def execute(self, command: str, timeout: int = 300, log_func=None) -> str:
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
                
                # Log Result with Border
                if log_func:
                    border = "=" * 60
                    msg = f"{border}\n$ {self.cwd} > {command}\n"
                    if result and result.strip():
                        msg += f"{'-' * 60}\n{result}\n"
                    msg += f"{border}\n"
                    log_func(msg)
                else:
                    # Fallback to stderr
                    border = "=" * 60
                    _safe_log(border)
                    _safe_log(f"$ {self.cwd} > {command}")
                    
                    if result and result.strip():
                        _safe_log("-" * 60)
                        _safe_log(result)
                        
                    _safe_log(border)
                    _safe_log("")

                return result
            
        self.last_timed_out = False
        timeout_result = self._handle_timeout(start_pos, timeout)
        
        # Log Timeout with Border
        if log_func:
            border = "=" * 60
            msg = f"{border}\n$ {self.cwd} > {command}\n"
            if timeout_result and timeout_result.strip():
                msg += f"{'-' * 60}\n{timeout_result}\n"
            msg += f"{border}\n"
            log_func(msg)
        else:
            border = "=" * 60
            _safe_log(border)
            _safe_log(f"$ {self.cwd} > {command}")
            
            if timeout_result and timeout_result.strip():
                _safe_log("-" * 60)
                _safe_log(timeout_result)
                
            _safe_log(border)
            _safe_log("")

        return timeout_result

    def _check_log_for_completion(self, start_pos, start_marker_pattern):
        if not os.path.exists(self.log_file):
            return None

        content = ""
        try:
            with open(self.log_file, "rb") as f:
                f.seek(start_pos)
                raw = f.read()
                # 使用 utf-8-sig 以处理 PowerShell 可能输出的 BOM
                read_encoding = "utf-8-sig" if self.encoding == "utf-8" else self.encoding
                content = raw.decode(read_encoding, errors='replace')
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
    def __init__(self, cwd=None, shell_command=None, verbose=False):
        cmd = shell_command or "powershell.exe -NoLogo -ExecutionPolicy Bypass -NoProfile"
        # 统一使用 UTF-8 编码
        super().__init__(cwd=cwd, shell_command=cmd, verbose=verbose, encoding="utf-8")
        
        # 不再启动 GUI 窗口，改用终端内分屏
        # 分屏视图由外部管理

    def _inject_shell_integration(self):
        """注入标记函数并设置 UTF-8 编码"""
        init_cmd = (
            # 1. 基础编码设置
            "$env:PYTHONIOENCODING='utf-8'; "
            "$OutputEncoding = [System.Text.Encoding]::UTF8; "
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            "[Console]::InputEncoding = [System.Text.Encoding]::UTF8; "
            "chcp 65001 | Out-Null; "

            # 2. 强制重置底层 Console 流 (解决 PowerShell 5.1 管道编码问题的核心方案)
            # 使用无 BOM 的 UTF-8 编码器，并使用 StreamWriter 替换 Console.Out
            # 增加 try-catch 以增强健壮性
            "try { "
            "  $utf8NoBom = New-Object System.Text.UTF8Encoding $false; "
            "  $stream = [System.Console]::OpenStandardOutput(); "
            "  $writer = New-Object System.IO.StreamWriter $stream, $utf8NoBom; "
            "  $writer.AutoFlush = $true; "
            "  [System.Console]::SetOut($writer); "
            "  $err_stream = [System.Console]::OpenStandardError(); "
            "  $err_writer = New-Object System.IO.StreamWriter $err_stream, $utf8NoBom; "
            "  $err_writer.AutoFlush = $true; "
            "  [System.Console]::SetError($err_writer); "
            "} catch { Write-Warning 'Stream reset failed: $_' }; "

            # 3. 设置文件操作默认参数
            "$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'; "
            "$PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'; "
            "$PSDefaultParameterValues['Get-Content:Encoding'] = 'utf8'; "
            "$PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'; "

            # 4. 兼容性修复：重写 Write-Host 以使用可靠的 Console.WriteLine
            # PowerShell 5.1 在管道重定向时 Write-Host 依然由宿主渲染，往往忽略 Console.Out 设置
            # 我们将其重定向到底层 .NET 流以确保 UTF-8 正确传输
            "function global:Write-Host { "
            "    param([Parameter(ValueFromPipeline)]$Object, [switch]$NoNewline, [System.ConsoleColor]$ForegroundColor, [System.ConsoleColor]$BackgroundColor) "
            "    $str = if ($Object -eq $null) { '' } else { $Object.ToString() }; "
            "    if ($NoNewline) { [Console]::Write($str) } else { [Console]::WriteLine($str) } "
            "}; "

            # 5. 兼容性修复：重写 Out-Default 以修复管道输出（如 ls, dir, Get-Content）的显示乱码
            # 将所有标准管道输出强制通过 Out-String 格式化后，写入我们接管的 UTF-8 Console.Out流
            "function global:Out-Default { "
            "    param([Parameter(ValueFromPipeline=$true)] $InputObject) "
            "    process { "
            "        if ($InputObject -eq $null) { return } "
            "        $InputObject | Out-String -Stream -Width 120 | ForEach-Object { "
            "            [System.Console]::WriteLine($_) "
            "        } "
            "    } "
            "}; "

            # 6. 定义标记函数
            "function global:Write-McpMarker($type, $pay) { "
            "  [Console]::Out.WriteLine(\"$([char]27)]633;P;Mcp${type}=$pay$([char]7)\"); "
            "}; \r\n"
        )
        self.proc.stdin.write(init_cmd.encode('utf-8'))
        self.proc.stdin.flush()


    def _send_command(self, command, cmd_id, prefix=""):
        """发送命令到 PowerShell，使用 Base64 编码避免转义问题"""
        if prefix:
            self.proc.stdin.write(prefix.encode('utf-8'))
            self.proc.stdin.flush()
        
        # 使用 Base64 编码传递命令，避免特殊字符问题
        cmd_bytes = command.encode('utf-8')
        cmd_base64 = base64.b64encode(cmd_bytes).decode('ascii')
        
        # 注入标记包装命令 - 确保每次执行前设置正确的编码环境
        wrapper_command = (
            # 强制设置控制台和输出编码为UTF-8，防止被之前的命令（如系统命令）修改
            f"$OutputEncoding = [System.Text.Encoding]::UTF8; "
            f"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            f"[Console]::InputEncoding = [System.Text.Encoding]::UTF8; "
            f"Write-McpMarker 'Start' '{cmd_id}'; "
            f"$env:PYTHONIOENCODING='utf-8'; "
            # 执行命令（直接输出到流，不进行Base64缓冲，保留实时输出能力）
            f"iex ([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('{cmd_base64}'))); "
            f"$exit_code=$LASTEXITCODE; "
            f"Write-McpMarker 'End' $exit_code\r\n"
        )
        
        self.proc.stdin.write(wrapper_command.encode('utf-8'))
        self.proc.stdin.flush()



class BashSession(BaseTerminalSession):
    def __init__(self, cwd=None, shell_command=None, verbose=False):
        cmd = shell_command or "bash"
        super().__init__(cwd=cwd, shell_command=cmd, verbose=verbose, encoding="utf-8")

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

    def get_or_create_session(self, session_id: str, shell_type: str = None, cwd: str = None, verbose: bool = False) -> BaseTerminalSession:
        if session_id not in self._sessions:
            if shell_type:
                is_powershell = "powershell" in shell_type.lower() or "pwsh" in shell_type.lower()
                if is_powershell:
                    self._sessions[session_id] = PowerShellSession(cwd, shell_command=shell_type, verbose=verbose)
                else:
                    self._sessions[session_id] = BashSession(cwd, shell_command=shell_type, verbose=verbose)
            else:
                # Auto-detect
                if os.name == "nt":
                    self._sessions[session_id] = PowerShellSession(cwd, verbose=verbose)
                else:
                    self._sessions[session_id] = BashSession(cwd, verbose=verbose)
        return self._sessions[session_id]

    def execute(self, session_id: str, command: str, timeout: int = 60, shell_type: str = None, cwd: str = None, verbose: bool = False, log_func=None) -> str:
        session = self.get_or_create_session(session_id, shell_type, cwd, verbose=verbose)
        return session.execute(command, timeout, log_func=log_func)
    
    def get_history(self, session_id: str, lines: int = None, shell_type: str = None, cwd: str = None, verbose: bool = False) -> str:
        """Get terminal history from log file"""
        session = self.get_or_create_session(session_id, shell_type, cwd, verbose=verbose)
        
        if not os.path.exists(session.log_file):
            return "No history available yet."
        
        try:
            with open(session.log_file, "r", encoding=session.encoding, errors="replace") as f:
                if lines:
                    all_lines = f.readlines()
                    return "".join(all_lines[-lines:])
                return f.read()
        except Exception as e:
            return f"Error reading history: {str(e)}"
    
    def close_session(self, session_id: str) -> str:
        """关闭指定的终端会话"""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            
            # 关闭进程
            if hasattr(session, 'proc') and session.proc:
                session.proc.terminate()
                session.proc.wait(timeout=5)
            
            # 关闭日志文件
            if hasattr(session, 'log_handle') and session.log_handle:
                session.log_handle.close()
            
            # 从会话列表中删除
            del self._sessions[session_id]
            
            return f"Session {session_id} closed."
        else:
            return f"Session {session_id} not found."

def execute_shell(manager: TerminalSessionManager, command: str, session_id: str = "default", timeout: int = 60, cwd: str = None, shell_type: str = None, verbose: bool = False, log_func=None) -> str:
    """Execute a terminal command and return the output."""
    # Safety audit
    is_safe, message = audit_command(command)
    if not is_safe:
        return message

    try:
        return manager.execute(session_id, command, timeout, shell_type, cwd, verbose=verbose, log_func=log_func)
    except Exception as e:
        return f"Error executing terminal command in session {session_id}: {str(e)}"
