import json
from typing import Union, List, Dict, Any

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

    print(f"\n" + "!"*60)
    print(f"[SECURITY AUDIT] Model is requesting to execute a sensitive tool:")
    print(f"Tool Name: {fn_name}")
    print(f"Arguments: {json.dumps(fn_args, indent=2, ensure_ascii=False)}")
    print("!"*60)

    while True:
        prompt = "\nAction: [y]es (approve once) / [a]lways approve / [n]o (reject) / [g]uide (add feedback): "
        choice = input(prompt).lower().strip()
        if choice == 'y':
            return True
        elif choice == 'a':
            _ALWAYS_APPROVED_TOOLS.add(fn_name)
            print(f"Adding '{fn_name}' to always-approved list.")
            return True
        elif choice == 'n':
            print("Action rejected by user.")
            return False
        elif choice == 'g':
            feedback = input("Enter your guidance/feedback for the model: ").strip()
            return feedback if feedback else False

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

async def select_relevant_tools(client, model_name, system_instruction, user_query, mcp_tool_list):
    """
    第一阶段：工具筛选
    """
    tools_summary = "\n".join([f"- {t.name}: {t.description}" for t in mcp_tool_list])

    prompt_user_zh = f"""请从以下工具列表中挑出解决用户问题所[最必须]的工具(最多选5个)。\n用户问题: "{user_query}"\n工具列表:\n{tools_summary}\n请仅返回工具名称，用逗号分隔，不要有任何其他文字。"""
    prompt_user_en = f"""Please select the [most essential] tools from the following list to solve the user's problem (up to 5). \nUser's question: "{user_query}"\nTool list:\n{tools_summary}\nPlease return only the tool names, separated by commas, without any other text."""
    prompt_user = prompt_user_zh if client.language == "zh" else prompt_user_en

    resp = client.create_completion(
        model_name=model_name,
        message_input=[{"role": "user", "content": prompt_user}],
        prompt_system=system_instruction,
        max_tokens=100,
        completion_name="MCP Tool Selection",
        update_history=False,
    )
    
    selected_names = [name.strip() for name in resp.choices[0].message.content.split(",")]
    return [t for t in mcp_tool_list if t.name in selected_names]

async def run_mcp_agent(client, model_name, system_instruction, user_query, sessions: list):
    """
    包装 MCP 工具交互循环，支持多个会话。
    包含：工具获取、筛选、转换、以及与模型的 Tool-Call 迭代逻辑。
    """
    # 1. 获取所有会话的工具并建立映射
    mcp_tool_list = []
    tool_to_session = {}
    
    for session in sessions:
        tools_resp = await session.list_tools()
        for tool in tools_resp.tools:
            mcp_tool_list.append(tool)
            tool_to_session[tool.name] = session
    
    # 2. 筛选相关工具
    relevant_mcp_tools = await select_relevant_tools(client, model_name, system_instruction, user_query, mcp_tool_list)
    openai_tools = [mcp_to_openai_tool(t) for t in relevant_mcp_tools]

    # 3. 设置对话环境
    import platform
    sys_info = f"{platform.system()} ({platform.release()})"
    prompt_zh_tool_part = f"\n当前操作系统: {sys_info}。你可以调用已加载的 MCP 工具来辅助工作。"
    prompt_en_tool_part = f"\nCurrent OS: {sys_info}. You can use the loaded MCP tools to assist your work."
    prompt_system = system_instruction + (prompt_zh_tool_part if client.language == "zh" else prompt_en_tool_part)

    # 4. 初始对话
    response = client.create_completion(
        model_name=model_name,
        message_input=[{"role": "user", "content": user_query}],
        prompt_system=prompt_system,
        max_tokens=4096,
        tools=openai_tools,
        tool_choice="auto"
    )
    response_message = response.choices[0].message

    # 5. 交互循环
    while response_message.tool_calls:
        tool_results = []
        skip_remaining_tools = False
        
        for tool_call in response_message.tool_calls:
            fn_name = tool_call.function.name
            
            if skip_remaining_tools:
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": fn_name,
                    "content": "Error: Batch execution cancelled due to previous tool feedback/rejection."
                })
                continue

            try:
                fn_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                # ... (rest of parsing error logic)
                print(f"   [Error] Failed to parse tool arguments for {fn_name}: {e}")
                print(f"   [Raw Arguments]: {tool_call.function.arguments}")
                result_text = f"Error: Invalid JSON arguments for tool {fn_name}. Please ensure you are sending valid JSON."
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": fn_name,
                    "content": result_text
                })
                continue
            
            # 安全审计
            audit_result = await human_audit_tool(fn_name, fn_args)
            
            if audit_result is True:
                print(f"   [MCP] Now Calling: {fn_name}...")
                session = tool_to_session.get(fn_name)
                if session:
                    try:
                        mcp_result = await session.call_tool(fn_name, fn_args)
                        result_text = str(mcp_result.content[0].text)
                        
                        # 如果是 run_terminal_command，打印详细执行信息
                        if fn_name == "run_terminal_command":
                            command = fn_args.get("command", "")
                            session_id = fn_args.get("session_id", "default")
                            print(f"\n$ [session:{session_id}] > {command}")
                            if result_text and not result_text.startswith("Error"):
                                print(result_text)
                            print()
                    except Exception as e:
                        result_text = f"Error calling tool {fn_name}: {str(e)}"
                else:
                    result_text = f"Error: No session found for tool {fn_name}"
            elif isinstance(audit_result, str):
                # 用户提供了指导建议
                result_text = f"User Feedback/Guidance: {audit_result}. PLEASE STOP CALLING TOOLS IMMEDIATELY AND ACKNOWLEDGE THIS FEEDBACK BEFORE PROCEEDING."
                skip_remaining_tools = True # 停止处理后续工具，让模型先回应指导
            else:
                result_text = "Error: Execution rejected by human user for security reasons."
                skip_remaining_tools = True
            
            tool_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": fn_name,
                "content": result_text
            })
            
        # 反馈结果
        response = client.create_completion(
            model_name=model_name,
            message_input=tool_results,
            prompt_system=None, 
            max_tokens=4096,
            tools=openai_tools,
            tool_choice="auto"
        )
        response_message = response.choices[0].message

    return response_message
