import asyncio
import json
import os
import argparse
import sys
import logging

from models import deepseek, qwen
from models.utils.mcp_utils import run_mcp_agent


from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client



from contextlib import AsyncExitStack

async def chat_with_agent(prompt_system, user_input, client, model_name, server_params_list):
    async with AsyncExitStack() as stack:
        sessions = []
        for i, params in enumerate(server_params_list):
            server_name = os.path.basename(os.path.dirname(params.args[0]))
            print(f"[*] Initializing MCP server {i+1}/{len(server_params_list)}: {server_name}...")
            # 开启每个服务器的连接
            read, write = await stack.enter_async_context(stdio_client(params))
            # 为每个连接创建会话
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            sessions.append(session)
            print(f"[+] Server {i+1} initialized.")

        print(f"\n>> System Prompt: {prompt_system}")
        print(f"\n>> Question: {user_input}")

        # 将所有会话传递给代理函数
        final_response = await run_mcp_agent(client, model_name, prompt_system, user_input, sessions)
        # 打印最终答案
        print(f">> Answer: {final_response.content if final_response.content else 'Task completed'}")

        # 打印生成的报告
        print("-" * 30)
        client.token_tracker.report("Total for this task")
        print("-" * 30)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='deepseek', help='Choose the model to use')
    parser.add_argument('--model_name', type=str, default='deepseek-chat', help='Model name for the selected model')
    parser.add_argument('--question', type=str, required=True, help='The question to ask the agent')
    parser.add_argument('--prompt_system', type=str, 
                        default='你是一个强大的智能助手，擅长通过调用外部工具解决复杂问题。',
                        help='System prompt for the agent')
    parser.add_argument('--language', type=str, default='zh', help='Language preference for the agent')
    parser.add_argument('--load_chat_history_path', type=str, default=None, help='Path to load previous chat history from')
    parser.add_argument('--mcp_servers', type=str, nargs='+', default=['math', 'web', 'code'], 
                        help='Choose which MCP servers to load (any of: math, web, code)')
    args = parser.parse_args()

    # Get the absolute path of the current script directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Configure logging to capture MCP notifications
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )
    # Suppress httpx request logging
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Instantiate the client based on the selected model
    print(f"[*] Initializing {args.model} client...")
    client = eval(args.model).Client(language=args.language, message_history=args.load_chat_history_path)

    # 定义所有需要加载的 MCP 服务器
    math_path = os.path.join(base_dir, "mcp_servers", "math_server")
    web_path = os.path.join(base_dir, "mcp_servers", "web_server")
    code_path = os.path.join(base_dir, "mcp_servers", "code_server")

    # 为每个服务器准备环境变量，确保它们能找到自己的 src 目录
    math_env = os.environ.copy()
    math_env["PYTHONPATH"] = math_path + os.pathsep + math_env.get("PYTHONPATH", "")
    
    web_env = os.environ.copy()
    web_env["PYTHONPATH"] = web_path + os.pathsep + web_env.get("PYTHONPATH", "")

    code_env = os.environ.copy()
    code_env["PYTHONPATH"] = code_path + os.pathsep + code_env.get("PYTHONPATH", "")

    math_server_params = StdioServerParameters(
        command=sys.executable,
        args=[os.path.join(math_path, "server.py")],
        env=math_env
    )

    web_server_params = StdioServerParameters(
        command=sys.executable,
        args=[os.path.join(web_path, "server.py")],
        env=web_env
    )

    # Prepare the sandbox path for code_server
    code_sandbox_path = os.path.join(base_dir, "code_sandbox")
    if not os.path.exists(code_sandbox_path):
        os.makedirs(code_sandbox_path, exist_ok=True)

    code_server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            os.path.join(code_path, "server.py"),
            "--sandbox-path", code_sandbox_path
        ],
        env=code_env
    )
    
    # 待加载的服务器列表
    server_list = []
    
    if 'math' in args.mcp_servers:
        server_list.append(math_server_params)
    if 'web' in args.mcp_servers:
        server_list.append(web_server_params)
    if 'code' in args.mcp_servers:
        server_list.append(code_server_params)

    if not server_list:
        print("[!] Warning: No MCP servers selected. The agent will have no external tools.")

    print(f"[*] Starting agent with question: {args.question}")

    # 执行对话
    try:
        asyncio.run(
                chat_with_agent(
                    args.prompt_system,
                    args.question,
                    client, 
                    args.model_name, 
                    server_list
                )
            )
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")
    except Exception as e:
        print(f"\n[!] An error occurred during execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

