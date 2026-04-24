Write-Host "--- GitHub Sync: Set All to Real-Time ---" -ForegroundColor Cyan

# 1. Ensure we are on the main branch
git checkout main

# 2. Add all current files (including siren and GOAT fixes)
git add -A

# 3. Get the exact current time from your computer
$today = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$env:GIT_AUTHOR_DATE="$today"
$env:GIT_COMMITTER_DATE="$today"

# 4. Commit with the NEW time and detailed notes
git commit -m "Project Updated: $today | Siren, GOAT & Rental Purge complete"

Write-Host "Pushing changes to GitHub..." -ForegroundColor Cyan

# 5. Push the updates
git push origin main

Write-Host "--- SUCCESS: GitHub is now updated to $today! ---" -ForegroundColor Green
pause
