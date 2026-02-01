"""
AgentCore Evaluation Agent with Observability and Built-in Evaluators.
Uses BedrockAgentCoreApp framework with MCP server integration.
Tracks user_id and session_id for observability and evaluation.
"""

import os
from urllib.parse import quote
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# ============================================================================
# Configuration
# ============================================================================

# MCP Server configuration
USE_MCP_ARN = os.getenv("USE_MCP_ARN", "true").lower() in ("true", "1", "yes")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
MCP_SERVER_ARN = os.getenv("MCP_SERVER_ARN", "arn:aws:bedrock-agentcore:us-west-2:381492273521:runtime/mcp_server_pdz_02-eHybfZHxYT")

# Default user/session for local testing
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "test-user-001")
DEFAULT_SESSION_ID = os.getenv("DEFAULT_SESSION_ID", "test-session-001")

print("\n" + "=" * 80)
print(" AgentCore Evaluation Agent - Initialization")
print("=" * 80)

# ============================================================================
# Initialize MCP Client
# ============================================================================

print("[1/4] Creating MCP Client...")
if USE_MCP_ARN:
    print(f"      MCP Mode: AgentCore Runtime (ARN)")
    print(f"      ARN: {MCP_SERVER_ARN}")
    try:
        from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client
        encoded_arn = quote(MCP_SERVER_ARN, safe="")
        mcp_endpoint_url = f"https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
        mcp_client = MCPClient(
            lambda: aws_iam_streamablehttp_client(
                endpoint=mcp_endpoint_url,
                aws_region="us-west-2",
                aws_service="bedrock-agentcore"
            )
        )
        print("      ✓ Using AWS IAM authentication")
    except ImportError:
        print("      ⚠ mcp-proxy-for-aws not installed, falling back to HTTP")
        from mcp.client.streamable_http import streamable_http_client
        mcp_client = MCPClient(lambda: streamable_http_client(MCP_SERVER_URL))
else:
    print(f"      MCP Mode: HTTP Endpoint")
    print(f"      URL: {MCP_SERVER_URL}")
    from mcp.client.streamable_http import streamable_http_client
    mcp_client = MCPClient(lambda: streamable_http_client(MCP_SERVER_URL))
    print("      ✓ Using HTTP client")

# ============================================================================
# Initialize Strands Agent
# ============================================================================

print("\n[2/4] Creating Strands Agent...")
bedrock_model = BedrockModel(model_id="anthropic.claude-3-5-sonnet-20240620-v1:0")
agent = Agent(model=bedrock_model, tools=[mcp_client])
print("      ✓ Bedrock Model: Claude 3.5 Sonnet")
print("      ✓ MCP Tools: Auto-discovered from MCP server")

# ============================================================================
# Configure Observability
# ============================================================================

print("\n[3/4] Configuring Observability...")
# Note: Observability is automatically enabled in BedrockAgentCoreApp
# Tracing, metrics, and logging are handled by the framework
print("      ✓ Tracing: Auto-enabled by AgentCore")
print("      ✓ Metrics: Auto-enabled by AgentCore")
print("      ✓ Logging: Auto-configured")

# ============================================================================
# Initialize BedrockAgentCoreApp
# ============================================================================

print("\n[4/4] Initializing BedrockAgentCoreApp...")
app = BedrockAgentCoreApp()
print("      ✓ AgentCore App initialized with observability")
print("=" * 80 + "\n")


# ============================================================================
# Agent Entrypoint with User/Session Tracking
# ============================================================================

@app.entrypoint
def agent_invocation(payload, context):
    """
    Main agent invocation handler.
    Extracts user_id and session_id from payload or context for tracking.
    """
    # Extract user inputs
    user_message = payload.get("prompt", "No prompt provided")
    
    # Extract or use default user_id and session_id
    # Context is a RequestContext object, use getattr() instead of .get()
    user_id = payload.get("user_id") or getattr(context, "user_id", None) or DEFAULT_USER_ID
    session_id = payload.get("session_id") or getattr(context, "session_id", None) or DEFAULT_SESSION_ID
    
    # Log invocation details
    print("\n" + "=" * 80)
    print(f" Agent Invocation")
    print("=" * 80)
    print(f" User ID:     {user_id}")
    print(f" Session ID:  {session_id}")
    print(f" Prompt:      {user_message[:100]}{'...' if len(user_message) > 100 else ''}")
    print("=" * 80)
    
    # Add observability context - Set trace attributes so they appear in observability dashboard
    # These are CRITICAL for evaluation to find and correlate spans
    if hasattr(context, 'set_trace_attribute'):
        context.set_trace_attribute("user_id", user_id)
        context.set_trace_attribute("session_id", session_id)
        context.set_trace_attribute("prompt_length", len(user_message))
        print(f" [TRACE] Set attributes: user_id={user_id}, session_id={session_id}")
    
    # Set OpenTelemetry baggage for session_id propagation across traces
    # This ensures the session_id is included in trace context for evaluation
    try:
        from opentelemetry import trace, baggage
        
        # Set baggage for context propagation
        ctx = baggage.set_baggage("session_id", session_id)
        ctx = baggage.set_baggage("user_id", user_id, context=ctx)
        
        # Set attributes on current span
        current_span = trace.get_current_span()
        if current_span:
            current_span.set_attribute("user_id", user_id)
            current_span.set_attribute("session_id", session_id)
            current_span.set_attribute("prompt_length", len(user_message))
            # Also set as resource attribute for broader visibility
            current_span.set_attribute("http.request.body.session_id", session_id)
            print(f" [OTEL] Set OpenTelemetry attributes and baggage")
    except Exception as e:
        print(f" [OTEL] Note: {e}")
    
    # Invoke agent with X-Ray tracing
    try:
        from opentelemetry import trace as otel_trace
        tracer = otel_trace.get_tracer(__name__)
        
        # Create a span for the agent invocation
        with tracer.start_as_current_span("agent_invocation") as span:
            span.set_attribute("user_id", user_id)
            span.set_attribute("session_id", session_id)
            span.set_attribute("model", "claude-3-5-sonnet")
            span.set_attribute("prompt_length", len(user_message))
            
            result = agent(user_message)
            
            span.set_attribute("response_received", True)
        
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
        
        print(f"\n[RESPONSE] {response_text[:200]}{'...' if len(response_text) > 200 else ''}\n")
        
        # Return structured response with metadata
        return {
            "result": result.message if hasattr(result, 'message') else {"content": [{"text": response_text}]},
            "metadata": {
                "user_id": user_id,
                "session_id": session_id,
                "response_length": len(response_text)
            }
        }
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}\n")
        if hasattr(context, 'set_trace_attribute'):
            context.set_trace_attribute("error", str(e))
        
        return {
            "error": str(e),
            "metadata": {
                "user_id": user_id,
                "session_id": session_id
            }
        }


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" Starting AgentCore Evaluation Agent")
    print("=" * 80)
    print(" Framework: BedrockAgentCoreApp")
    print(" Observability: Enabled")
    print(" Evaluation: Ready for built-in evaluators")
    print("=" * 80 + "\n")
    
    app.run()
