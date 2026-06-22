$projectId = "your-gcp-project-id"

Write-Host "Setting project..."
gcloud config set project $projectId

Write-Host ""
Write-Host "Enabling APIs..."
gcloud services enable run.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com

Write-Host ""
Write-Host "Creating secrets..."
Write-Host "NOTE: Replace the placeholder values below with your actual keys before running."

# Helper function to create or update a secret
function Set-GcloudSecret($name, $value) {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($value)
    $tempFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllBytes($tempFile, $bytes)
    
    $existing = gcloud secrets describe $name 2>&1
    if ($LASTEXITCODE -ne 0) {
        gcloud secrets create $name --data-file=$tempFile
        Write-Host "  Created secret: $name"
    } else {
        gcloud secrets versions add $name --data-file=$tempFile
        Write-Host "  Updated secret: $name"
    }
    Remove-Item $tempFile
}

Set-GcloudSecret "MONGODB_URI" "your-mongodb-uri-here"
Set-GcloudSecret "VAPI_API_KEY" "your-vapi-api-key-here"
Set-GcloudSecret "VAPI_PHONE_NUMBER_ID" "your-vapi-phone-number-id-here"
Set-GcloudSecret "OPENAI_API_KEY" "your-openai-api-key-here"

Write-Host ""
Write-Host "All secrets created!"
Write-Host ""
Write-Host "Now deploying to Cloud Run..."

Set-Location "c:\Users\polam\Downloads\krid"

gcloud builds submit --tag "gcr.io/$projectId/voice-orchestrator" .

gcloud run deploy voice-orchestrator `
    --image "gcr.io/$projectId/voice-orchestrator" `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --port 8080 `
    --memory 1Gi `
    --cpu 1 `
    --min-instances 0 `
    --max-instances 3 `
    --timeout 300 `
    --set-secrets="MONGODB_URI=MONGODB_URI:latest,VAPI_API_KEY=VAPI_API_KEY:latest,OPENAI_API_KEY=OPENAI_API_KEY:latest,VAPI_PHONE_NUMBER_ID=VAPI_PHONE_NUMBER_ID:latest"

Write-Host ""
Write-Host "=== DEPLOYMENT COMPLETE ==="
Write-Host ""
gcloud run services describe voice-orchestrator --region us-central1 --format "value(status.url)"
