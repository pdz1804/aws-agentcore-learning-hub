# agentcore-testing

AgentCore Runtime samples and tests for AWS Bedrock.

## Structure

```
agentcore-testing/
├── agentcore-runtime-agent/   # Agent runtimes (see its README)
│   ├── agent_pdz_01/          # Single agent (Strands + Bedrock)
│   └── agent_pdz_02/          # MCP server + agent (two runtimes)
├── LICENSE
└── README.md
```

## Quick start

- **Single agent:** [agentcore-runtime-agent/agent_pdz_01/](agentcore-runtime-agent/agent_pdz_01/) — build, push ECR, deploy.
- **MCP + agent:** [agentcore-runtime-agent/agent_pdz_02/](agentcore-runtime-agent/agent_pdz_02/) — deploy MCP server first, then agent.

See each folder’s README for run and deploy steps.
