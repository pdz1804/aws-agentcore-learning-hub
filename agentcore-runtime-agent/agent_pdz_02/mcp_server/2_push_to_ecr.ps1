#!/usr/bin/env pwsh
# Push MCP Server to ECR

$AGENT = "mcp-server-pdz-02"
$REGION = "us-west-2"
$ACCOUNT = "381492273521"
$ECR_REPO = "${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/${AGENT}"

Write-Host "=========================================================================="
Write-Host " Push MCP Server to ECR"
Write-Host "=========================================================================="
Write-Host "  Repository: $AGENT"
Write-Host "  Region: $REGION"
Write-Host ""

# Create ECR repo
aws ecr create-repository --repository-name $AGENT --region $REGION 2>$null | Out-Null

# Login to ECR
$password = aws ecr get-login-password --region $REGION
$password | docker login --username AWS --password-stdin "${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com" 2>&1 | Out-Null

# Setup buildx
docker buildx use arm64-builder 2>$null

# Build and push
Write-Host "[Building and pushing...]"
docker buildx build --platform linux/arm64 -t "${ECR_REPO}:latest" --push .

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSUCCESS - Image pushed to: ${ECR_REPO}:latest"
} else {
    Write-Host "`nERROR - Push failed"
    exit 1
}
