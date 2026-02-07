import json
import os
from typing import Union, List, Dict, Any
import platform
import asyncio

from models.utils.frontend import input_user, print_error, print_mcptool, print_security_audit, print_system, print_terminal, print_user, print_agent, print_warning
from models.utils.mcp import human_audit_tool, mcp_to_openai_tool, select_relevant_tools


async def _process_mcptool_output(result_text, fn_name, fn_args, preview_len=2000, code_sandbox_path=None):
    preview_len = 2000 if fn_name == "run_terminal_command" else 500
    if len(result_text) > preview_len * 2:
        result_text = f"\n\tTool Output: {result_text[:preview_len]}" + f"\n... [{len(result_text) - preview_len * 2} chars omitted] ...\n" + result_text[-preview_len:]

    if fn_name == "run_terminal_command":
        command = fn_args.get("command", "")
        if not code_sandbox_path:
            code_sandbox_path = os.path.join(os.getcwd(), "code_sandbox")
        print_terminal(code_sandbox_path, command, result_text)

    else:
        print_mcptool(result_text, fn_name)


async def _execute_mcp_tool(session, fn_name, fn_args, code_sandbox_path=None):
    # 如果对应的工具会话存在，尝试调用工具并返回结果
    if session:
        try:
            ## 尝试调用工具 
            mcp_result = await session.call_tool(fn_name, fn_args)
            result_text = str(mcp_result.content[0].text)

            ## 打印工具输出给用户（智能截断）
            await _process_mcptool_output(result_text, fn_name, fn_args, code_sandbox_path=code_sandbox_path)

        except Exception as e:
            ## 调用工具出错，打印错误信息并返回错误结果
            result_text = f"Error calling tool {fn_name}: {str(e)}."
            print_error(result_text)
    # 否则返回错误信息
    else:
        result_text = f"Error: No session found for tool {fn_name}."

    return result_text


async def _call_single_tool(tool_call, tool_to_session, skip_remaining_tools=False, code_sandbox_path=None):
    # 解析工具调用信息
    fn_name = tool_call.function.name

    # 如果之前工具有调用错误或用户拒绝，跳过执行并直接返回错误信息
    if skip_remaining_tools:
        tool_result = {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": fn_name,
            "content": "Error: Batch execution cancelled due to previous tool feedback/rejection."
        }
        return tool_result, skip_remaining_tools

    # 主体调用逻辑
    ## 解析工具参数
    try:
        ### 工具参数是 JSON 格式字符串，尝试解析成字典
        fn_args = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as e:
        ### 打印错误信息
        text_error = f"Failed to parse tool arguments for {fn_name}: {e}\n\tRaw Arguments: {tool_call.function.arguments}"
        print_error(text_error)

        ### 返回错误结果
        result_text = f"Error: Invalid JSON arguments for tool {fn_name}: {e}.\nPlease ensure you are sending valid JSON."
        tool_result = {
            "tool_call_id": tool_call.id,
            "role": "tool",
            "name": fn_name,
            "content": result_text
        }
        return tool_result, skip_remaining_tools
    
    ## 安全审计
    audit_result = await human_audit_tool(fn_name, fn_args)
    if audit_result is True:
        ### 打印执行工具信息
        text_mcp = f"Calling MCP tool\n\tArguments: {json.dumps(fn_args, indent=2, ensure_ascii=False)}"
        print_mcptool(text_mcp, fn_name)

        ### 执行工具
        session = tool_to_session.get(fn_name)
        result_text = await _execute_mcp_tool(session, fn_name, fn_args, code_sandbox_path=code_sandbox_path)
    
    ### 如果审计结果是字符串，说明用户提供了指导建议，返回给模型并停止后续工具执行
    elif isinstance(audit_result, str):
        result_text = f"User Feedback/Guidance: {audit_result}. PLEASE STOP CALLING TOOLS IMMEDIATELY AND ACKNOWLEDGE THIS FEEDBACK BEFORE PROCEEDING."
        skip_remaining_tools = True

    ### 否则说明用户拒绝执行，返回错误信息并停止后续工具执行
    else:
        result_text = "Error: Execution rejected by human user for security reasons."
        skip_remaining_tools = True
    
    # 构造工具结果返回给模型
    tool_result = {
        "tool_call_id": tool_call.id,
        "role": "tool",
        "name": fn_name,
        "content": result_text
    }
    return tool_result, skip_remaining_tools


async def _call_tools(tool_calls, tool_to_session, code_sandbox_path=None):
    tool_results, skip_remaining_tools = [], False
    ## 逐个处理工具调用，安全审计，执行，并收集结果 
    for tool_call in tool_calls:
        tool_result, skip_remaining_tools = await _call_single_tool(tool_call, tool_to_session, skip_remaining_tools, code_sandbox_path=code_sandbox_path)
        tool_results.append(tool_result)
        
    return tool_results
    

async def _run_single_turn(
        client,
        model_name,
        system_instruction: Union[str, None] = None,
        user_query: Union[str, None] = None,
        mcp_tool_list: list = [],
        tool_to_session: dict = {},
        code_sandbox_path: str = None
    ):
    # 1. 动态筛选工具 (初始筛选)
    relevant_mcp_tools = await select_relevant_tools(
        client, model_name, 
        system_instruction=system_instruction, 
        current_context=user_query,
        mcp_tool_list=mcp_tool_list
    )
    openai_tools = [mcp_to_openai_tool(t) for t in relevant_mcp_tools]

    # 2. 调用模型
    # BaseClient 会自动处理 history，这里只需传入初始 query
    response = client.create_completion(
        model_name=model_name,
        message_input=[{"role": "user", "content": user_query}],
        prompt_system=system_instruction,
        max_tokens=4096,
        tools=openai_tools,
        tool_choice="auto"
    )
    response_message = response.choices[0].message

    # 3. 打印 AI 的回复（如果存在）
    if response_message.content:
        print_agent(f"{response_message.content}")
    
    turn_count, max_turns = 0, 10  # 限制连续工具调用轮数
    
    while response_message.tool_calls:
        turn_count += 1
        
        # 4. 处理工具调用
        tool_results = await _call_tools(response_message.tool_calls, tool_to_session, code_sandbox_path=code_sandbox_path)

        # 检查是否超出深度限制
        if turn_count >= max_turns:
            prompt = f"\n[!] Tool call chain depth reached {turn_count}. Do you want to continue? [y]es / [n]o (stop) / [g]uide: "
            choice = input_user(prompt).lower().strip()
            
            if choice == "g":
                feedback = input_user("Enter your guidance: ").strip()
                stop_notice = f"User Feedback: {feedback}. Chain limit reached. Please proceed accordingly."
                # 更新工具结果内容，引导模型
                if tool_results:
                    tool_results[-1]["content"] += f"\n\n[System Note] {stop_notice}"
            elif choice != "y":
                print_warning(f"Tool chain execution stopped by user after {turn_count} turns.")
                stop_notice = "Error: Tool chain execution limit reached and user opted to stop. PLEASE STOP CALLING MORE TOOLS AND PROVIDE A FINAL RESPONSE BASED ON CURRENT RESULTS."
                
                # 最后一次反馈结果，关闭工具调用
                response = client.create_completion(
                    model_name=model_name,
                    message_input=tool_results,
                    prompt_system=None,
                    max_tokens=2048,
                    tools=None,
                    tool_choice=None
                )
                response_message = response.choices[0].message
                if response_message.content:
                    print_agent(f"{response_message.content}")
                break

        # 动态重新筛选工具 (使用 use_history=False, 避免 400 错误)
        progress_context = f"Original Query: {user_query}\nRecent progress details: {str(tool_results)[:1000]}"
        relevant_mcp_tools = await select_relevant_tools(
            client, model_name, 
            system_instruction=system_instruction, 
            current_context=progress_context, 
            mcp_tool_list=mcp_tool_list
        )
        openai_tools = [mcp_to_openai_tool(t) for t in relevant_mcp_tools]

        # 5. 将工具结果反馈给模型，让模型基于工具结果生成下一步或最终回复
        # 传入 tool_results 作为 message_input，BaseClient 会将其 append 到包含 tool_calls 的历史中
        response = client.create_completion(
            model_name=model_name,
            message_input=tool_results, 
            prompt_system=None,
            max_tokens=4096,
            tools=openai_tools,
            tool_choice="auto" 
        )
        response_message = response.choices[0].message

        # 6. 打印总结性回复（如果有）
        if response_message.content:
            print_agent(f"{response_message.content}")
    
    return response_message


async def run_agent(
        client,
        model_name,
        system_instruction: Union[str, None] = None,
        user_query: Union[str, None] = None,
        sessions: list = [],
        code_sandbox_path: str = None
    ):
    # 1. 获取所有会话的工具并建立映射
    mcp_tool_list = []
    tool_to_session = {}
    
    for session in sessions:
        tools_resp = await session.list_tools()
        for tool in tools_resp.tools:
            mcp_tool_list.append(tool)
            tool_to_session[tool.name] = session

    # 2. 设置对话环境
    sys_info = f"{platform.system()} ({platform.release()})"
    prompt_zh_tool_part = f"\n当前操作系统: {sys_info}。你可以调用已加载的 MCP 工具来辅助工作。"
    prompt_en_tool_part = f"\nCurrent OS: {sys_info}. You can use the loaded MCP tools to assist your work."
    prompt_system = system_instruction + (prompt_zh_tool_part if client.language == "zh" else prompt_en_tool_part)

    # 3. 处理单轮对话
    if not user_query:
        user_query = input_user("Input your question for the agent: ")

    response_message = await _run_single_turn(
        client, 
        model_name, 
        system_instruction=prompt_system, 
        user_query=user_query, 
        mcp_tool_list=mcp_tool_list,
        tool_to_session=tool_to_session,
        code_sandbox_path=code_sandbox_path
    )

    client.token_tracker.report("Total for this task")

    # 4. 继续对话，直到用户选择退出
    while True:
        user_query = input_user("Input more queries, otherwise press 'q' to quit: ")
        print()
        if user_query == 'q':
            break
        ## 继续处理单轮对话，传入新的用户查询和之前的工具会话
        response_message = await _run_single_turn(
            client, 
            model_name, 
            system_instruction=None,    # 只有第一轮传入系统提示，后续轮次不需要重复传入
            user_query=user_query,
            mcp_tool_list=mcp_tool_list,
            tool_to_session=tool_to_session,
            code_sandbox_path=code_sandbox_path
        )

        client.token_tracker.report("Total for this task")