# agentcore-runtime-agent

AgentCore Runtime samples: single agent (PDZ-01) and MCP server + agent (PDZ-02).

## Structure

```
agentcore-runtime-agent/
├── agent_pdz_01/   # Single Strands agent (Bedrock), one runtime
├── agent_pdz_02/   # MCP server + Strands agent, two runtimes (deploy MCP first)
├── requirements.txt
└── README.md
```

## Quick start

**agent_pdz_01** — one runtime  
- Local: `cd agent_pdz_01` → `.\1_build_local.ps1`; run `python invoke_agent_local.py` from repo root or `agent_pdz_01`.  
- Deploy: `.\2_push_to_ecr.ps1` → `.\3_deploy_runtime.ps1`.  
- Invoke: `python invoke_agent_runtime.py "Your prompt"` (set runtime ARN in script or env).

**agent_pdz_02** — two runtimes (MCP server, then agent)  
- See [agent_pdz_02/README.md](agent_pdz_02/README.md) for run locally, deploy, and test deployed.

## Requirements

- Docker (ARM64 for ECR deploy)
- AWS CLI v2, credentials or IAM role
- PowerShell 7+ for scripts
- Python 3.11+ (uv recommended for agent_pdz_01)
