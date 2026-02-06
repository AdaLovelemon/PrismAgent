# Terminal 使用说明

## 当前实现

终端现在提供最真实的 shell 体验：

```
$ <路径> > <命令>
<输出结果（如果有）>

$ <路径> > <下一个命令>
...
```

- ✅ 没有输出的命令不显示任何东西
- ✅ 只显示实际输出，无多余消息  
- ✅ UTF-8 中文正确显示（输出）

## 重要提示

### 文件写入中文内容

**不要**使用 PowerShell 命令写入包含中文的文件：
```powershell
# ❌ 不推荐 - 会损坏中文
'你好' > file.txt
'你好' | Out-File file.txt
'你好' | Set-Content file.txt
```

**应该**使用 `write_file` MCP 工具：
```python
# ✅ 推荐 - 正确处理 UTF-8
await write_file("file.txt", "你好世界")
```

### PowerShell 适合做什么

✅ **执行** Python 脚本（脚本内容用 write_file 创建）
✅ **读取** 文件内容（Get-Content）
✅ **列出** 目录（Get-ChildItem）
✅ **移动/删除** 文件  
✅ **运行** 其他命令行工具

❌ **不适合**：直接在 PowerShell 命令中写入中文字符串到文件

### 示例工作流

```python
# 1. 用 write_file 创建包含中文的 Python 脚本
await write_file("hello.py", "print('你好世界')")

# 2. 用 terminal 执行
await run_terminal_command("python hello.py")
# 输出:
# $ E:\sandbox > python hello.py
# 你好世界

# 3. 用 terminal 读取
await run_terminal_command("Get-Content hello.py")
# 输出:
# $ E:\sandbox > Get-Content hello.py  
# print('你好世界')
```

## 技术原因

- PowerShell 5.1 的字符串处理在管道和重定向时有编码问题
- 我们使用 Base64 传输命令以避免转义问题
- Base64 编码时，管道字符串会损坏非 ASCII 字符
- 读取和执行输出没有问题，只有写入有问题

## 解决方案

分工合作：
- **write_file** - 创建/修改文件（支持中文）
- **terminal** - 执行/读取/管理（查看结果）
