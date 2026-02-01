# Agent (agent_pdz_02)

Agent AgentCore Runtime. Strands agent (Bedrock) on port 8080; uses MCP server tools via MCPClient.

**Run locally:** `.\1_test_local.ps1` (uses local MCP if MCP container is running).  
**Deploy:** `.\2_push_to_ecr.ps1` → create runtime; set **`MCP_SERVER_ARN`** to the MCP server’s ARN. Do not set `USE_MCP_ARN=false`.  
**Test deployed:** `$env:AGENT_RUNTIME_ARN = "arn:..."; python test_deployed.py`

Deploy the MCP server runtime **first**.
