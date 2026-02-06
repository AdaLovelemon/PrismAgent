"""
简单测试：验证终端输出格式
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mcp_servers", "code_server"))

from src.terminal import TerminalSessionManager

def main():
    manager = TerminalSessionManager()
    sandbox = os.path.join(os.path.dirname(__file__), "code_sandbox")
    
    print("=== Terminal Output Test ===\n")
    
    # 测试 1
    manager.execute("test", "echo 'Hello World'", cwd=sandbox)
    
    # 测试 2: 使用 Set-Content 写入 UTF8 文件
    manager.execute("test", "'Test 你好' | Set-Content -Encoding UTF8 test.txt", cwd=sandbox)
    
    # 测试 3: 读取 UTF8 文件
    manager.execute("test", "Get-Content test.txt -Encoding UTF8", cwd=sandbox)
    
    # 测试 4
    manager.execute("test", "python -c \"print('Python: 你好世界 Δ √')\"", cwd=sandbox)
    
    # 测试 5
    manager.execute("test", "Get-ChildItem -Name", cwd=sandbox)
    
    # 关闭
    manager.close_session("test")
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    main()
