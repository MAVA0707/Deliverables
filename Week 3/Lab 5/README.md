# LAB | Using MCP in LangChain

A hands-on lab that walks through integrating **MCP (Model Context Protocol)** servers with **LangChain** agents — enabling agents to access external tools and resources through a standardised, unified interface.

---

## File Map

```
.
├── mcp_langchain.ipynb   # Main lab notebook (all steps)
├── lab_summary.md        # One-paragraph MCP vs direct API comparison
└── README.md             # This file
```

---

## What You'll Learn

- Connect to MCP servers using `MultiServerMCPClient`
- Load and inspect MCP tools as native LangChain tools
- Build an agent (`create_agent`) powered by MCP tools
- Access MCP resources for read-only context injection
- Write tool interceptors (middleware) for logging and observability
- Configure a multi-server MCP client
- Compare MCP integration against direct API integration

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.10+ | `python --version` |
| OpenAI API key | Required for the LLM |
| Internet access | Connects to `https://docs.langchain.com/mcp` |

---

## Setup

### 1. Clone / download this repository

```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install langchain langchain-openai langchain-mcp-adapters langgraph mcp python-dotenv httpx
```

Or run the first cell of the notebook which does this for you:

```python
%pip install langchain langchain-openai langchain-mcp-adapters langgraph mcp python-dotenv -q
```

### 4. Set your API key

Create a `.env` file in the same directory as the notebook:

```
OPENAI_API_KEY=sk-...
```

---

## How to Run

```bash
jupyter notebook mcp_langchain.ipynb
```

Then execute the cells top-to-bottom. All cells use `await` (top-level async), which works natively in Jupyter.

---

## Notebook Structure

| Step | Description |
|---|---|
| **1 — Setup** | Install packages, load API key, initialise LLM |
| **2 — Connect** | Configure `MultiServerMCPClient` for the LangChain docs MCP server |
| **3 — Load Tools** | Call `get_tools()` and inspect available tools |
| **4 — Agent** | Build a `create_agent` and run test queries |
| **5 — Resources** | Explore `get_resources()` and how to inject resource content into prompts |
| **6 — Interceptors** | Add logging + call-counter middleware via `tool_interceptors` |
| **7 — Multi-Server** | Extend the client dict to manage multiple MCP servers, including optional Claude Code |
| **8 — Practical Example** | Full documentation Q&A session with a polished agent |
| **9 — Comparison (optional)** | MCP vs direct API — side-by-side implementation and trade-off table |

---

## MCP Server Used

The lab connects to the **LangChain Documentation MCP Server** — a public, zero-setup server ideal for learning:

- **URL**: `https://docs.langchain.com/mcp`
- **Transport**: HTTP
- **Covers**: LangChain, LangGraph, LangSmith documentation

To use a local filesystem server instead, replace the server config with:

```python
"my-filesystem": {
    "transport": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/your/docs"]
}
```

---

## Key Concepts

### MultiServerMCPClient

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "server-name": {
        "transport": "http",          # or "stdio"
        "url": "https://..."          # for HTTP transport
    }
})

tools = await client.get_tools()      # stateless — no context manager needed
```

### Tool Interceptors

```python
async def my_interceptor(request, handler):
    print(f"Calling: {request.name}")
    result = await handler(request)
    return result

client = MultiServerMCPClient(servers, tool_interceptors=[my_interceptor])
```

### Agent

```python
from langchain.agents import create_agent

agent = create_agent(model=llm, tools=tools, system_prompt="...")
result = await agent.ainvoke({"messages": [HumanMessage(content="...")]})
print(result["messages"][-1].content)
```

---

## References

- [langchain-mcp-adapters docs](https://docs.langchain.com/oss/python/langchain/mcp)
- [LangChain MCP Server](https://docs.langchain.com/mcp)
- [MCP Official Documentation](https://modelcontextprotocol.io)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [LangChain create_agent](https://docs.langchain.com/oss/python/langchain/agents)
