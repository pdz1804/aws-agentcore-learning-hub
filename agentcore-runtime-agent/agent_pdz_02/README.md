# Agent PDZ-02

Two separate AgentCore Runtimes: an **MCP server** (tools) and a **Strands agent** (Bedrock) that uses those tools. Deploy the MCP server first, then the agent.

---

## Structure

```
agent_pdz_02/
├── mcp_server/          # MCP Server Runtime (port 8000)
│   ├── mcp_server.py    # FastAPI + tools: calculate_statistics, compound_interest, text_analyzer
│   ├── 1_test_local.ps1
│   ├── 2_push_to_ecr.ps1
│   ├── test_local.py, test_deployed.py
│   ├── Dockerfile, requirements.txt
│   └── __init__.py
│
└── agent/               # Agent Runtime (port 8080)
    ├── agent.py         # Strands agent (Bedrock) + MCPClient → MCP tools
    ├── 1_test_local.ps1
    ├── 2_push_to_ecr.ps1
    ├── test_local.py, test_deployed.py
    ├── Dockerfile, requirements.txt
    └── __init__.py
```

---

## Run locally

**MCP server**
```powershell
cd mcp_server
.\1_test_local.ps1
```

**Agent** (uses local MCP if the MCP container is running; otherwise expects deployed MCP)
```powershell
cd agent
.\1_test_local.ps1
```

---

## Deploy

1. **MCP server first:** `cd mcp_server` → `.\2_push_to_ecr.ps1` → create runtime in AWS, note its ARN.
2. **Agent:** `cd agent` → `.\2_push_to_ecr.ps1` → create runtime; set env **`MCP_SERVER_ARN`** to the MCP server’s ARN. Do not set `USE_MCP_ARN=false` when deploying.

---

## Test deployed

**MCP server**
```powershell
cd mcp_server
$env:MCP_RUNTIME_ARN = "arn:aws:bedrock-agentcore:..."
python test_deployed.py
```

**Agent**
```powershell
cd agent
$env:AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:..."
python test_deployed.py
```
