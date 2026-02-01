"""Test deployed MCP Server runtime using boto3"""
import boto3
import json
import os
import sys
from botocore.exceptions import ClientError


def call_mcp(client, runtime_arn, method, params=None):
    """
    Call an MCP method on the agent runtime.
    
    Args:
        client: boto3 bedrock-agentcore client
        runtime_arn: The runtime ARN
        method: The MCP method to call (e.g., 'tools/list', 'tools/call')
        params: Optional parameters for the method
    
    Returns:
        The result from the MCP response
    """
    if params is None:
        params = {}

    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }).encode()

    try:
        response = client.invoke_agent_runtime(
            agentRuntimeArn=runtime_arn,
            payload=payload,
            qualifier='DEFAULT',
            contentType='application/json',
            accept='application/json, text/event-stream'
        )

        raw = response['response'].read().decode()
        json_data = json.loads(raw[raw.find('{'):])
        return json_data['result']

    except ClientError as e:
        print(f"\n{'=' * 70}")
        print("AWS ClientError:")
        print(json.dumps(e.response, indent=2, default=str))
        print(f"{'=' * 70}\n")
        raise


def main():
    # Get runtime ARN from environment
    runtime_arn = os.getenv("MCP_RUNTIME_ARN", "arn:aws:bedrock-agentcore:us-west-2:381492273521:runtime/mcp_server_pdz_02-eHybfZHxYT")
    
    if not runtime_arn:
        print("ERROR: MCP_RUNTIME_ARN environment variable is not set")
        print("Usage:")
        print("  $env:MCP_RUNTIME_ARN='arn:aws:bedrock-agentcore:us-west-2:381492273521:runtime/mcp-server-pdz-02-xyz'")
        print("  python test_deployed.py")
        sys.exit(1)
    
    print("=" * 70)
    print(" Testing MCP Server (Deployed)")
    print("=" * 70)
    print(f" Runtime ARN: {runtime_arn}\n")
    
    # Initialize the Bedrock AgentCore client
    client = boto3.client('bedrock-agentcore', region_name='us-west-2')
    
    try:
        # List available tools
        print("[Tools] Listing available tools...")
        tools_result = call_mcp(client, runtime_arn, "tools/list")
        print(f"Found {len(tools_result['tools'])} tools:")
        for tool in tools_result['tools']:
            print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
        print()
        
        # Test 1: calculate_statistics
        print("[Test 1] calculate_statistics([10, 20, 30, 40, 50])")
        stats_result = call_mcp(client, runtime_arn, "tools/call", {
            "name": "calculate_statistics",
            "arguments": {"numbers": [10, 20, 30, 40, 50]}
        })
        print("Result:")
        print(json.dumps(stats_result['content'], indent=2))
        print()
        
        # Test 2: compound_interest
        print("[Test 2] compound_interest(principal=1000, rate=5, time=10)")
        interest_result = call_mcp(client, runtime_arn, "tools/call", {
            "name": "compound_interest",
            "arguments": {
                "principal": 1000,
                "rate": 5,
                "time": 10,
                "frequency": 12
            }
        })
        print("Result:")
        print(json.dumps(interest_result['content'], indent=2))
        print()
        
        # Test 3: text_analyzer
        print("[Test 3] text_analyzer('Hello world. This is a test.')")
        text_result = call_mcp(client, runtime_arn, "tools/call", {
            "name": "text_analyzer",
            "arguments": {"text": "Hello world. This is a test."}
        })
        print("Result:")
        print(json.dumps(text_result['content'], indent=2))
        print()
        
        print("=" * 70)
        print(" All tests passed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
