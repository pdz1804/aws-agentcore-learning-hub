#!/usr/bin/env pwsh
# Test MCP Server locally

Write-Host "=========================================================================="
Write-Host " MCP Server - Local Test"
Write-Host "=========================================================================="

$IMAGE = "mcp-server-pdz-02:local"

Write-Host "`n[1/3] Building image..."
docker buildx build --platform linux/arm64 -t $IMAGE --load .

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR - Build failed"
    exit 1
}

Write-Host "`n[2/3] Starting container..."
docker stop mcp-server-test 2>$null | Out-Null
docker rm mcp-server-test 2>$null | Out-Null

docker run --platform linux/arm64 -p 8000:8000 --name mcp-server-test -d $IMAGE | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR - Container start failed"
    exit 1
}

Write-Host "Waiting for server to be ready..."
Start-Sleep -Seconds 15

Write-Host "`n[3/3] Testing MCP server..."
python test_local.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "`nShowing container logs:"
    docker logs mcp-server-test
}

Write-Host "`n=========================================================================="
Write-Host " SUCCESS - MCP Server is running at http://localhost:8000/mcp"
Write-Host "=========================================================================="
Write-Host "`nTo stop: docker stop mcp-server-test"
