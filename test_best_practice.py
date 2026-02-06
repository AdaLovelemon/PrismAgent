"""
演示正确的使用方式
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mcp_servers", "code_server"))

from src.terminal import TerminalSessionManager

def main():
    manager = TerminalSessionManager()
    sandbox = os.path.join(os.path.dirname(__file__), "code_sandbox")
    
    print("=== 正确的使用方式演示 ===\n")
    
    # 1. 用 Python 的 write 创建包含中文的脚本
    print("[Step 1] 创建包含中文的 Python 脚本...")
    script_path = os.path.join(sandbox, "chinese_test.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write("print('你好世界！Hello World!')\n")
        f.write("print('特殊字符：Δ √ ² ³')\n")
    print(f"已创建: {script_path}\n")
    
    # 2. 用 terminal 执行这个脚本
    print("[Step 2] 执行 Python 脚本...")
    manager.execute("demo", "python chinese_test.py", cwd=sandbox)
    
    # 3. 用 terminal 读取脚本内容
    print("\n[Step 3] 读取脚本内容...")
    manager.execute("demo", "Get-Content chinese_test.py", cwd=sandbox)
    
    # 4. 用 terminal 列出文件
    print("\n[Step 4] 列出目录...")
    manager.execute("demo", "Get-ChildItem chinese*.py", cwd=sandbox)
    
    # 5. 清理
    print("\n[Step 5] 清理...")
    manager.execute("demo", "Remove-Item chinese_test.py", cwd=sandbox)
    
    manager.close_session("demo")
    
    print("\n=== 演示完成 ===")
    print("\n总结:")
    print("  ✅ Python 脚本执行 - 中文显示正确")
    print("  ✅ 文件读取 - 中文显示正确")  
    print("  ✅ 文件操作 - 无输出就不显示")
    print("\n建议:")
    print("  - 用 write_file 创建包含中文的文件")
    print("  - 用 terminal 执行、读取、管理文件")

if __name__ == "__main__":
    main()
