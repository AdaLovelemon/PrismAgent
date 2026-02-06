"""
测试不用 Base64 传输命令
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mcp_servers", "code_server"))

from src.terminal import TerminalSessionManager

# 直接在真实 PowerShell 中测试
import subprocess

proc = subprocess.Popen(
    ["powershell.exe", "-NoLogo", "-NoProfile"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    encoding='utf-8',
    text=True
)

# 设置 UTF-8
proc.stdin.write("$OutputEncoding = [System.Text.Encoding]::UTF8\r\n")
proc.stdin.write("[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\r\n")  
proc.stdin.write("chcp 65001\r\n")
proc.stdin.flush()

# 测试命令
proc.stdin.write("'Test 你好' | Set-Content -Encoding UTF8 test_direct.txt\r\n")
proc.stdin.write("Get-Content test_direct.txt -Encoding UTF8\r\n")
proc.stdin.write("exit\r\n")
proc.stdin.flush()

output = proc.stdout.read()
print("=== Direct PowerShell Test ===")
print(output)
