# MCP Server (agent_pdz_02)

MCP Server AgentCore Runtime. FastAPI on port 8000; tools: `calculate_statistics`, `compound_interest`, `text_analyzer`.

**Run locally:** `.\1_test_local.ps1`  
**Deploy:** `.\2_push_to_ecr.ps1` → create runtime in AWS; note ARN for the agent.  
**Test deployed:** `$env:MCP_RUNTIME_ARN = "arn:..."; python test_deployed.py`

Deploy this runtime **before** the agent.
