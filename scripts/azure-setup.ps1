# GenomeCostTracker Azure Setup Script
# This script sets up the required Azure resources and permissions

param(
    [Parameter(Mandatory=$true)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroupName = "genomecost-rg",
    
    [Parameter(Mandatory=$true)]
    [string]$Location = "East US",
    
    [Parameter(Mandatory=$false)]
    [string]$ServicePrincipalName = "genomecost-sp"
)

Write-Host "🧬 GenomeCostTracker Azure Setup" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if Azure CLI is installed
if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Error "Azure CLI is not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
}

# Login to Azure
Write-Host "Logging in to Azure..." -ForegroundColor Yellow
az login

# Set subscription
Write-Host "Setting subscription to $SubscriptionId..." -ForegroundColor Yellow
az account set --subscription $SubscriptionId

# Create resource group
Write-Host "Creating resource group $ResourceGroupName..." -ForegroundColor Yellow
az group create --name $ResourceGroupName --location $Location

# Create service principal for GenomeCostTracker
Write-Host "Creating service principal $ServicePrincipalName..." -ForegroundColor Yellow
$spOutput = az ad sp create-for-rbac --name $ServicePrincipalName --role "Cost Management Reader" --scopes "/subscriptions/$SubscriptionId" --output json | ConvertFrom-Json

$clientId = $spOutput.appId
$clientSecret = $spOutput.password
$tenantId = $spOutput.tenant

Write-Host "Service Principal created successfully!" -ForegroundColor Green
Write-Host "Client ID: $clientId" -ForegroundColor Cyan
Write-Host "Tenant ID: $tenantId" -ForegroundColor Cyan
Write-Host "Client Secret: [HIDDEN]" -ForegroundColor Cyan

# Assign additional permissions
Write-Host "Assigning additional permissions..." -ForegroundColor Yellow

# Resource Group Reader for resource discovery
az role assignment create --assignee $clientId --role "Reader" --scope "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName"

# Tag Contributor for resource tagging
az role assignment create --assignee $clientId --role "Tag Contributor" --scope "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroupName"

# Create Azure Batch account
$batchAccountName = "genomecostbatch$(Get-Random -Minimum 1000 -Maximum 9999)"
Write-Host "Creating Azure Batch account $batchAccountName..." -ForegroundColor Yellow

az batch account create `
    --name $batchAccountName `
    --resource-group $ResourceGroupName `
    --location $Location

# Get Batch account keys
$batchKeys = az batch account keys list --name $batchAccountName --resource-group $ResourceGroupName --output json | ConvertFrom-Json
$batchEndpoint = "https://$batchAccountName.$Location.batch.azure.com"

# Create storage account for Batch and genomics data
$storageAccountName = "genomecost$(Get-Random -Minimum 1000 -Maximum 9999)"
Write-Host "Creating storage account $storageAccountName..." -ForegroundColor Yellow

az storage account create `
    --name $storageAccountName `
    --resource-group $ResourceGroupName `
    --location $Location `
    --sku Standard_LRS `
    --kind StorageV2 `
    --access-tier Hot

# Get storage account keys
$storageKeys = az storage account keys list --account-name $storageAccountName --resource-group $ResourceGroupName --output json | ConvertFrom-Json
$storageKey = $storageKeys[0].value

# Create file shares for genomics data
Write-Host "Creating file shares..." -ForegroundColor Yellow

az storage share create --name "genomics-data" --account-name $storageAccountName --account-key $storageKey
az storage share create --name "genomics-results" --account-name $storageAccountName --account-key $storageKey
az storage share create --name "genomics-temp" --account-name $storageAccountName --account-key $storageKey

# Create Batch pool for genomics workloads
Write-Host "Creating Batch pool..." -ForegroundColor Yellow

# Create pool configuration JSON
$poolConfig = @{
    id = "genomics-pool"
    vmSize = "Standard_D4s_v3"
    targetDedicatedNodes = 0
    targetLowPriorityNodes = 5
    enableAutoScale = $true
    autoScaleFormula = 'startingNumberOfVMs = 1; maxNumberofVMs = 20; pendingTaskSamplePercent = $PendingTasks.GetSamplePercent(180 * TimeInterval_Second); pendingTaskSamples = pendingTaskSamplePercent < 70 ? startingNumberOfVMs : avg($PendingTasks.GetSample(180 * TimeInterval_Second)); $TargetLowPriorityNodes=min(maxNumberofVMs, pendingTaskSamples);'
    enableInterNodeCommunication = $false
    taskSlotsPerNode = 4
    virtualMachineConfiguration = @{
        imageReference = @{
            publisher = "microsoft-azure-batch"
            offer = "ubuntu-server-container"
            sku = "20-04-lts"
            version = "latest"
        }
        nodeAgentSkuId = "batch.node.ubuntu 20.04"
    }
} | ConvertTo-Json -Depth 10

# Save pool config to temp file
$poolConfigFile = [System.IO.Path]::GetTempFileName()
$poolConfig | Out-File -FilePath $poolConfigFile -Encoding UTF8

# Create the pool
az batch pool create --json-file $poolConfigFile --account-name $batchAccountName --account-key $batchKeys.primary

# Clean up temp file
Remove-Item $poolConfigFile

# Create environment file
Write-Host "Creating environment configuration..." -ForegroundColor Yellow

$envContent = @"
# GenomeCostTracker Environment Configuration
# Generated on $(Get-Date)

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/genomecost

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Azure Configuration
AZURE_TENANT_ID=$tenantId
AZURE_CLIENT_ID=$clientId
AZURE_CLIENT_SECRET=$clientSecret
AZURE_SUBSCRIPTION_ID=$SubscriptionId

# Azure Batch
AZURE_BATCH_ACCOUNT=$batchAccountName
AZURE_BATCH_KEY=$($batchKeys.primary)
AZURE_BATCH_ENDPOINT=$batchEndpoint

# Azure Storage
AZURE_STORAGE_ACCOUNT=$storageAccountName
AZURE_STORAGE_KEY=$storageKey

# Resource Configuration
AZURE_RESOURCE_GROUP=$ResourceGroupName
AZURE_LOCATION=$Location

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=GenomeCostTracker
BACKEND_CORS_ORIGINS=["http://localhost:4200","https://genomecost.vercel.app"]

# Redis (for production)
REDIS_URL=redis://localhost:6379
"@

$envFile = Join-Path $PSScriptRoot "..\backend\.env"
$envContent | Out-File -FilePath $envFile -Encoding UTF8

Write-Host "Environment file created at: $envFile" -ForegroundColor Green

# Create Nextflow environment file
$nextflowEnvContent = @"
# Nextflow Azure Configuration for GenomeCostTracker
export AZURE_BATCH_ACCOUNT=$batchAccountName
export AZURE_BATCH_KEY=$($batchKeys.primary)
export AZURE_BATCH_ENDPOINT=$batchEndpoint
export AZURE_STORAGE_ACCOUNT=$storageAccountName
export AZURE_STORAGE_KEY=$storageKey
export NXF_EXECUTOR=azurebatch
export NXF_WORK=az://genomics-temp/work
"@

$nextflowEnvFile = Join-Path $PSScriptRoot "..\config\nextflow.env"
$nextflowEnvContent | Out-File -FilePath $nextflowEnvFile -Encoding UTF8

Write-Host "Nextflow environment file created at: $nextflowEnvFile" -ForegroundColor Green

# Create sample Nextflow command
$sampleCommand = @"
# Sample Nextflow command for GenomeCostTracker integration
nextflow run nf-core/rnaseq \
    -profile azure \
    --input samples.csv \
    --outdir results \
    --genome GRCh38 \
    -c nextflow.config \
    --project_name "Cancer Genomics" \
    --sample_id "SAMPLE_001" \
    --user_email "researcher@lab.com" \
    --pipeline_type "RNA-seq" \
    --azure_resource_group "$ResourceGroupName" \
    --azure_batch_pool_id "genomics-pool"
"@

$sampleCommandFile = Join-Path $PSScriptRoot "..\scripts\sample-nextflow-command.sh"
$sampleCommand | Out-File -FilePath $sampleCommandFile -Encoding UTF8

Write-Host "Sample Nextflow command created at: $sampleCommandFile" -ForegroundColor Green

# Summary
Write-Host "`n🎉 Azure setup completed successfully!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Cyan
Write-Host "Batch Account: $batchAccountName" -ForegroundColor Cyan
Write-Host "Storage Account: $storageAccountName" -ForegroundColor Cyan
Write-Host "Service Principal: $ServicePrincipalName" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Update the DATABASE_URL in the .env file with your PostgreSQL connection string" -ForegroundColor White
Write-Host "2. Change the SECRET_KEY in the .env file to a secure random string" -ForegroundColor White
Write-Host "3. Start the GenomeCostTracker backend: cd backend && python -m uvicorn src.api.main:app --reload" -ForegroundColor White
Write-Host "4. Start the Angular frontend: cd frontend && npm install && ng serve" -ForegroundColor White
Write-Host "5. Test with the sample Nextflow command in scripts/sample-nextflow-command.sh" -ForegroundColor White

Write-Host "`n⚠️  Important: Store the service principal credentials securely!" -ForegroundColor Red
Write-Host "Client ID: $clientId" -ForegroundColor Red
Write-Host "Client Secret: $clientSecret" -ForegroundColor Red
Write-Host "Tenant ID: $tenantId" -ForegroundColor Red