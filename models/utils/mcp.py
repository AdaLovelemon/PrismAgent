import json
from typing import Union, List, Dict, Any

from models.utils.frontend import input_user, print_error, print_mcptool, print_security_audit, print_system, print_user, print_user

# 全局变量，记录用户已选择“始终允许”的工具
_ALWAYS_APPROVED_TOOLS = set()

# 需要人工审计的敏感工具列表（来自 code_server）
_SENSITIVE_TOOLS = [
    "run_terminal_command", 
    "write_file"
]



async def human_audit_tool(fn_name: str, fn_args: dict) -> Union[bool, str]:
    """
    针对敏感工具进行人工审计。
    返回:
      True: 允许执行
      False: 拒绝执行
      str: 拒绝执行并提供反馈建议
    """
    global _ALWAYS_APPROVED_TOOLS
    
    if fn_name not in _SENSITIVE_TOOLS:
        return True
    
    if fn_name in _ALWAYS_APPROVED_TOOLS:
        return True

    # Prepare print text
    text_to_print = f"Model is requesting to execute a sensitive tool:\nTool Name: {fn_name}\nArguments: {json.dumps(fn_args, indent=2, ensure_ascii=False)}"
    print_security_audit(text_to_print)
    
    # Prompt user for decision
    while True:
        prompt = "Action: [y]es (approve once) / [a]lways approve / [n]o (reject) / [g]uide (add feedback) / [q]uit (the chat): "
        choice = input_user(prompt).lower().strip()
        if choice == 'y':
            print()
            return True
        elif choice == 'a':
            _ALWAYS_APPROVED_TOOLS.add(fn_name)
            print_user(f"Adding '{fn_name}' to always-approved list.")
            return True
        elif choice == 'n':
            print_user("Action rejected by user.")
            return False
        elif choice == 'g':
            feedback = input_user("Enter your guidance/feedback for the model: ").strip()
            return feedback if feedback else False
        elif choice == 'q':
            print_user("Exiting the chat session.")
            exit(0)
        else:
            print_error("Invalid choice. Please enter 'y', 'a', 'n', 'g', or 'q'.")



def mcp_to_openai_tool(mcp_tool):
    """转换 MCP 工具格式"""
    return {
        "type": "function",
        "function": {
            "name": mcp_tool.name,
            "description": mcp_tool.description,
            "parameters": mcp_tool.inputSchema
        }
    }


async def select_relevant_tools(client, model_name, system_instruction, current_context, mcp_tool_list, n_tools=5):
    """
    第一阶段：工具筛选
    """
    tools_summary = "\n".join([f"- {t.name}: {t.description}" for t in mcp_tool_list])

    prompt_user_zh = f"""请从以下工具列表中挑出解决当前问题所[最必须]的工具(最多选{n_tools}个)。\n当前对话上下文/问题: \n\"\"\"\n{current_context}\n\"\"\"\n工具列表:\n{tools_summary}\n请仅返回工具名称，用逗号分隔，不要有任何其他文字。"""
    prompt_user_en = f"""Please select the [most essential] tools from the following list to solve the current problem (up to {n_tools}). \nCurrent Conversation/Problem: \n\"\"\"\n{current_context}\n\"\"\"\nTool list:\n{tools_summary}\nPlease return only the tool names, separated by commas, without any other text."""
    prompt_user = prompt_user_zh if client.language == "zh" else prompt_user_en

    resp = client.create_completion(
        model_name=model_name,
        message_input=[{"role": "user", "content": prompt_user}],
        prompt_system=system_instruction,
        max_tokens=100,
        completion_name="MCP Tool Selection",
        update_history=False,
        use_history=False,
    )
    
    selected_names = [name.strip() for name in resp.choices[0].message.content.split(",")]
    print_mcptool(f"Model selected tools: {selected_names}", "Tool Selection")
    return [t for t in mcp_tool_list if t.name in selected_names]


