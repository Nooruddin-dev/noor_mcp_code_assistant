# 🚀 Noor MCP Code Assistant

> MCP (Model Context Protocol) Server that bridges Claude Desktop with your RAG-powered Code Agent API.

[![Author](https://img.shields.io/badge/Author-Noor%20Uddin-blue)](https://github.com/nooruddin-dev)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Noor%20Uddin-0A66C2)](https://www.linkedin.com/in/nooruddin-dev/)
[![YouTube](https://img.shields.io/badge/YouTube-Noor%20Codelogics-red)](https://youtube.com/@noorcodelogics)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://python.org)


---

## 📋 Overview

This project creates an MCP server that allows **Claude Desktop** to communicate with your existing **RAG Code Agent API** running at `localhost:8900`. When you ask code-related questions in Claude Desktop, it can use this tool to fetch context-aware answers from your codebase.

### 🎯 Features

- ✅ Seamless integration with Claude Desktop
- ✅ Connects to existing RAG API (`/api/chat/rag`)
- ✅ Session management for conversation continuity
- ✅ Comprehensive error handling
- ✅ Configurable via environment variables
- ✅ Ready for future agent extensions (SQL, React, Java)

---

## 🏗️ Project Structure
```
noor_mcp_code_assistant_parent/
├── env_container/              # Virtual environment
│   ├── bin/
│   ├── lib/
│   └── ...
└── noor_mcp_code_assistant/    # Project source
    ├── mcp_server.py           # Main MCP server
    ├── config.py               # Configuration management
    ├── requirements.txt        # Dependencies
    ├── .env.example            # Environment template
    ├── .env                    # Your configuration (git-ignored)
    └── README.md               # This file
```

---

## 🚀 Quick Start

### 1️⃣ Create Virtual Environment

Navigate to the parent folder and create the environment:
```bash
cd noor_mcp_code_assistant_parent
python3.11 -m venv env_container
```

Activate the environment:
```bash
# Linux/WSL/macOS
source env_container/bin/activate

# Windows PowerShell
.\env_container\Scripts\Activate
```

---

### 2️⃣ Install Requirements
```bash
cd noor_mcp_code_assistant
pip install -r requirements.txt
```

---

### 3️⃣ Configure Environment Variables

Copy the example file and customize:
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```bash
# Required
RAG_API_BASE_URL=http://localhost:8900
RAG_CHAT_ENDPOINT=/api/chat/rag

# Optional
DEFAULT_SESSION_ID=claude-desktop-session
REQUEST_TIMEOUT=120
```

---

### 4️⃣ Configure Claude Desktop

Locate your Claude Desktop configuration file:

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```
(Usually: `C:\Users\<YourUsername>\AppData\Roaming\Claude\claude_desktop_config.json`)

Add the MCP server configuration:
```json
{
  "mcpServers": {
    "noor-code-assistant": {
      "command": "wsl",
      "args": [
        "-d", "Ubuntu-20.04",
        "--",
        "/home/<your-username>/noor_mcp_code_assistant_parent/env_container/bin/python",
        "/home/<your-username>/noor_mcp_code_assistant_parent/noor_mcp_code_assistant/mcp_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

> ⚠️ **Important:** Replace `<your-username>` with your actual WSL username and adjust paths accordingly.

#### 🔍 Find Your WSL Distribution Name
```powershell
wsl --list --verbose
```

Use the exact name shown (e.g., `Ubuntu-20.04`, `Ubuntu`, etc.)

---

### 5️⃣ Verify Setup

**Step 1:** Ensure your RAG API is running:
```bash
# In WSL terminal
cd /path/to/your/rag-project
source env_container/bin/activate
uvicorn main:app --reload --port 8900
```

**Step 2:** Test the RAG API:
```bash
curl -X POST http://localhost:8900/api/chat/rag \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test", "message": "hello"}'
```

**Step 3:** Restart Claude Desktop completely (check system tray)

**Step 4:** The `noor-code-assistant` tool should now appear in Claude Desktop!

---

## 💬 Usage Examples

Once configured, you can ask Claude Desktop:

> "Use the code assistant to create a C# function that gets employee requests by employee ID"

> "Ask the code assistant how pagination is implemented in my project"

> "Use code_assistant to show me the DTO structure for Employee entity"

---

## 🔮 Adding Future Agents

When you're ready to add more agents (SQL, React, Java):

### Step 1: Add endpoints to your RAG API
```python
@app.post("/api/sql/agent")
async def sql_agent(request: SQLAgentRequest):
    # Your SQL agent logic
    pass
```

### Step 2: Update `.env`
```bash
SQL_AGENT_ENDPOINT=/api/sql/agent
```

### Step 3: Uncomment tool definitions in `mcp_server.py`

Look for the commented `sql_agent` tool and handler, then uncomment them.

### Step 4: Restart Claude Desktop

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **MCP server not appearing** | Check Claude Desktop logs at `%APPDATA%\Claude\logs\` |
| **Connection refused** | Ensure RAG API is running on `localhost:8900` |
| **WSL path issues** | Use full Linux paths (e.g., `/home/user/...`) |
| **Python not found** | Use full path to Python in venv |
| **Timeout errors** | Increase `REQUEST_TIMEOUT` in `.env` |

### 📋 View Logs

**Claude Desktop Logs:**
```
C:\Users\<YourUsername>\AppData\Roaming\Claude\logs\
```

**Test MCP Server Standalone:**
```bash
cd noor_mcp_code_assistant
source ../env_container/bin/activate
python mcp_server.py
```

---

## 📊 Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `RAG_API_BASE_URL` | `http://localhost:8900` | Base URL of your RAG API |
| `RAG_CHAT_ENDPOINT` | `/api/chat/rag` | Chat endpoint path |
| `DEFAULT_SESSION_ID` | `claude-desktop-session` | Default session for continuity |
| `REQUEST_TIMEOUT` | `120` | API timeout in seconds |

---

## 🔐 Security Notes

- This MCP server only makes **outbound** HTTP requests to your local RAG API
- No sensitive data is stored or logged
- Session IDs are used only for conversation context
- All communication happens over localhost

---

## 📄 License

MIT License - Feel free to use and modify!

---

## 👨‍💻 Author

**Noor Uddin**
- 🎥 YouTube: [Noor Codelogics](https://youtube.com/@noorcodelogics)
- 💼 LinkedIn: [Noor Uddin](https://linkedin.com/in/nooruddin-dev)
- 🛒 CodeCanyon: 180+ Sales

---

## 🌟 Support

If you find this helpful, please:
- ⭐ Star the repository
- 📺 Subscribe to [Noor Codelogics](https://youtube.com/@noorcodelogics)
- 🔗 Share with fellow developers

Happy Coding! 🚀