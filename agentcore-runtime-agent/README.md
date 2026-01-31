# Agent PDZ-01 - Amazon Bedrock AgentCore Runtime

A production-ready AI agent for Amazon Bedrock AgentCore Runtime using FastAPI and Strands Agent SDK.

## 📁 Project Structure

```
agentcore-runtime-agent/
├── agent_pdz_01/                    # Main agent application
│   ├── agent.py                     # FastAPI application (required)
│   ├── pyproject.toml               # Python project config
│   ├── uv.lock                      # Dependency lock file
│   ├── Dockerfile                   # ARM64 Docker container
│   ├── .dockerignore                # Docker build exclusions
│   ├── .gitignore                   # Git exclusions
│   ├── README.md                    # Agent documentation
│   ├── 1_build_local.ps1            # Build Docker image locally
│   ├── 2_push_to_ecr.ps1            # Push to ECR
│   ├── 3_deploy_runtime.ps1         # Deploy to AWS AgentCore
│   ├── 4_invoke_agent.ps1           # Invoke agent from AWS
│   └── test_local_invocation.ps1    # Test agent locally
├── invoke_agent_local.ps1           # Start server and test locally
├── invoke_agent_runtime.py          # Invoke agent from AWS
├── requirements.txt                 # Python dependencies
└── README.md                        # This file

```

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (with ARM64 support)
- AWS CLI v2 configured with credentials
- PowerShell 7+
- Python 3.11+
- `uv` package manager

### 1. Build Docker Image (Locally)

```powershell
cd agent_pdz_01
.\1_build_local.ps1
```

This will:
- Build ARM64 Docker image
- Mount your AWS credentials
- Test `/ping` and `/invocations` endpoints locally

### 2. Push to ECR

```powershell
.\2_push_to_ecr.ps1
```

This will:
- Create ECR repository if needed
- Login to ECR
- Build and push the image for ARM64

### 3. Deploy to AWS AgentCore Runtime

```powershell
.\3_deploy_runtime.ps1
```

This will:
- Deploy the agent runtime to AWS
- Output the runtime ARN
- Example: `arn:aws:bedrock-agentcore:ap-southeast-1:381492273521:runtime/agent_pdz_01-cQUpBd59IF`

### 4. Invoke the Agent from AWS

```powershell
.\4_invoke_agent.ps1
```

Or from outside the folder:

```powershell
uv run invoke_agent_runtime.py "Your prompt here"
```

Example:
```powershell
uv run invoke_agent_runtime.py "What can you help me with?"
```

## 🧪 Testing

### Quick Test (Recommended)

Start server and run all tests:

```bash
python invoke_agent_local.py
```

This will:
1. Check Docker, uv, and other prerequisites
2. Start the FastAPI server
3. Test `/ping` endpoint
4. Test `/invocations` with sample prompt
5. Test multiple prompts
6. Keep server running (Ctrl+C to stop)

### Test Locally with Docker

Build and test the Docker image:

```powershell
cd agent_pdz_01
.\1_build_local.ps1
.\test_local_invocation.ps1
```

### Test with Multiple Payloads (PowerShell)

```powershell
cd agent_pdz_01
.\test_local_invocation.ps1
```

This tests:
1. AWS format: `{"prompt": "..."}`
2. Direct format: `{"prompt": "..."}`
3. With context and session
4. Raw JSON simulation

### Manual Testing

Start just the server:

```bash
cd agent_pdz_01
uv run uvicorn agent:app --host 0.0.0.0 --port 8080
```

Then in another terminal, test endpoints:

```bash
# Test ping
curl http://localhost:8080/ping

# Test invocation
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello agent!"}'
```

Or use Python:

```python
import requests

# Test ping
response = requests.get('http://localhost:8080/ping')
print(response.json())

# Test invocation
payload = {"prompt": "What can you help me with?"}
response = requests.post(
    'http://localhost:8080/invocations',
    json=payload
)
print(response.json())
```

## 📋 API Endpoints

### `/ping` (GET)
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### `/invocations` (POST)
Main agent invocation endpoint.

**Request:**
```json
{
  "prompt": "Your message here"
}
```

**Response:**
```json
{
  "output": {
    "message": {
      "role": "assistant",
      "content": [
        {
          "text": "Agent response here"
        }
      ]
    },
    "timestamp": "2026-01-31T11:05:35.912095"
  }
}
```

## 🔍 CloudWatch Logs

View agent logs:

```powershell
$AGENT_NAME = "agent_pdz_01"
aws logs tail /aws/bedrock-agentcore/runtime/$AGENT_NAME --follow --region ap-southeast-1
```

Check specific invocation:

```powershell
aws logs tail /aws/bedrock-agentcore/runtime/agent_pdz_01 --filter-pattern "[INVOCATION]" --region ap-southeast-1
```

## 🛠️ Troubleshooting

### Docker Build Issues

```powershell
# Check Docker is running
docker ps

# View build logs
docker buildx build --platform linux/arm64 -t agent-pdz-01 --load . --progress=plain
```

### ECR Login Failed (400 Bad Request)

This is a known issue with root AWS credentials. The script will continue and Docker may use cached credentials.

```powershell
# Manually login if needed
$pass = aws ecr get-login-password --region ap-southeast-1
$pass.Trim() | docker login --username AWS --password-stdin 381492273521.dkr.ecr.ap-southeast-1.amazonaws.com
```

### Agent Runtime Not Responding

1. Check agent status:
   ```powershell
   aws bedrock-agentcore-control list-agent-runtimes --region ap-southeast-1
   ```

2. Check CloudWatch logs for errors:
   ```powershell
   aws logs tail /aws/bedrock-agentcore/runtime/agent_pdz_01 --region ap-southeast-1
   ```

3. Verify IAM role has correct permissions

### Empty Response from Agent

Check the detailed logs in CloudWatch:

```
[STRANDS TEXT EXTRACTED] ...
[RESPONSE TEXT] ...
[OUTPUT OBJECT] ...
```

## 📝 Environment Variables

### Local Testing

```powershell
$env:AWS_REGION = "ap-southeast-1"
$env:AWS_ACCESS_KEY_ID = "your-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret"
```

### Docker

The Dockerfile mounts `~/.aws` directory for credentials in local testing.

For AWS deployment, credentials are provided via IAM role automatically.

## 🔐 Security Notes

- **Never** commit AWS credentials to repository
- `.gitignore` excludes credential files
- Docker uses read-only mount for `~/.aws`
- IAM role provides temporary credentials in production

## 📚 References

- [AWS Bedrock AgentCore Runtime](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [Strands Agent SDK](https://github.com/strands-ai/agent)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)

## 💡 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 AWS Bedrock AgentCore                    │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Agent PDZ-01 (ECS Container)             │   │
│  │                                                   │   │
│  │  ┌──────────────────────────────────────────┐   │   │
│  │  │       FastAPI Server (Port 8080)        │   │   │
│  │  │                                          │   │   │
│  │  │  • GET /ping -> Health check            │   │   │
│  │  │  • POST /invocations -> Process prompt  │   │   │
│  │  └──────────────────────────────────────────┘   │   │
│  │                    ▲                             │   │
│  │                    │                             │   │
│  │  ┌──────────────────┴──────────────────────┐   │   │
│  │  │     Strands Agent (Claude)              │   │   │
│  │  │                                          │   │   │
│  │  │  • Processes user prompts                │   │   │
│  │  │  • Uses AWS credentials (via IAM role) │   │   │
│  │  │  • Returns structured responses         │   │   │
│  │  └──────────────────────────────────────────┘   │   │
│  │                                                   │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## 📖 Usage Examples

### Example 1: Invoke from Command Line

```bash
# Simple question
python invoke_agent_runtime.py "What is machine learning?"

# With special characters
python invoke_agent_runtime.py "Explain quantum computing in simple terms"
```

### Example 2: Invoke from Python Script

```python
import json
import boto3

AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:ap-southeast-1:381492273521:runtime/agent_pdz_01-cQUpBd59IF"

client = boto3.client('bedrock-agentcore', region_name='ap-southeast-1')

# Send prompt
prompt = "What can you help me with?"
payload = json.dumps({"prompt": prompt})

response = client.invoke_agent_runtime(
    agentRuntimeArn=AGENT_RUNTIME_ARN,
    runtimeSessionId='session-' + str(uuid.uuid4()),
    payload=payload
)

# Parse response
response_body = response['response'].read()
response_data = json.loads(response_body)
print(response_data)
```

### Example 3: Test Locally

```bash
# Start server and run all tests
python invoke_agent_local.py

# Output shows:
# - Prerequisites check
# - Server startup
# - Ping test
# - Invocation test
# - Multiple prompts test
```

### Example 4: Continuous Interaction

```python
import requests
import json

prompts = [
    "Hello! What are you?",
    "Can you help me learn Python?",
    "Tell me about machine learning",
]

for prompt in prompts:
    response = requests.post(
        'http://localhost:8080/invocations',
        json={"prompt": prompt}
    )
    data = response.json()
    message = data['output']['message']
    text = message['content'][0]['text']
    print(f"Q: {prompt}")
    print(f"A: {text}\n")
```

## 🎯 Next Steps

1. **Monitor Performance**: Check CloudWatch metrics
2. **Add Tools/Integrations**: Extend Strands agent with custom tools
3. **Production Hardening**: Add error handling, retry logic, rate limiting
4. **Cost Optimization**: Review CloudWatch logs and optimize model usage

---

**Agent Version:** 2.0.0  
**Last Updated:** 2026-01-31  
**Status:** ✅ Production Ready
