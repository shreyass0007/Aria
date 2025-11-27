#!/usr/bin/env pwsh
# Backup Critical Files (credentials and environment)
# These files should NOT be in Git for security reasons

$backupDir = "CRITICAL_BACKUPS"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = "$backupDir/backup_$timestamp"

# Create backup directory
New-Item -ItemType Directory -Force -Path $backupPath | Out-Null

# Files to backup
$criticalFiles = @(
    ".env",
    "credentials.json",
    "token.pickle",
    "token_gmail.pickle"
)

Write-Host "`n🔐 Backing up critical files..." -ForegroundColor Cyan

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination "$backupPath/$file" -Force
        Write-Host "  ✓ Backed up: $file" -ForegroundColor Green
    }
    else {
        Write-Host "  ⚠ Not found: $file" -ForegroundColor Yellow
    }
}

# Create a README in the backup
$readmeContent = @"
# Critical Backup - $timestamp

This backup contains sensitive files that should NOT be committed to Git:
- .env (API keys and environment variables)
- credentials.json (Google API credentials)
- token.pickle (Google Calendar auth token)
- token_gmail.pickle (Gmail auth token)

## How to Restore:
Copy-Item CRITICAL_BACKUPS/backup_$timestamp/* . -Force

WARNING: KEEP THIS FOLDER PRIVATE - Contains sensitive data!
"@

Set-Content -Path "$backupPath/README.md" -Value $readmeContent

Write-Host "`n✅ Backup complete: $backupPath" -ForegroundColor Green
Write-Host "📁 Backed up $(($criticalFiles | Where-Object { Test-Path $_ }).Count) files" -ForegroundColor Cyan
