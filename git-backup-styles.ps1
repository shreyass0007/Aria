#!/usr/bin/env pwsh
# Quick Git Backup Script for styles.css
# Usage: .\git-backup-styles.ps1 "Your commit message"

param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

$stylesPath = "electron/renderer/styles.css"

# Check if there are changes
git diff --quiet $stylesPath
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ No changes to styles.css" -ForegroundColor Green
    exit 0
}

# Add and commit
git add $stylesPath
git commit -m "styles: $Message"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Committed: $Message" -ForegroundColor Green
    
    # Show what changed
    Write-Host "`nRecent commits:" -ForegroundColor Cyan
    git log --oneline -5 -- $stylesPath
} else {
    Write-Host "✗ Commit failed" -ForegroundColor Red
    exit 1
}
