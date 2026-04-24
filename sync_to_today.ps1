Write-Host "--- GitHub Sync: Set All to Today ---" -ForegroundColor Cyan

# 1. Create a fresh branch without old history
git checkout --orphan temp_branch

# 2. Add all current files
git add -A

# 3. Set the date and time variables for PowerShell
$today = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$env:GIT_AUTHOR_DATE="$today"
$env:GIT_COMMITTER_DATE="$today"

# 4. Commit with today's timestamp
git commit -m "Project Updated: $today"

# 5. Delete the old main branch and rename this one to main
git branch -D main
git branch -m main

Write-Host "Pushing changes to GitHub..." -ForegroundColor Cyan

# 6. Force push to overwrite the old dates on GitHub
git push -f origin main

Write-Host "--- SUCCESS: All files on GitHub are now updated to Today! ---" -ForegroundColor Green
pause
