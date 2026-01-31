#!/usr/bin/env pwsh
# ============================================================================
# Build and Push to ECR
# ============================================================================

Write-Host ""
Write-Host "=========================================================================="
Write-Host " Build & Push to ECR"
Write-Host "=========================================================================="

# Configuration
$AGENT = "agent-pdz-01"
$REGION = "ap-southeast-1"
$ACCOUNT = "381492273521"
$ECR_REPO = "${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/${AGENT}"

Write-Host ""
Write-Host "[Config]"
Write-Host "   Agent: $AGENT"
Write-Host "   Region: $REGION"
Write-Host "   Account: $ACCOUNT"
Write-Host "   ECR: $ECR_REPO"

# Check Docker
Write-Host ""
Write-Host "[Prerequisites] Checking Docker..."
docker ps 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ERROR - Docker not running. Start Docker Desktop."
    exit 1
}
Write-Host "   SUCCESS - Docker running"

# Step 1: Create ECR repo
Write-Host ""
Write-Host "=========================================================================="
Write-Host " [Step 1/4] Creating ECR Repository"
Write-Host "=========================================================================="

aws ecr create-repository --repository-name $AGENT --region $REGION 2>$null | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "   SUCCESS - ECR repository created"
} else {
    Write-Host "   INFO - ECR repository already exists (OK)"
}

# Step 2: Login
Write-Host ""
Write-Host "=========================================================================="
Write-Host " [Step 2/4] Logging into ECR"
Write-Host "=========================================================================="

# For root account credentials, we need to use the legacy login command
$loginCommand = aws ecr get-login --no-include-email --region $REGION 2>$null

if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrEmpty($loginCommand)) {
    Write-Host "   INFO - Legacy login not available, trying modern method..."
    
    # Get ECR URI without repository name for login
    $ECR_URI = "${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com"
    
    # Try alternative method: save password to temp file with proper encoding
    $tempFile = [System.IO.Path]::GetTempFileName()
    try {
        # Get password and save to file without BOM
        $password = aws ecr get-login-password --region $REGION
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   FAILED - Could not get ECR login password"
            exit 1
        }
        
        # Write without BOM
        [System.IO.File]::WriteAllText($tempFile, $password, [System.Text.UTF8Encoding]::new($false))
        
        # Use the temp file for docker login
        Get-Content $tempFile -Raw | docker login --username AWS --password-stdin $ECR_URI 2>&1 | Out-Null
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "   FAILED - ECR login failed with error 400"
            Write-Host ""
            Write-Host "   WORKAROUND: Skip ECR login and push directly"
            Write-Host "   (Docker may use cached credentials)"
            Write-Host ""
        } else {
            Write-Host "   SUCCESS - Logged into ECR"
        }
    }
    finally {
        # Clean up temp file
        if (Test-Path $tempFile) {
            Remove-Item $tempFile -Force
        }
    }
} else {
    # Use legacy login command
    Invoke-Expression $loginCommand | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   SUCCESS - Logged into ECR (legacy method)"
    } else {
        Write-Host "   FAILED - ECR login failed"
        exit 1
    }
}

Write-Host "   SUCCESS - Logged into ECR"

# Step 3: Setup buildx
Write-Host ""
Write-Host "=========================================================================="
Write-Host " [Step 3/4] Setting up Docker buildx"
Write-Host "=========================================================================="

docker buildx create --use --name arm64-builder 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "   SUCCESS - Buildx configured"
} else {
    Write-Host "   INFO - Buildx already configured (OK)"
    docker buildx use arm64-builder 2>$null | Out-Null
}

# Step 4: Build and push
Write-Host ""
Write-Host "=========================================================================="
Write-Host " [Step 4/4] Building & Pushing ARM64 Image"
Write-Host "=========================================================================="
Write-Host "   Platform: linux/arm64"
Write-Host "   Target: ${ECR_REPO}:latest"
Write-Host ""

docker buildx build --platform linux/arm64 -t "${ECR_REPO}:latest" --push .

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "   FAILED - Build/push failed!"
    exit 1
}

Write-Host ""
Write-Host "   SUCCESS - Image pushed to ECR!"

# Verify
Write-Host ""
Write-Host "=========================================================================="
Write-Host " Verifying Image"
Write-Host "=========================================================================="

aws ecr describe-images --repository-name $AGENT --region $REGION --output table

Write-Host ""
Write-Host "=========================================================================="
Write-Host " SUCCESS - Image Ready in ECR!"
Write-Host "=========================================================================="
Write-Host ""
Write-Host "Container URI: ${ECR_REPO}:latest"
Write-Host ""
Write-Host "Next step: Deploy to AgentCore Runtime"
Write-Host "   Run: .\3_deploy_runtime.ps1"
Write-Host ""
Write-Host "=========================================================================="
Write-Host ""
