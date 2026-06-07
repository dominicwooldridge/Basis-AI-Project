# Usage: .\deploy.ps1
# Requires: AWS CLI, Docker Desktop running, profile GSB570-BedrockOnly-490332585640

$PROFILE    = "GSB570-BedrockOnly-490332585640"
$REGION     = "us-west-2"
$ACCOUNT_ID = "490332585640"
$REPO_NAME  = "basis"
$FUNC_NAME  = "basis-api"
$IMAGE_URI  = "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/${REPO_NAME}:latest"

# 1 — Create ECR repo (safe to run repeatedly)
aws ecr describe-repositories --repository-names $REPO_NAME --region $REGION --profile $PROFILE 2>$null
if ($LASTEXITCODE -ne 0) {
    aws ecr create-repository --repository-name $REPO_NAME --region $REGION --profile $PROFILE
}

# 2 — Authenticate Docker to ECR
aws ecr get-login-password --region $REGION --profile $PROFILE |
    docker login --username AWS --password-stdin "$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

# 3 — Build and push image
docker build --platform linux/amd64 -t "${REPO_NAME}:latest" .
docker tag "${REPO_NAME}:latest" $IMAGE_URI
docker push $IMAGE_URI

# 4 — Create or update Lambda function
$funcExists = aws lambda get-function --function-name $FUNC_NAME --region $REGION --profile $PROFILE 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating Lambda function..."
    # NOTE: replace --role ARN with your actual Lambda execution role ARN
    aws lambda create-function `
        --function-name $FUNC_NAME `
        --package-type Image `
        --code ImageUri=$IMAGE_URI `
        --role "arn:aws:iam::${ACCOUNT_ID}:role/basis-lambda-role" `
        --timeout 900 `
        --memory-size 1024 `
        --environment "Variables={AWS_PROFILE=,NREL_API_KEY=$env:NREL_API_KEY,EIA_API_KEY=$env:EIA_API_KEY}" `
        --region $REGION `
        --profile $PROFILE
} else {
    Write-Host "Updating Lambda function image..."
    aws lambda update-function-code `
        --function-name $FUNC_NAME `
        --image-uri $IMAGE_URI `
        --region $REGION `
        --profile $PROFILE
}

# 5 — Enable Function URL (HTTPS endpoint, no API Gateway needed)
$urlExists = aws lambda get-function-url-config --function-name $FUNC_NAME --region $REGION --profile $PROFILE 2>$null
if ($LASTEXITCODE -ne 0) {
    aws lambda create-function-url-config `
        --function-name $FUNC_NAME `
        --auth-type NONE `
        --region $REGION `
        --profile $PROFILE
}

$url = aws lambda get-function-url-config --function-name $FUNC_NAME --region $REGION --profile $PROFILE |
    ConvertFrom-Json | Select-Object -ExpandProperty FunctionUrl
Write-Host "`nDeployed. Function URL: $url"
Write-Host "Health check: curl ${url}health"
