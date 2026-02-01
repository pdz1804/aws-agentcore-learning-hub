"""
Invoke the Agent PDZ-01 Runtime deployed on AWS Bedrock AgentCore
"""

import boto3
import json
import uuid
from datetime import datetime

# Configuration
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:ap-southeast-1:381492273521:runtime/agent_pdz_01-cQUpBd59IF"
REGION = "ap-southeast-1"

def invoke_agent_runtime(prompt: str, session_id: str = None) -> dict:
    """
    Invoke the agent runtime with a prompt.
    
    Args:
        prompt: User message to send to the agent
        session_id: Optional session ID (generates one if not provided)
    
    Returns:
        Response from the agent
    """
    # Generate session ID if not provided (must be 33+ characters)
    if not session_id:
        session_id = f"session-{uuid.uuid4()}"
    
    print("\n" + "=" * 70)
    print(" Invoking Agent PDZ-01 Runtime")
    print("=" * 70)
    print(f"[Time] {datetime.utcnow().isoformat()}Z")
    print(f"[ARN] {AGENT_RUNTIME_ARN}")
    print(f"[Session ID] {session_id}")
    print(f"[Prompt] {prompt}")
    print("")
    
    # Create Bedrock AgentCore client
    client = boto3.client('bedrock-agentcore', region_name=REGION)
    
    # Prepare payload (AWS expects just the prompt)
    payload = json.dumps({"prompt": prompt})
    
    print(f"[Payload] {payload}")
    print("")
    
    try:
        # Invoke the runtime
        print("[Status] Calling invoke_agent_runtime...")
        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_RUNTIME_ARN,
            runtimeSessionId=session_id,
            payload=payload
            # Note: qualifier is optional, defaults to "DEFAULT"
        )
        
        # Read response body
        response_body = response['response'].read()
        response_data = json.loads(response_body)
        
        print("[Status] SUCCESS")
        print("")
        print("[Response Body]")
        print(json.dumps(response_data, indent=2))
        print("")
        
        return response_data
    
    except Exception as e:
        print(f"[Status] FAILED")
        print(f"[Error] {str(e)}")
        print("")
        raise


if __name__ == "__main__":
    import sys
    
    # Get prompt from command line or use default
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Hello! What can you help me with?"
    
    try:
        result = invoke_agent_runtime(prompt)
        print("=" * 70)
        print("")
        
        # Extract agent response
        if "output" in result and "message" in result["output"]:
            message = result["output"]["message"]
            if "content" in message and len(message["content"]) > 0:
                agent_text = message["content"][0].get("text", "No response")
                print("Agent Response:")
                print("-" * 70)
                print(agent_text)
                print("-" * 70)
                print("")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
