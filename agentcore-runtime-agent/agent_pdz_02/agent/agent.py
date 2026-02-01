"""
Strands Agent for Amazon Bedrock AgentCore Runtime.
Uses MCP server tools via Strands MCPClient.
Supports both HTTP MCP servers and AgentCore Runtime MCP servers.
"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
import json
import os
from urllib.parse import quote
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

# ============================================================================
# Configuration
# ============================================================================

app = FastAPI(title="Agent PDZ-02")

# Choose MCP server mode: "arn" = AgentCore Runtime, "url" = HTTP endpoint
# Default True = use MCP_SERVER_ARN (for container/deployment). Set USE_MCP_ARN=false only for local HTTP MCP.
USE_MCP_ARN = os.getenv("USE_MCP_ARN", "true").lower() in ("true", "1", "yes")

# MCP Server configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
MCP_SERVER_ARN = os.getenv("MCP_SERVER_ARN", "arn:aws:bedrock-agentcore:us-west-2:381492273521:runtime/mcp_server_pdz_02-eHybfZHxYT")

AGENT_READY = False
strands_agent = None
mcp_client = None


# ============================================================================
# Initialize
# ============================================================================

print("\n" + "=" * 70)
print(" Agent PDZ-02 Initialization")
print("=" * 70)

# Determine MCP server type from constant
if USE_MCP_ARN:
    print(f" MCP Mode: AgentCore Runtime (USE_MCP_ARN=True)")
    print(f" ARN: {MCP_SERVER_ARN}\n")
    mcp_endpoint = MCP_SERVER_ARN
else:
    print(f" MCP Mode: HTTP Endpoint (USE_MCP_ARN=False)")
    print(f" URL: {MCP_SERVER_URL}\n")
    mcp_endpoint = MCP_SERVER_URL

# Create MCP client
print("[1/2] Creating MCP Client...")
if USE_MCP_ARN:
    # mcp-proxy-for-aws expects an HTTP(S) URL, not an ARN. Build the AgentCore invoke URL from ARN.
    try:
        from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client
        # Bedrock AgentCore invoke URL: https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT
        encoded_arn = quote(MCP_SERVER_ARN, safe="")
        mcp_endpoint_url = f"https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
        mcp_client = MCPClient(
            lambda: aws_iam_streamablehttp_client(
                endpoint=mcp_endpoint_url,
                aws_region="us-west-2",
                aws_service="bedrock-agentcore"
            )
        )
        print("      Using AWS IAM authentication for AgentCore Runtime")
    except ImportError:
        print("      ERROR: mcp-proxy-for-aws not installed")
        print("      Install: pip install mcp-proxy-for-aws")
        print("      Falling back to HTTP endpoint...")
        mcp_client = MCPClient(lambda: streamablehttp_client(MCP_SERVER_URL))
else:
    # For HTTP MCP servers, use streamable HTTP client
    mcp_client = MCPClient(lambda: streamablehttp_client(MCP_SERVER_URL))
    print("      Using HTTP client for MCP server")

print("      MCP Client created successfully")

# Create Strands agent with MCP client
print("\n[2/2] Creating Strands Agent...")
bedrock_model = BedrockModel(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0")
strands_agent = Agent(model=bedrock_model, tools=[mcp_client])
AGENT_READY = True

print("      ✓ Bedrock Model: Claude 3.5 Sonnet")
print("      ✓ MCP Tools: Auto-discovered from MCP server")
print("      ✓ Agent Status: Ready")
print("=" * 70 + "\n")


# ============================================================================
# Response Model
# ============================================================================

class InvocationResponse(BaseModel):
    output: Dict[str, Any]


# ============================================================================
# Endpoints
# ============================================================================

@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: Request):
    """Main invocation endpoint"""
    print(f"\n[INVOCATION] {datetime.now().isoformat()}Z")
    
    try:
        raw_body = await request.body()
        request_data = json.loads(raw_body)
        user_message = request_data.get("prompt", "")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="No prompt provided")
        
        print(f"[PROMPT] {user_message}")
        
        # Strands manages MCP client lifecycle automatically
        result = strands_agent(user_message)
        
        # Extract response text
        response_text = ""
        if hasattr(result, 'message'):
            message = result.message
            if isinstance(message, dict) and 'content' in message:
                content = message['content']
                if content and len(content) > 0:
                    first_content = content[0]
                    if isinstance(first_content, dict) and 'text' in first_content:
                        response_text = first_content['text']
        
        if not response_text:
            response_text = str(result)
        
        output = {
            "message": {
                "role": "assistant",
                "content": [{"text": response_text}]
            },
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"[RESPONSE] {response_text[:100]}...")
        return InvocationResponse(output=output)
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ping")
async def ping():
    """Health check"""
    return {
        "status": "healthy",
        "agent_ready": AGENT_READY,
        "mcp_mode": "arn" if USE_MCP_ARN else "url",
        "mcp_server": MCP_SERVER_ARN if USE_MCP_ARN else MCP_SERVER_URL
    }


@app.get("/")
async def root():
    """Info endpoint"""
    return {
        "agent": "PDZ-02",
        "status": "running",
        "bedrock_ready": AGENT_READY,
        "mcp_server": MCP_SERVER_ARN if USE_MCP_ARN else MCP_SERVER_URL,
        "mcp_server_type": "agentcore-runtime" if USE_MCP_ARN else "http",
        "mcp_tools": "auto-discovered"
    }


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 70)
    print(" Starting Agent PDZ-02")
    print("=" * 70)
    print(" Host: 0.0.0.0")
    print(" Port: 8080")
    print("=" * 70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8080)
