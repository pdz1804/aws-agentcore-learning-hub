# AgentCore Evaluation Agent 02

A production-ready agent implementation using **BedrockAgentCoreApp** framework with comprehensive **observability** and **evaluation** capabilities using AWS AgentCore built-in evaluators.

---

## ⚠️ CRITICAL KNOWN ISSUE: Evaluation Spans Not Accessible

**Status**: Agent is fully functional ✅ | Evaluation service is BLOCKED ❌

**Issue**: The evaluation service **cannot find or access X-Ray spans** from agent invocations, preventing on-demand evaluation from working.

**Error Message**: 
```
Error: No spans found for session {session_id}
```

**What's Working**:
- ✅ Agent invocations execute successfully
- ✅ CloudWatch logs are being written
- ✅ OpenTelemetry instrumentation is active
- ✅ Responses are complete and correct

**What's NOT Working**:
- ❌ `agentcore eval run` CLI fails with "No spans found"
- ❌ Python SDK evaluation fails with "No spans found"
- ❌ X-Ray integration misconfigured (multiple broken delivery destinations)

**Root Cause**: AWS infrastructure configuration issue, not code issue
- X-Ray delivery destinations have empty/invalid resource ARNs
- Traces generated but not indexed/queryable by session_id
- Likely requires AWS support or manual AWS configuration

**Impact**: 
- Built-in evaluators cannot run via `agentcore eval run`
- Manual evaluation workarounds available (see docs below)
- Agent responses can still be manually evaluated against criteria

**See**: [EVALUATION_STATUS_REPORT.md](EVALUATION_STATUS_REPORT.md) for detailed diagnostics and workarounds.

---

## 🎯 Features

### ✅ BedrockAgentCoreApp Framework
- Uses the new `BedrockAgentCoreApp` instead of FastAPI
- Simplified deployment and runtime management
- Native AgentCore integration

### 📊 Observability
- **Tracing**: Full distributed tracing for request flows
- **Metrics**: Performance and usage metrics collection
- **Logging**: Structured logging with configurable levels
- **User/Session Tracking**: Track user_id and session_id across all invocations

### 🔍 Built-in Evaluators
The agent is configured with 13 built-in evaluators across 4 categories:

#### Response Quality (8 evaluators)
- `Builtin.Correctness` - Factual accuracy evaluation
- `Builtin.Faithfulness` - Context-supported information
- `Builtin.Helpfulness` - User value assessment
- `Builtin.ResponseRelevance` - Query-response alignment
- `Builtin.Conciseness` - Brevity without information loss
- `Builtin.Coherence` - Logical structure evaluation
- `Builtin.InstructionFollowing` - Instruction adherence
- `Builtin.Refusal` - Detection of evasive responses

#### Task Completion (1 evaluator)
- `Builtin.GoalSuccessRate` - Goal achievement evaluation

#### Tool Level (2 evaluators)
- `Builtin.ToolSelectionAccuracy` - Appropriate tool selection
- `Builtin.ToolParameterAccuracy` - Parameter extraction accuracy

#### Safety (2 evaluators)
- `Builtin.Harmfulness` - Harmful content detection
- `Builtin.Stereotyping` - Generalization detection

### 🔧 MCP Integration
- Supports both HTTP and AgentCore Runtime MCP servers
- Auto-discovery of MCP tools
- Seamless tool invocation through Strands framework

---

## 📁 File Structure

```
evaluation_02/
├── agent.py                    # Main agent using BedrockAgentCoreApp
├── evaluation_config.py        # Built-in evaluators configuration
├── run_evaluation.py           # Evaluation runner script
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container image definition
├── test_local.py              # Local testing with user/session tracking
├── test_deployed.py           # Test deployed agent on AgentCore
├── 1_test_local.ps1           # PowerShell: Test locally
├── 2_build_push.ps1           # PowerShell: Build & push to ECR
├── 3_deploy_runtime.ps1       # PowerShell: Deploy to AgentCore
├── 4_run_evaluation.ps1       # PowerShell: Run evaluation
└── README.md                  # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker
- AWS CLI configured
- AWS account with AgentCore access
- MCP server deployed (optional for testing)

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Configure Environment
Create a `.env` file or set environment variables:

```bash
# MCP Server Configuration
USE_MCP_ARN=true
MCP_SERVER_ARN=arn:aws:bedrock-agentcore:us-west-2:ACCOUNT_ID:runtime/mcp_server_name

# Or for HTTP MCP server
USE_MCP_ARN=false
MCP_SERVER_URL=http://localhost:8000/mcp

# Default User/Session for Local Testing
DEFAULT_USER_ID=test-user-001
DEFAULT_SESSION_ID=test-session-001
```

### 3️⃣ Test Locally
```powershell
.\1_test_local.ps1
```

This will:
- Set up local testing environment
- Run test cases with different user_id and session_id
- Generate test results JSON file
- Validate observability tracking

### 4️⃣ Build and Push Docker Image
```powershell
.\2_build_push.ps1
```

This will:
- Authenticate to Amazon ECR
- Create ECR repository (if needed)
- Build Docker image
- Push to ECR

### 5️⃣ Deploy to AgentCore Runtime
```powershell
.\3_deploy_runtime.ps1
```

This will:
- Generate deployment configuration with observability and evaluation
- Enable all 13 built-in evaluators
- Create deployment manifest
- Provide AWS CLI command for deployment

### 6️⃣ Run Evaluation
```powershell
.\4_run_evaluation.ps1
```

This will:
- Execute test cases against the deployed agent
- Run all built-in evaluators
- Generate comprehensive evaluation report
- Save metrics to JSON file

---

## 📖 Usage Guide

### Invoking the Agent

#### Local Invocation
```python
from agent import agent_invocation

payload = {
    "prompt": "What is quantum computing?",
    "user_id": "user-123",
    "session_id": "session-456"
}

context = MockContext()  # For local testing
result = agent_invocation(payload, context)
```

#### AgentCore Runtime Invocation
```python
import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-west-2')

response = client.invoke_runtime(
    runtimeIdentifier='arn:aws:bedrock-agentcore:...:runtime/evaluation-agent-02',
    qualifier='DEFAULT',
    contentType='application/json',
    body=json.dumps({
        "prompt": "What is quantum computing?",
        "user_id": "user-123",
        "session_id": "session-456"
    })
)

result = json.loads(response['body'].read())
```

### User and Session Tracking

The agent automatically tracks `user_id` and `session_id` from:
1. Request payload (`payload.get("user_id")`)
2. Context object (`context.get("user_id")`)
3. Environment defaults (`DEFAULT_USER_ID`)

These IDs are:
- Logged for each invocation
- Added to trace attributes for observability
- Included in response metadata
- Used for evaluation tracking

### Viewing Evaluation Results

After running evaluation:
```python
import json

# Load evaluation report
with open('evaluation_report_20260201_120000.json') as f:
    report = json.load(f)

# View summary
print(report['summary'])

# View evaluator metrics
for evaluator, metrics in report['evaluator_metrics'].items():
    print(f"{evaluator}: {metrics['average_score']:.2f}")
```

### Customizing Evaluators

Edit `evaluation_config.py` to enable/disable evaluators:

```python
RESPONSE_QUALITY_EVALUATORS = [
    {
        "name": "Builtin.Correctness",
        "description": "...",
        "enabled": True  # Set to False to disable
    },
    # ...
]
```

---

## 🔧 Configuration Options

### Agent Configuration (`agent.py`)

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_MCP_ARN` | `true` | Use AgentCore Runtime MCP (true) or HTTP (false) |
| `MCP_SERVER_URL` | `http://localhost:8000/mcp` | HTTP MCP server endpoint |
| `MCP_SERVER_ARN` | (see code) | AgentCore Runtime MCP ARN |
| `DEFAULT_USER_ID` | `test-user-001` | Default user ID for local testing |
| `DEFAULT_SESSION_ID` | `test-session-001` | Default session ID for local testing |

### Observability Configuration

```python
observability_config = ObservabilityConfig(
    enabled=True,
    trace_enabled=True,
    metrics_enabled=True,
    log_level="INFO"  # DEBUG, INFO, WARNING, ERROR
)
```

### Deployment Configuration (`3_deploy_runtime.ps1`)

Key configuration in deployment:
- **Observability**: Tracing, metrics, logging all enabled
- **Evaluation**: All 13 built-in evaluators enabled
- **Environment**: MCP server ARN, user/session defaults

---

## 📊 Evaluation Metrics

### Response Quality Metrics
Evaluates the quality of agent responses:
- Correctness, Faithfulness, Helpfulness
- Relevance, Conciseness, Coherence
- Instruction following, Refusal detection

### Task Completion Metrics
Measures goal achievement:
- Success rate in meeting user objectives

### Tool Usage Metrics
Assesses tool interaction:
- Tool selection accuracy
- Parameter extraction precision

### Safety Metrics
Ensures responsible AI:
- Harmful content detection
- Stereotype identification

### Evaluation Report Format
```json
{
  "summary": {
    "total_test_cases": 4,
    "total_evaluators": 13,
    "timestamp": "2026-02-01T12:00:00"
  },
  "evaluator_metrics": {
    "Builtin.Correctness": {
      "average_score": 0.92,
      "min_score": 0.85,
      "max_score": 0.98,
      "passed_count": 4,
      "total_count": 4
    },
    // ... other evaluators
  },
  "detailed_results": [
    // ... per-test-case results
  ]
}
```

---

## 🔍 Observability Features

### Tracing
- Distributed tracing for all requests
- User/session ID in trace context
- Tool invocation tracking
- Error propagation

### Metrics
- Request count and latency
- Response length distribution
- Error rates by type
- Tool usage statistics

### Logging
Structured logs include:
```
[INVOCATION]
User ID:     user-123
Session ID:  session-456
Prompt:      What is quantum computing?
[RESPONSE]
...
```

---

## 🧪 Testing

### Test Scenarios

**test_local.py** includes:
1. Factual queries (different users)
2. Tool usage requests
3. Explanatory questions
4. Safety tests (refusal scenarios)

**test_deployed.py** validates:
- AgentCore Runtime integration
- User/session tracking in production
- Response format and metadata

### Running Tests

```powershell
# Local testing
python test_local.py

# Or use PowerShell script
.\1_test_local.ps1

# Deployed testing
python test_deployed.py
```

---

## 📈 Monitoring

### CloudWatch Integration
The agent automatically sends:
- Logs to CloudWatch Logs
- Metrics to CloudWatch Metrics
- Traces to AWS X-Ray (if configured)

### Key Metrics to Monitor
- Invocation count per user/session
- Average response time
- Evaluation scores over time
- Error rates

### Viewing Traces
```bash
# Using AWS X-Ray Console
# Filter by user_id or session_id attributes
```

---

## 🔒 Security Considerations

### User ID and Session ID
- Never expose sensitive user information
- Use anonymized or hashed IDs when possible
- Implement proper access controls

### Built-in Safety Evaluators
- `Builtin.Harmfulness` detects harmful content
- `Builtin.Stereotyping` identifies biased responses
- Review safety metrics regularly

### MCP Server Security
- Use IAM authentication for AgentCore Runtime MCP
- Implement least-privilege access
- Rotate credentials regularly

---

## 🛠️ Troubleshooting

### Common Issues

#### Agent fails to connect to MCP server
```
Solution: Verify MCP_SERVER_ARN or MCP_SERVER_URL
Check: aws bedrock-agentcore list-runtimes
```

#### Missing user_id or session_id in traces
```
Solution: Ensure payload includes user_id and session_id
Or set DEFAULT_USER_ID and DEFAULT_SESSION_ID environment variables
```

#### Evaluation metrics show low scores
```
Solution: 
1. Review detailed_results in evaluation report
2. Check which evaluators are failing
3. Iterate on agent prompts/configuration
4. Re-run evaluation to measure improvement
```

#### Docker build fails
```
Solution: Check requirements.txt has all dependencies
Verify: Python version 3.11+ in Dockerfile
```

---

## 📚 Additional Resources

### Documentation
- [AWS AgentCore Documentation](https://docs.aws.amazon.com/bedrock/agentcore)
- [Strands AI Framework](https://github.com/awslabs/strands-ai)
- [MCP Protocol](https://modelcontextprotocol.io)

### Examples
- [AgentCore Samples](https://github.com/awslabs/amazon-bedrock-agentcore-samples)
- [Strands Agent Examples](https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/03-integrations/agentic-frameworks/strands-agents)

---

## 🤝 Contributing

When extending this agent:
1. Add new test cases to `test_local.py` and `test_deployed.py`
2. Update evaluation configuration if adding custom evaluators
3. Document changes in this README
4. Test locally before deploying to AgentCore

---

## 📝 License

See LICENSE file in the root of the repository.

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review AWS AgentCore documentation
3. Consult team documentation

---

**Last Updated**: February 2026  
**Version**: 1.0.0  
**Framework**: BedrockAgentCoreApp with Built-in Evaluators
