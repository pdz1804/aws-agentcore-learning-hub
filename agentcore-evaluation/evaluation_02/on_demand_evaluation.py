"""
On-Demand Evaluation - Use agentcore CLI for evaluation
The agentcore eval run command is the recommended approach for on-demand evaluation
"""

import json
import time
import subprocess
from datetime import datetime
import boto3
from boto3.session import Session

# Test cases
TEST_CASES = [
    {
        "name": "Statistics Tool Usage",
        "prompt": "Calculate statistics for these numbers: 10, 20, 30, 40, 50",
    },
    {
        "name": "Compound Interest Tool",
        "prompt": "If I invest $1000 at 5% annual interest for 2 years compounded monthly, how much will I have?",
    },
    {
        "name": "Text Analysis Tool",
        "prompt": "Analyze this text for me: 'The quick brown fox jumps over the lazy dog. This is a test sentence.'",
    },
]

def invoke_agent_runtime(agentcore_client, agent_arn, prompt, session_id):
    """Invoke agent and return response + runtime session ID"""
    try:
        response = agentcore_client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            qualifier="DEFAULT",
            payload=json.dumps({"prompt": prompt, "session_id": session_id})
        )
        
        runtime_session_id = response.get('runtimeSessionId')
        trace_id = response.get('traceId')
        
        # Extract response content
        content_parts = []
        if 'response' in response:
            for line in response['response'].iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if isinstance(data, dict) and 'result' in data:
                            result = data['result']
                            if isinstance(result, dict) and 'content' in result:
                                for item in result['content']:
                                    if isinstance(item, dict) and 'text' in item:
                                        content_parts.append(item['text'])
                    except:
                        pass
        
        response_text = "\n".join(content_parts) if content_parts else ""
        
        return {
            "response": response_text,
            "runtime_session_id": runtime_session_id,
            "trace_id": trace_id
        }
    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "runtime_session_id": None,
            "trace_id": None
        }

def run_on_demand_evaluation():
    """Run on-demand evaluation using agentcore CLI"""
    
    print("\n" + "=" * 80)
    print(" AgentCore On-Demand Evaluation (CLI-based)")
    print("=" * 80 + "\n")
    
    agent_id = "arn:aws:bedrock-agentcore:us-west-2:381492273521:runtime/evaluation_agent_02-ToChVoCQ4o"
    user_session_id = f"eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    region = "us-west-2"
    
    print(f"Agent ID: {agent_id}")
    print(f"User Session ID: {user_session_id}")
    print(f"Region: {region}\n")
    
    # Initialize clients
    agentcore_client = boto3.client('bedrock-agentcore', region_name=region)
    
    print("[1] Invoking agent with test cases...\n")
    
    runtime_session_ids = []
    
    for i, test in enumerate(TEST_CASES, 1):
        print(f"    [{i}/{len(TEST_CASES)}] {test['name']}")
        
        result = invoke_agent_runtime(agentcore_client, agent_id, test['prompt'], user_session_id)
        response_text = result['response']
        runtime_sid = result['runtime_session_id']
        
        if runtime_sid:
            runtime_session_ids.append(runtime_sid)
            print(f"        ✓ Response: {response_text[:80]}...")
            print(f"        ✓ RuntimeSessionId: {runtime_sid}\n")
        else:
            print(f"        ✗ Failed to get runtime session ID\n")
    
    if not runtime_session_ids:
        print("    ✗ Failed to get any runtime session IDs\n")
        return
    
    print(f"[2] Waiting for traces to be flushed to CloudWatch...\n")
    print("    Sleeping 5 seconds...\n")
    time.sleep(5)
    
    print("[3] Running on-demand evaluation via agentcore CLI...\n")
    
    all_results = []
    
    evaluators = [
        "Builtin.GoalSuccessRate",
        "Builtin.Correctness",
        "Builtin.ToolParameterAccuracy",
        "Builtin.ToolSelectionAccuracy"
    ]
    
    for idx, runtime_sid in enumerate(runtime_session_ids, 1):
        print(f"    [{idx}/{len(runtime_session_ids)}] Evaluating session {runtime_sid[:8]}...\n")
        
        # Build CLI command
        cmd = ["agentcore", "eval", "run", "--session-id", runtime_sid]
        for evaluator in evaluators:
            cmd.extend(["--evaluator", evaluator])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"        ✓ Evaluation completed\n")
                print(result.stdout)
                all_results.append({
                    "session_id": runtime_sid,
                    "output": result.stdout
                })
            else:
                print(f"        ✗ Error: {result.stderr}\n")
        
        except subprocess.TimeoutExpired:
            print(f"        ✗ Evaluation timed out\n")
        except FileNotFoundError:
            print(f"        ✗ agentcore CLI not found\n")
            print("        Install: pip install bedrock-agentcore-starter-toolkit\n")
        except Exception as e:
            print(f"        ✗ Error: {str(e)}\n")
    
    # Save results
    if all_results:
        output = {
            "timestamp": datetime.now().isoformat(),
            "user_session_id": user_session_id,
            "runtime_session_ids": runtime_session_ids,
            "test_cases": len(TEST_CASES),
            "evaluation_outputs": [r['output'] for r in all_results]
        }
        
        output_file = f"ondemand_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"✓ Results saved to: {output_file}\n")
    else:
        print("\n    ✗ No evaluation results\n")
        print("    Troubleshooting:")
        print("    1. Verify agentcore CLI is installed: pip install bedrock-agentcore-starter-toolkit")
        print("    2. Run manually: agentcore eval run --session-id <id> --evaluator Builtin.GoalSuccessRate")
        print("    3. Check CloudWatch for traces\n")

if __name__ == "__main__":
    run_on_demand_evaluation()


