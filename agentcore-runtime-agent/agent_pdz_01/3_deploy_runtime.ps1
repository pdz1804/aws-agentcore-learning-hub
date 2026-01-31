#!/usr/bin/env pwsh
# ============================================================================
# Agent PDZ-01 - Deploy to AgentCore Runtime
# ============================================================================

Write-Host ""
Write-Host "=========================================================================="
Write-Host " Agent PDZ-01 - Deploy to AgentCore Runtime"
Write-Host "=========================================================================="

# Configuration
$AGENT_NAME = "agent_pdz_01"
$REGION = "ap-southeast-1"
$ACCOUNT_ID = "381492273521"
$CONTAINER_URI = "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/agent-pdz-01:latest"
$ROLE_ARN = "arn:aws:iam::${ACCOUNT_ID}:role/AgentRuntimeRole"

Write-Host ""
Write-Host "[Config]"
Write-Host "   Agent Name: $AGENT_NAME"
Write-Host "   Region: $REGION"
Write-Host "   Container: $CONTAINER_URI"
Write-Host "   Role: $ROLE_ARN"

Write-Host ""
Write-Host "[Important] Make sure:"
Write-Host "   1. Image is pushed to ECR (run .\2_push_to_ecr.ps1)"
Write-Host "   2. IAM role exists: $ROLE_ARN"
Write-Host "   3. AWS credentials are configured"
Write-Host ""

$confirmation = Read-Host "Continue with deployment? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Host ""
    Write-Host "   Deployment cancelled."
    exit 0
}

# Deploy
Write-Host ""
Write-Host "=========================================================================="
Write-Host " Creating Agent Runtime..."
Write-Host "=========================================================================="

# Create JSON files for parameters
$artifactJsonFile = Join-Path $env:TEMP "artifact.json"
$networkJsonFile = Join-Path $env:TEMP "network.json"

try {
    # Write artifact JSON to file (UTF8 without BOM)
    $artifactJson = @"
{
    "containerConfiguration": {
        "containerUri": "$CONTAINER_URI"
    }
}
"@
    [System.IO.File]::WriteAllText($artifactJsonFile, $artifactJson, [System.Text.UTF8Encoding]::new($false))
    
    # Write network JSON to file (UTF8 without BOM)
    $networkJson = @"
{
    "networkMode": "PUBLIC"
}
"@
    [System.IO.File]::WriteAllText($networkJsonFile, $networkJson, [System.Text.UTF8Encoding]::new($false))
    
    Write-Host ""
    Write-Host "[Info] Using temporary JSON files for AWS CLI..."
    Write-Host "   Artifact: $artifactJsonFile"
    Write-Host "   Network: $networkJsonFile"
    Write-Host ""
    
    # Call AWS CLI with file:// protocol
    $response = aws bedrock-agentcore-control create-agent-runtime `
        --agent-runtime-name $AGENT_NAME `
        --agent-runtime-artifact "file://$artifactJsonFile" `
        --network-configuration "file://$networkJsonFile" `
        --role-arn $ROLE_ARN `
        --region $REGION `
        --output json
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "   FAILED - Deployment failed!"
        Write-Host ""
        Write-Host "Common issues:"
        Write-Host "   1. IAM role doesn't exist - create it first"
        Write-Host "   2. Insufficient permissions - check IAM policies"
        Write-Host "   3. Agent name already exists - use different name or delete existing"
        Write-Host "   4. Container image not found - verify ECR image exists"
        Write-Host ""
        exit 1
    }
    
    # Parse response
    $result = $response | ConvertFrom-Json
    
    Write-Host ""
    Write-Host "=========================================================================="
    Write-Host " SUCCESS - Agent Runtime Created!"
    Write-Host "=========================================================================="
    Write-Host ""
    Write-Host "Agent Runtime ARN: $($result.agentRuntimeArn)"
    Write-Host "Status: $($result.status)"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "   1. Wait for agent to become ACTIVE (may take a few minutes)"
    Write-Host "   2. Check status:"
    Write-Host "      aws bedrock-agentcore-control get-agent-runtime \"
    Write-Host "        --agent-runtime-arn `"$($result.agentRuntimeArn)`" \"
    Write-Host "        --region $REGION"
    Write-Host "   3. Invoke agent: .\4_invoke_agent.ps1"
    Write-Host ""
    Write-Host "=========================================================================="
    Write-Host ""
}
finally {
    # Clean up temp files
    if (Test-Path $artifactJsonFile) {
        Remove-Item $artifactJsonFile -ErrorAction SilentlyContinue
    }
    if (Test-Path $networkJsonFile) {
        Remove-Item $networkJsonFile -ErrorAction SilentlyContinue
    }
}
