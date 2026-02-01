"""
Test the agent locally with user_id and session_id tracking.
"""

import json
from datetime import datetime

# Mock context for local testing
class MockContext:
    def __init__(self):
        self.attributes = {}
    
    def set_trace_attribute(self, key, value):
        self.attributes[key] = value
        print(f"   [TRACE] {key} = {value}")
    
    def get(self, key, default=None):
        return self.attributes.get(key, default)


def test_agent_local():
    """Test the agent locally"""
    print("\n" + "=" * 80)
    print(" Local Agent Test with User/Session Tracking")
    print("=" * 80 + "\n")
    
    # Import agent after setting environment for local testing
    import os
    os.environ["USE_MCP_ARN"] = "false"
    os.environ["MCP_SERVER_URL"] = "http://localhost:8000/mcp"
    
    from agent import agent_invocation
    
    # Test cases with different user_id and session_id
    test_cases = [
        {
            "prompt": "What is the capital of France?",
            "user_id": "test-user-001",
            "session_id": "test-session-001"
        },
        {
            "prompt": "Help me with available tools",
            "user_id": "test-user-001",
            "session_id": "test-session-002"
        },
        {
            "prompt": "Explain quantum computing",
            "user_id": "test-user-002",
            "session_id": "test-session-003"
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
        
        # Create mock context
        context = MockContext()
        context.attributes = {
            "user_id": test_case.get("user_id"),
            "session_id": test_case.get("session_id")
        }
        
        # Invoke agent
        try:
            result = agent_invocation(test_case, context)
            
            print("\n[RESULT]")
            print(json.dumps(result, indent=2))
            
            results.append({
                "test_case": test_case,
                "result": result,
                "status": "success",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"\n[ERROR] {str(e)}")
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
    output_file = f"test_results_local_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✓ Test results saved to: {output_file}\n")


if __name__ == "__main__":
    test_agent_local()
