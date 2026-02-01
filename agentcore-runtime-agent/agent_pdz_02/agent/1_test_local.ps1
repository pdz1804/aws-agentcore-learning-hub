#!/usr/bin/env pwsh
# Test Agent locally

Write-Host "=========================================================================="
Write-Host " Agent - Local Test"
Write-Host "=========================================================================="

$IMAGE = "agent-pdz-02:local"

Write-Host "`n[1/3] Building image..."
docker buildx build --platform linux/arm64 -t $IMAGE --load .

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR - Build failed"
    exit 1
}

Write-Host "`n[2/3] Starting container..."
docker stop agent-test 2>$null | Out-Null
docker rm agent-test 2>$null | Out-Null

$awsDir = "$HOME/.aws"
$mcpServerIp = docker inspect mcp-server-test --format '{{.NetworkSettings.IPAddress}}' 2>$null

if ($mcpServerIp) {
    Write-Host "  MCP server found at: $mcpServerIp - using HTTP (USE_MCP_ARN=false)"
    docker run --platform linux/arm64 -p 8080:8080 -e USE_MCP_ARN=false -e MCP_SERVER_URL="http://${mcpServerIp}:8000/mcp" -v "${awsDir}:/root/.aws:ro" -e AWS_REGION=us-east-1 --name agent-test -d $IMAGE | Out-Null
} else {
    Write-Host "  MCP server not running - using default (USE_MCP_ARN=true, AgentCore Runtime MCP)"
    docker run --platform linux/arm64 -p 8080:8080 -v "${awsDir}:/root/.aws:ro" -e AWS_REGION=us-west-2 --name agent-test -d $IMAGE | Out-Null
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR - Container start failed"
    exit 1
}

Write-Host "Waiting for server to be ready..."
Start-Sleep -Seconds 15

Write-Host "`n[3/3] Testing agent..."
python test_local.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nShowing container logs:"
    docker logs agent-test
}

Write-Host "`n=========================================================================="
Write-Host " SUCCESS - Agent is running at http://localhost:8080"
Write-Host "=========================================================================="
Write-Host "`nTo stop: docker stop agent-test"
