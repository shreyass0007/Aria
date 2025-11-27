#!/usr/bin/env pwsh
# Backup Critical Files (credentials and environment)

$backupDir = "CRITICAL_BACKUPS"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = "$backupDir/backup_$timestamp"

New-Item -ItemType Directory -Force -Path $backupPath | Out-Null

$criticalFiles = @(".env", "credentials.json", "token.pickle", "token_gmail.pickle")

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

Write-Host "`n✅ Backup complete: $backupPath" -ForegroundColor Green
