# Test the agent locally before deployment
Write-Host "================================" -ForegroundColor Cyan
Write-Host " Testing Agent Locally" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Set environment for local testing
$env:USE_MCP_ARN = "false"
$env:MCP_SERVER_URL = "http://172.17.0.3:8000/mcp"
$env:DEFAULT_USER_ID = "local-test-user-001"
$env:DEFAULT_SESSION_ID = "local-test-session-001"

Write-Host "Running test_local.py..." -ForegroundColor Yellow
python test_local.py

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host " Local Test Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review test results JSON file" -ForegroundColor White
Write-Host "  2. If tests pass, run 2_build_push.ps1" -ForegroundColor White
Write-Host "  3. Then run 3_deploy_runtime.ps1" -ForegroundColor White
Write-Host ""
