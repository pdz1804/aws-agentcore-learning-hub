#!/usr/bin/env pwsh
# ============================================================================
# Build and Test Docker Image Locally
# ============================================================================

Write-Host ""
Write-Host "=========================================================================="
Write-Host " Build & Test Docker Image Locally"
Write-Host "=========================================================================="

$IMAGE = "agent-pdz-01:local-test"

# Check Docker
Write-Host ""
Write-Host "[Prerequisites] Checking Docker..."
docker ps 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERROR - Docker not running. Please start Docker Desktop."
    exit 1
}
Write-Host "   SUCCESS - Docker running"

# Check AWS credentials
Write-Host ""
Write-Host "[Prerequisites] Checking AWS credentials..."
try {
    $credentials = aws sts get-caller-identity --output json | ConvertFrom-Json
    Write-Host "   SUCCESS - AWS credentials found!"
    Write-Host "   Account: $($credentials.Account)"
}
catch {
    Write-Host "   FAILED - No AWS credentials configured!"
    Write-Host "   Run: aws configure"
    exit 1
}

# Build
Write-Host ""
Write-Host "=========================================================================="
Write-Host " [Step 1/3] Building ARM64 Image"
Write-Host "=========================================================================="
Write-Host "   Image: $IMAGE"
Write-Host ""

docker buildx build --platform linux/arm64 -t $IMAGE --load .

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "   FAILED - Build failed!"
    exit 1
}

Write-Host ""
Write-Host "   SUCCESS - Image built!"

# Clean up old container
Write-Host ""
Write-Host "=========================================================================="
Write-Host " [Step 2/3] Starting Container with AWS Credentials"
Write-Host "=========================================================================="

docker stop agent-pdz-01-test 2>$null | Out-Null
docker rm agent-pdz-01-test 2>$null | Out-Null

# Start container with AWS credentials mounted
$awsDir = "$HOME/.aws"
docker run `
  --platform linux/arm64 `
  -p 8080:8080 `
  -v "${awsDir}:/root/.aws:ro" `
  -e AWS_REGION=ap-southeast-1 `
  --name agent-pdz-01-test `
  -d `
  $IMAGE | Out-Null

if ($LASTEXITCODE -ne 0) {
    Write-Host "   FAILED - Could not start container"
    exit 1
}

Write-Host "   SUCCESS - Container started with AWS credentials!"
Start-Sleep -Seconds 3

# Test
Write-Host ""
Write-Host "=========================================================================="
Write-Host " [Step 3/3] Testing Agent"
Write-Host "=========================================================================="

Write-Host ""
Write-Host "[Test 1/2] GET /ping"
try {
    $response = Invoke-WebRequest -Uri http://localhost:8080/ping -UseBasicParsing
    Write-Host "   Status: $($response.StatusCode)"
    Write-Host "   Response: $($response.Content)"
}
catch {
    Write-Host "   FAILED: $_"
}

Write-Host ""
Write-Host "[Test 2/2] POST /invocations"
try {
    $body = @{prompt = "Hello! What can you do?"} | ConvertTo-Json
    $response = Invoke-WebRequest -Uri http://localhost:8080/invocations `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -UseBasicParsing
    
    Write-Host "   Status: $($response.StatusCode)"
    Write-Host "   Response: $($response.Content.Substring(0, 200))..."
}
catch {
    Write-Host "   FAILED: $_"
}

# Show logs
Write-Host ""
Write-Host "=========================================================================="
Write-Host " Container Logs"
Write-Host "=========================================================================="
Write-Host ""

docker logs agent-pdz-01-test

Write-Host ""
Write-Host "=========================================================================="
Write-Host " SUCCESS - Local Test Complete"
Write-Host "=========================================================================="
Write-Host ""
Write-Host "Container running at http://localhost:8080"
Write-Host ""
Write-Host "To clean up:"
Write-Host "   docker stop agent-pdz-01-test"
Write-Host "   docker rm agent-pdz-01-test"
Write-Host ""
Write-Host "Next step: Push to ECR"
Write-Host "   Run: .\2_push_to_ecr.ps1"
Write-Host ""
Write-Host "=========================================================================="
Write-Host ""
