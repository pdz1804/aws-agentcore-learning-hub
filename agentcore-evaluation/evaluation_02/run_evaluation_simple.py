"""
AgentCore Online Evaluation - Trigger with Test Cases
Invokes the agent with test prompts to trigger online evaluation.
Uses the online evaluation config: evaluation_evaluation_agent_02
Tests agent performance with MCP tools: calculate_statistics, compound_interest, text_analyzer
"""

import json
import os
import subprocess
import time
from datetime import datetime

import boto3
from boto3.session import Session
from bedrock_agentcore_starter_toolkit import Evaluation

# ============================================================================
# Test Cases Based on Available MCP Tools
# ============================================================================
# Available Tools from MCP Server:
# 1. calculate_statistics(numbers: List[float]) - Statistical analysis
# 2. compound_interest(principal, rate, time, frequency) - Financial calculations
# 3. text_analyzer(text) - Text analysis and metrics
# ============================================================================

TEST_CASES = [
    {
        "name": "Statistics Tool Usage",
        "prompt": "Calculate statistics for these numbers: 10, 20, 30, 40, 50",
        "tool_used": "calculate_statistics",
        "expected_output": "mean, median, std_dev"
    },
    {
        "name": "Compound Interest Tool",
        "prompt": "If I invest $1000 at 5% annual interest for 2 years compounded monthly, how much will I have?",
        "tool_used": "compound_interest",
        "expected_output": "final_amount, interest_earned"
    },
    {
        "name": "Text Analysis Tool",
        "prompt": "Analyze this text for me: 'The quick brown fox jumps over the lazy dog. This is a test sentence.'",
        "tool_used": "text_analyzer",
        "expected_output": "word_count, character_count, sentences"
    },
    {
        "name": "Tool Selection - Math",
        "prompt": "What's the standard deviation of: 100, 150, 200, 250, 300?",
        "tool_used": "calculate_statistics",
        "expected_output": "std_dev"
    },
    {
        "name": "Tool Selection - Finance",
        "prompt": "How much interest will I earn on $5000 at 4% for 3 years?",
        "tool_used": "compound_interest",
        "expected_output": "interest_earned, roi"
    }
]

# ============================================================================
# Configuration
# ============================================================================

def get_agent_info():
    """Get agent info from environment variables"""
    agent_id = os.getenv("AGENT_ID", "arn:aws:bedrock-agentcore:us-west-2:381492273521:runtime/evaluation_agent_02-ToChVoCQ4o")
    session_id = os.getenv("SESSION_ID", "quangphung-eval-session-20260201-183237")
    
    if not agent_id:
        raise ValueError("""
AGENT_ID environment variable not set.
Please set it with your agent ARN:
  $env:AGENT_ID = 'arn:aws:bedrock-agentcore:us-west-2:381492273521:runtime/evaluation_agent_02-ToChVoCQ4o'
        """)
    if not session_id:
        raise ValueError("""
SESSION_ID environment variable not set.
Please set it with your session ID:
  $env:SESSION_ID = 'eval-session-20260201-175719'
        """)
    
    return agent_id, session_id


# ============================================================================
# Invoke Agent with Test Cases (Trigger Online Evaluation)
# ============================================================================

def invoke_agent_runtime(agentcore_client, agent_arn, prompt, session_id):
    """
    Invoke the agent with a test prompt and session_id.
    Properly handles AgentCore application/json response format.
    Returns both the response text AND the runtime session ID for observability.
    """
    try:
        # Build payload with prompt and session_id for observability tracking
        payload = {
            "prompt": prompt,
            "session_id": session_id  # CRITICAL: Pass session_id so agent can tag traces
        }
        
        response = agentcore_client.invoke_agent_runtime(
            agentRuntimeArn=agent_arn,
            qualifier="DEFAULT",
            payload=json.dumps(payload)
        )
        
        # Extract runtime session ID from response (needed for observability queries)
        runtime_session_id = response.get('runtimeSessionId', None)
        trace_id = response.get('traceId', None)
        
        # AgentCore returns application/json response with streaming body
        # Structure: {"result": {"role": "assistant", "content": [{"text": "..."}, ...]}}
        content_parts = []
        
        # Read streaming response
        if 'response' in response:
            try:
                # Read all lines from the stream
                for line in response['response'].iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        # Parse as JSON (each line is a complete JSON object)
                        try:
                            data = json.loads(line_text)
                            
                            # Extract text from AgentCore response structure
                            if isinstance(data, dict) and 'result' in data:
                                result = data['result']
                                if isinstance(result, dict) and 'content' in result:
                                    contents = result['content']
                                    if isinstance(contents, list):
                                        for item in contents:
                                            if isinstance(item, dict) and 'text' in item:
                                                content_parts.append(item['text'])
                        except json.JSONDecodeError:
                            # Not JSON, skip
                            pass
            except Exception as e:
                return {
                    "response": f"Error reading response stream: {str(e)}",
                    "runtime_session_id": runtime_session_id,
                    "trace_id": trace_id
                }
        
        # Return combined content with metadata
        response_text = "\n".join(content_parts) if content_parts else "(Agent responded with no text content)"
        
        return {
            "response": response_text,
            "runtime_session_id": runtime_session_id,
            "trace_id": trace_id
        }
    
    except Exception as e:
        return {
            "response": f"Error invoking agent: {str(e)}",
            "runtime_session_id": None,
            "trace_id": None
        }


def run_evaluation():
    """
    Run online evaluation by invoking the agent with test cases.
    Following the AgentCore Evaluations tutorial pattern.
    """
    
    print("\n" + "=" * 80)
    print(" AgentCore Online Evaluation - Trigger with Test Cases")
    print("=" * 80)
    
    # Get agent info
    agent_id, session_id = get_agent_info()
    print(f"\n Agent ID (ARN): {agent_id}")
    print(f" Session ID:    {session_id}")
    print("\n" + "=" * 80)
    
    # Initialize boto session and clients
    boto_session = Session(region_name="us-west-2")
    region = boto_session.region_name or "us-west-2"
    print(f" Region: {region}\n")
    
    # Initialize AgentCore and Evaluation clients
    print("[1/4] Initializing clients...")
    agentcore_client = boto3.client('bedrock-agentcore', region_name=region)
    eval_client = Evaluation(region=region)
    print("      ✓ Clients ready\n")
    
    # Display test cases
    print("[2/4] Test Cases to Invoke:")
    print("      MCP Tools Available:")
    print("        • calculate_statistics - Statistical analysis of numbers")
    print("        • compound_interest - Financial compound interest calculations")
    print("        • text_analyzer - Text analysis and metrics\n")
    print("      Test Scenarios:")
    for i, test in enumerate(TEST_CASES, 1):
        print(f"        {i}. {test['name']}")
        print(f"           Tool: {test['tool_used']}")
        print(f"           Prompt: {test['prompt'][:60]}...")
    print()
    
    # Invoke agent with test cases (triggers online evaluation)
    print("[3/4] Invoking agent with test prompts...")
    print("      This will generate traces for online evaluation\n")
    
    invocation_results = []
    runtime_session_ids = []  # Collect runtime session IDs for evaluation queries
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"      [{i}/{len(TEST_CASES)}] {test_case['name']}...")
        try:
            result = invoke_agent_runtime(agentcore_client, agent_id, test_case['prompt'], session_id)
            response_text = result.get('response', 'Error')
            runtime_sid = result.get('runtime_session_id')
            trace_id = result.get('trace_id')
            
            # Track runtime session ID for observability queries
            if runtime_sid:
                runtime_session_ids.append(runtime_sid)
            
            invocation_results.append({
                "test_case": test_case['name'],
                "prompt": test_case['prompt'],
                "response": str(response_text)[:500],  # Capture more of response
                "runtime_session_id": runtime_sid,
                "trace_id": trace_id,
                "status": "success"
            })
            print(f"          ✓ Success")
            print(f"          Response: {str(response_text)[:150]}{'...' if len(str(response_text)) > 150 else ''}\n")
        except Exception as e:
            print(f"          ✗ Error: {str(e)}\n")
            invocation_results.append({
                "test_case": test_case['name'],
                "error": str(e),
                "status": "failed"
            })
    
    # Retrieve evaluation results using CLI (recommended approach)
    print("[4/4] Running on-demand evaluation via CLI...\n")
    print("      Using: agentcore eval run --agent-id <agent_id> --session-id <session_id> --evaluator <evaluator>\n")
    
    results_summary = {
        "session_id": session_id,
        "agent_id": agent_id,
        "region": region,
        "evaluation_id": "evaluation_evaluation_agent_02-kuaABUAhPM",
        "timestamp": datetime.now().isoformat(),
        "test_cases_count": len(TEST_CASES),
        "invocation_results": invocation_results,
        "evaluator_results": [],
        "runtime_session_ids": runtime_session_ids
    }
    
    try:
        # Use CLI-based evaluation for each runtime session ID
        all_eval_results = []
        
        evaluators = [
            "Builtin.GoalSuccessRate",
            "Builtin.Correctness",
            "Builtin.ToolParameterAccuracy",
            "Builtin.ToolSelectionAccuracy"
        ]
        
        # Set AWS_REGION environment variable for CLI
        env = os.environ.copy()
        env['AWS_REGION'] = region
        
        for idx, rsid in enumerate(runtime_session_ids, 1):
            print(f"      [{idx}/{len(runtime_session_ids)}] Evaluating session {rsid[:8]}...\n")
            
            # Build CLI command with all evaluators
            # CRITICAL: Must include --agent-id parameter
            cmd = ["agentcore", "eval", "run", "--agent-id", agent_id, "--session-id", rsid]
            for evaluator in evaluators:
                cmd.extend(["--evaluator", evaluator])
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
                
                if result.returncode == 0:
                    print(f"        ✓ Evaluation completed\n")
                    print(result.stdout)
                    
                    # Parse and store results
                    all_eval_results.append({
                        "session_id": rsid,
                        "raw_output": result.stdout
                    })
                else:
                    error_msg = result.stderr if result.stderr else result.stdout
                    print(f"        ✗ Evaluation failed: {error_msg[:200]}\n")
                    
                    # Store error for debugging
                    all_eval_results.append({
                        "session_id": rsid,
                        "error": error_msg,
                        "returncode": result.returncode
                    })
            
            except subprocess.TimeoutExpired:
                print(f"        ✗ Evaluation timed out (60s)\n")
            except FileNotFoundError:
                print(f"        ✗ agentcore CLI not found in PATH\n")
                print("        Make sure bedrock-agentcore-starter-toolkit is installed:\n")
                print("        pip install bedrock-agentcore-starter-toolkit\n")
            except Exception as e:
                print(f"        ✗ Error: {str(e)}\n")
        
        # Display evaluation results
        if all_eval_results:
            print("\n" + "=" * 80)
            print(" Evaluation Results")
            print("=" * 80 + "\n")
            
            for result in all_eval_results:
                results_summary["evaluator_results"].append(result)
                print(f"Session: {result.get('session_id', 'N/A')[:8]}...")
                print(f"Output:\n{result.get('raw_output', 'No output')}\n")
        else:
            print("      INFO: No evaluation results found yet.")
            print("      Try running: agentcore eval run --session-id <session_id> --evaluator Builtin.GoalSuccessRate\n")
    
    except Exception as e:
        print(f"      Note: {str(e)}")
        print("      This is normal - online evaluations run continuously.")
        print("      Results will be available in the AgentCore dashboard.\n")
    
    # Save results to file
    print("[SAVE] Saving invocation and evaluation results...\n")
    output_file = f"evaluation_results_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results_summary, f, indent=2, default=str)
    
    print(f"✓ Results saved to: {output_file}\n")
    
    # Print summary
    print("=" * 80)
    print(" Evaluation Summary")
    print("=" * 80)
    print(f" Session:           {session_id}")
    print(f" Evaluation ID:     evaluation_evaluation_agent_02-kuaABUAhPM")
    print(f" Test Cases:        {len(TEST_CASES)}")
    print(f" Successful Calls:  {sum(1 for r in invocation_results if r['status'] == 'success')}")
    print(f" Results file:      {output_file}")
    print("=" * 80 + "\n")
    
    return results_summary


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    try:
        results = run_evaluation()
        print("✓ Agent invocation and evaluation complete!\n")
        print("Next steps:")
        print("  1. Review the invocation results above")
        print("  2. Check the evaluation_results_*.json file")
        print("  3. View AgentCore dashboard for real-time online evaluation metrics")
        print("  4. Use insights to improve agent tool selection and parameter accuracy")
        print("\nOnline Evaluation:")
        print("  - Runs continuously in the background")
        print("  - Processes traces based on configured sampling rate (10%)")
        print("  - Applies built-in evaluators to assess quality")
        print("  - Results visible in AgentCore Observability dashboard")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Evaluation cancelled by user")
    except Exception as e:
        print(f"\n\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)


