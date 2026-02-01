"""Test deployed Agent runtime - Focus on MCP tool invocation"""
import os
import boto3
import json
import sys


def test_deployed_agent():
    # Get runtime ARN from environment
    runtime_arn = os.getenv("AGENT_RUNTIME_ARN", "arn:aws:bedrock-agentcore:us-west-2:381492273521:runtime/agent_pdz_02-IDIqXK7V5r")
    if not runtime_arn:
        print("ERROR: Set AGENT_RUNTIME_ARN environment variable")
        print("Usage:")
        print("  $env:AGENT_RUNTIME_ARN='arn:aws:bedrock-agentcore:us-west-2:381492273521:runtime/agent-pdz-02-xyz'")
        print("  python test_deployed.py")
        sys.exit(1)
    
    print("=" * 70)
    print(" Testing Deployed Agent with MCP Tools")
    print("=" * 70)
    print(f" ARN: {runtime_arn}\n")
    
    client = boto3.client('bedrock-agentcore', region_name='us-west-2')
    
    test_cases = [
        {
            "name": "Calculate Statistics",
            "prompt": "Calculate statistics for these numbers: 10, 20, 30, 40, 50"
        },
        {
            "name": "Compound Interest",
            "prompt": "Calculate compound interest: $5000 invested at 6% for 10 years, compounded monthly"
        },
        {
            "name": "Text Analyzer",
            "prompt": "Analyze this text: 'Hello world. This is a test. Testing AI capabilities.'"
        }
    ]
    
    for idx, test in enumerate(test_cases, 1):
        print(f"[Test {idx}/{len(test_cases)}] {test['name']}")
        print(f"  Prompt: {test['prompt']}")
        
        try:
            response = client.invoke_agent_runtime(
                agentRuntimeArn=runtime_arn,
                payload=json.dumps({"prompt": test['prompt']}).encode(),
                qualifier='DEFAULT',
                contentType='application/json',
                accept='application/json'
            )
            
            result = json.loads(response['response'].read())
            text = result["output"]["message"]["content"][0]["text"]
            text_safe = text.encode('ascii', 'ignore').decode('ascii')
            
            print(f"  Response: {text_safe[:250]}...\n")
            
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 70)
    print(" All MCP tool tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    test_deployed_agent()
