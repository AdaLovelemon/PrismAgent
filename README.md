# PrismAgent

PrismAgent is a highly sophisticated, multi-model AI agent framework built on the **Model Context Protocol (MCP)**. Like a prism that decomposes light into its constituent colors, PrismAgent decomposes complex user requests into specialized tasks, leveraging a suite of dedicated MCP servers to provide precise answers and execute actions.

## 🌟 Key Features

- **Multi-Model Support**: Seamlessly switch between state-of-the-art models like **DeepSeek** and **Qwen**.
- **MCP Native**: Fully utilizes the Model Context Protocol for tool discovery and invocation.
- **Specialized Toolkits**:
  - 🔢 **Math Server**: Advanced symbolic mathematics using SymPy (Calculus, Algebra, Statistics).
  - 🌐 **Web Server**: Comprehensive search capabilities (Text, Lens, Scholar, News) via Serper.dev and webpage content fetching.
  - 💻 **Code Server**: Secure, persistent terminal sessions and sandboxed file management.
- **Extensible Architecture**: Easily add new MCP servers to expand the agent's capabilities.
- **Token Tracking**: Built-in monitoring for API usage and costs.

## 🏗 Project Structure

```text
PrismAgent/
├── main.py              # Main entry point for the agent
├── models/              # Model handlers (DeepSeek, Qwen, etc.)
├── mcp_servers/         # Specialized MCP tool servers
│   ├── math_server/     # Symbolic math and computation
│   ├── web_server/      # Web search and scraping
│   └── code_server/     # Terminal and file sandbox
└── config/              # Configuration and memory logs
```

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- [Serper.dev](https://serper.dev/) API Key (for web search)
- DeepSeek or Qwen API credentials

### Installation

1. Clone the repository and navigate to the project directory:
   ```bash
   cd PrismAgent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # or using uv
   uv sync
   ```

3. Setup environment variables:
   ```bash
   # Windows
   $env:SERPER_SEARCH_API_KEY = "your_key_here"
   $env:DEEPSEEK_API_KEY = "your_key_here"
   ```

### Running the Agent

You can interact with PrismAgent via the command line:

```bash
python main.py --model deepseek --model_name deepseek-chat --question "求解方程 x^2 + 5x + 6 = 0 的根，并搜索这个方程在物理学中的应用。"
```

#### Command Line Arguments:
- `--model`: Choose the provider (`deepseek`, `qwen`).
- `--model_name`: Specific model ID (e.g., `deepseek-reasoner`).
- `--question`: Your query or task.
- `--mcp_servers`: Choose which tools to load (default: `math web code`).

## 🛠 MCP Servers

### Math Server
Provides high-level mathematical tools including symbolic differentiation, integration, equation solving, and statistical analysis.

### Web Server
Empowers the agent with real-time information. Supports standard text search, academic search (Scholar), visual search (Lens), and full webpage content extraction.

### Code Server
Allows the agent to write and execute code in a persistent environment. It supports file management and terminal command execution with built-in security auditing.

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
