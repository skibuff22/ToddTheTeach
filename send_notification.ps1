param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

$envFilePath = Join-Path -Path $PSScriptRoot -ChildPath ".env.notify"

if (-not (Test-Path $envFilePath)) {
    Write-Host "Error: .env.notify not found. Please create it with PUSHOVER_APP_TOKEN and PUSHOVER_USER_KEY."
    exit 1
}

$envSettings = Get-Content $envFilePath | ConvertFrom-StringData

$appToken = $envSettings["PUSHOVER_APP_TOKEN"]
$userKey = $envSettings["PUSHOVER_USER_KEY"]

if (-not $appToken -or -not $userKey) {
    Write-Host "Error: PUSHOVER_APP_TOKEN and PUSHOVER_USER_KEY must be defined in .env.notify."
    exit 1
}

$uri = "https://api.pushover.net/1/messages.json"
$body = @{
    token = $appToken
    user  = $userKey
    message = $Message
    title = "AutomateIT Agent"
}

try {
    Invoke-RestMethod -Uri $uri -Method Post -Body $body
    Write-Host "Notification sent successfully!"
} catch {
    Write-Host "Failed to send notification: $_"
}
