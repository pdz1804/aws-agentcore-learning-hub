"""
Test the deployed agent on AgentCore Runtime with user_id and session_id.
"""

import boto3
import json
from datetime import datetime


def test_deployed_agent():
    """Test the agent deployed on AgentCore Runtime"""
    print("\n" + "=" * 80)
    print(" Testing Deployed Agent on AgentCore Runtime")
    print("=" * 80 + "\n")
    
    # AgentCore Runtime ARN (update with your actual ARN after deployment)
    AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-west-2:381492273521:runtime/evaluation_agent_02-ToChVoCQ4o"
    
    client = boto3.client('bedrock-agentcore', region_name='us-west-2')
    
    # Test cases with user_id and session_id
    test_cases = [
        {
            "prompt": "What is the capital of France?",
            "user_id": "deployed-user-001",
            "session_id": "deployed-session-001"
        },
        {
            "prompt": "Help me understand quantum computing",
            "user_id": "deployed-user-001",
            "session_id": "deployed-session-002"
        },
        {
            "prompt": "What tools are available?",
            "user_id": "deployed-user-002",
            "session_id": "deployed-session-003"
        }
    ]
    
    results = []
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f" Test Case {idx}/{len(test_cases)}")
        print(f"{'=' * 80}")
        print(f" User ID:     {test_case['user_id']}")
        print(f" Session ID:  {test_case['session_id']}")
        print(f" Prompt:      {test_case['prompt']}")
        print(f"{'=' * 80}\n")
        
        try:
            # Invoke the AgentCore Runtime
            response = client.invoke_agent_runtime(
                agentRuntimeArn=AGENT_RUNTIME_ARN,
                qualifier='DEFAULT',
                contentType='application/json',
                payload=json.dumps(test_case)
            )
            
            # Read the streaming response body
            response_body = json.loads(response['response'].read().decode('utf-8'))
            
            # Extract response text from the agent response
            if isinstance(response_body, dict):
                # Try to get text from different possible locations
                response_text = response_body.get('result', '')
                if isinstance(response_text, dict):
                    response_text = str(response_text)
                else:
                    response_text = str(response_text)
                
                # Or try from response field
                if not response_text or response_text == 'No response':
                    response_text = response_body.get('response', 'No response')
            else:
                response_text = str(response_body)
            
            # Clean response text for printing
            response_text_clean = response_text.encode('ascii', 'ignore').decode('ascii')
            print(f"  Response: {response_text_clean[:250]}...\n")
            
            print("[RESPONSE]")
            print(json.dumps(response_body, indent=2, default=str))
            
            results.append({
                "test_case": test_case,
                "response": response_body,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            results.append({
                "test_case": test_case,
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            })
    
    # Print summary
    print("\n" + "=" * 80)
    print(" Test Summary")
    print("=" * 80)
    print(f" Total Tests: {len(results)}")
    print(f" Passed:      {sum(1 for r in results if r['status'] == 'success')}")
    print(f" Failed:      {sum(1 for r in results if r['status'] == 'failed')}")
    print("=" * 80 + "\n")
    
    # Save results
    output_file = f"test_results_deployed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✓ Test results saved to: {output_file}\n")


if __name__ == "__main__":
    test_deployed_agent()
