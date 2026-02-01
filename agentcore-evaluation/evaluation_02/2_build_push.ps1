# Build Docker image and push to ECR
Write-Host "================================" -ForegroundColor Cyan
Write-Host " Build & Push to ECR" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$AWS_REGION = "us-west-2"
$AWS_ACCOUNT_ID = "381492273521"
$ECR_REPOSITORY = "evaluation-agent-02"
$IMAGE_TAG = "latest"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Region:     $AWS_REGION" -ForegroundColor White
Write-Host "  Account ID: $AWS_ACCOUNT_ID" -ForegroundColor White
Write-Host "  Repository: $ECR_REPOSITORY" -ForegroundColor White
Write-Host "  Image Tag:  $IMAGE_TAG" -ForegroundColor White
Write-Host ""

# Step 1: Authenticate Docker to ECR
Write-Host "[1/5] Authenticating to ECR..." -ForegroundColor Yellow
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to authenticate to ECR" -ForegroundColor Red
    exit 1
}
Write-Host "      [OK] Authenticated successfully" -ForegroundColor Green

# Step 2: Create ECR repository if it doesn't exist
Write-Host ""
Write-Host "[2/5] Creating ECR repository (if not exists)..." -ForegroundColor Yellow
aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "      [OK] Repository created" -ForegroundColor Green
}
else {
    Write-Host "      [OK] Repository already exists" -ForegroundColor Green
}

# Step 3: Build Docker image
Write-Host ""
Write-Host "[3/5] Building Docker image for ARM64..." -ForegroundColor Yellow
$ECR_URI = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY`:$IMAGE_TAG"

docker build --platform linux/arm64 -t $ECR_REPOSITORY`:$IMAGE_TAG .

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build Docker image" -ForegroundColor Red
    exit 1
}
Write-Host "      [OK] Image built successfully" -ForegroundColor Green

# Step 4: Tag the image
Write-Host ""
Write-Host "[4/5] Tagging image..." -ForegroundColor Yellow
docker tag $ECR_REPOSITORY`:$IMAGE_TAG $ECR_URI

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to tag image" -ForegroundColor Red
    exit 1
}
Write-Host "      [OK] Image tagged: $ECR_URI" -ForegroundColor Green

# Step 5: Push to ECR
Write-Host ""
Write-Host "[5/5] Pushing to ECR..." -ForegroundColor Yellow
docker push $ECR_URI

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to push image to ECR" -ForegroundColor Red
    exit 1
}
Write-Host "      [OK] Image pushed successfully" -ForegroundColor Green

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host " Build & Push Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "ECR Image URI: $ECR_URI" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next step: Run 3_deploy_runtime.ps1 to deploy to AgentCore" -ForegroundColor Yellow
Write-Host ""
