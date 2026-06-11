# PowerShell script to watch source folder and run build 1 minute after changes
# Run this script manually or set it to run at startup

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$configFile = Join-Path $scriptPath "config.yml"  # Which config to use
$sourceFolder = "C:/Users/Zoom/My Drive (hello@causalmap.app)/Causal Map/10-19 Outreach - marketing - presentations - academic - theory/19aCMgarden/content"
$outputFolder = "dist"  # Which output folder to commit/push
$buildScript = Join-Path $scriptPath "build_static_site.py"
$mapcatIndexScript = "C:/dev/causal-map-extension/scripts/generate-mapcat-garden-index.js"
$mapcatIndexOutput = "C:/dev/causal-map-extension/webapp/mapcat-garden-index.md"
$debounceSeconds = 60  # Wait 1 minute after last change
$maxWaitSeconds = 300  # Force build after 5 minutes even if changes keep coming
$pollIntervalSeconds = 180  # Poll every 3 minutes for Google Drive changes

# Track last change time
$lastChangeTime = $null
$firstChangeTime = $null  # Track when changes first started
$pendingBuild = $false
$lastEventFile = $null
$lastEventTime = $null
$lastPollTime = Get-Date
$lastKnownMtimes = @{}  # Track file modification times for polling

function Remove-GitDesktopIniRefs {
    # Windows/Google Drive can create desktop.ini inside .git/refs, which breaks git push.
    $refsPath = Join-Path $scriptPath ".git\refs"
    Get-ChildItem -Path $refsPath -Filter "desktop.ini" -Recurse -Force -ErrorAction SilentlyContinue |
        Remove-Item -Force -ErrorAction SilentlyContinue
}

function Sync-ContentFromGitHub {
    # The content vault is its own git repo. Web edits made in mist are committed
    # back to its GitHub remote, so pull them in before building. Fast-forward
    # only, so any local Obsidian edits are never clobbered (resolve those by hand).
    $contentGit = Join-Path $sourceFolder ".git"
    if (-not (Test-Path $contentGit)) { return $false }
    Get-ChildItem -Path $contentGit -Filter "desktop.ini" -Recurse -Force -ErrorAction SilentlyContinue |
        Remove-Item -Force -ErrorAction SilentlyContinue
    $before = git -C $sourceFolder rev-parse HEAD 2>$null
    git -C $sourceFolder pull --ff-only --no-edit 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] content pull skipped (diverged or error); resolve manually." -ForegroundColor Yellow
        return $false
    }
    $after = git -C $sourceFolder rev-parse HEAD 2>$null
    if ($before -ne $after) {
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Pulled web edits into content vault." -ForegroundColor Magenta
        return $true
    }
    return $false
}

function Run-Build {
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Running build..." -ForegroundColor Green
    Set-Location $scriptPath
    
    # Run build (incremental)
    # Only page PDFs - chapter/site PDFs only on --clean runs
    python $buildScript --config $configFile --incremental --incremental-strict-pipeline --page-pdf
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Build failed with exit code $LASTEXITCODE" -ForegroundColor Red
        return
    }
    
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Build completed successfully." -ForegroundColor Green

    # Keep MapCat's Garden index in sync with Obsidian front matter tags.
    if (Test-Path $mapcatIndexScript) {
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Updating MapCat Garden index..." -ForegroundColor Cyan
        node $mapcatIndexScript --garden-config $configFile --out $mapcatIndexOutput
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] MapCat Garden index update failed; continuing Garden build flow." -ForegroundColor Yellow
        }
    }
    
    # Commit and push changes
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Checking for changes to commit..." -ForegroundColor Cyan
    Remove-GitDesktopIniRefs

    # Stage only the specific output folder for this config
    git add "$outputFolder"
    
    # Get staged files and unstage those with '!' in filename
    $stagedFiles = git diff --cached --name-only
    foreach ($file in $stagedFiles) {
        $filename = Split-Path -Leaf $file
        if ($filename -match '!') {
            git reset HEAD -- "$file" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  Excluded draft file: $file" -ForegroundColor Gray
            }
        }
    }
    
    # Only commit if there are staged changes in the output folder
    git diff --cached --quiet
    $hasStagedChanges = ($LASTEXITCODE -ne 0)
    if ($hasStagedChanges) {
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Staged changes found, committing..." -ForegroundColor Cyan
        $commitMsg = "Auto-build: Incremental rebuild with PDFs [$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')]"
        git commit -m $commitMsg
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Commit failed." -ForegroundColor Red
            return
        }
    } else {
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] No staged output changes to commit." -ForegroundColor Gray
    }

    # Push any local auto-build commit that is still ahead of origin
    Remove-GitDesktopIniRefs
    $aheadCount = git rev-list --count "@{u}..HEAD" 2>$null
    if ($LASTEXITCODE -eq 0 -and [int]$aheadCount -gt 0) {
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Pushing $aheadCount local commit(s)..." -ForegroundColor Cyan
        git push
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Push completed successfully." -ForegroundColor Green
        } else {
            Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Push failed." -ForegroundColor Red
        }
    } else {
        Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] No local commits to push." -ForegroundColor Gray
    }
}

# FileSystemWatcher to monitor source folder
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $sourceFolder
$watcher.IncludeSubdirectories = $true
$watcher.Filter = "*.*"
$watcher.NotifyFilter = [System.IO.NotifyFilters]::FileName -bor [System.IO.NotifyFilters]::LastWrite -bor [System.IO.NotifyFilters]::DirectoryName
$watcher.EnableRaisingEvents = $true

# Action when file changes - just record the time
$action = {
    param($sender, $e)
    $fileName = $e.Name
    $fullPath = $e.FullPath
    
    # Skip directory-only changes (no file extension = likely a directory)
    if ($fileName -notmatch '\.') {
        return
    }
    
    # Skip temporary files and hidden files
    if ($fileName -match '^\.|~$|\.tmp$|\.swp$|desktop\.ini$') {
        return
    }
    
    # Only track markdown files to reduce noise from Google Drive sync
    if ($fileName -notmatch '\.md$') {
        return
    }
    
    # Deduplicate: ignore same file within 2 seconds
    $now = Get-Date
    if ($global:lastEventFile -eq $fileName -and $global:lastEventTime -and (($now - $global:lastEventTime).TotalSeconds -lt 2)) {
        return
    }
    
    # Set global flag and time
    $global:lastChangeTime = $now
    # Track when changes first started (for max wait)
    if (-not $global:firstChangeTime) {
        $global:firstChangeTime = $now
    }
    $global:pendingBuild = $true
    $global:lastEventFile = $fileName
    $global:lastEventTime = $now
    Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Change detected: $($e.ChangeType) - $fileName" -ForegroundColor Yellow
}

# Verify folder exists
if (-not (Test-Path $sourceFolder)) {
    Write-Host "ERROR: Source folder does not exist: $sourceFolder" -ForegroundColor Red
    return
}

# Register events
Register-ObjectEvent -InputObject $watcher -EventName "Changed" -Action $action | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName "Created" -Action $action | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName "Deleted" -Action $action | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName "Renamed" -Action $action | Out-Null

Write-Host "Watching folder: $sourceFolder" -ForegroundColor Cyan
Write-Host "Build will run $debounceSeconds seconds after changes stop (max wait: $maxWaitSeconds s)." -ForegroundColor Cyan
Write-Host "Polling every $pollIntervalSeconds seconds for Google Drive sync changes." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop..." -ForegroundColor Cyan

# Main loop - check if we need to build
try {
    while ($true) {
        Start-Sleep -Seconds 1
        $now = Get-Date
        
        # Periodic polling for Google Drive changes (every 3 minutes)
        if (($now - $lastPollTime).TotalSeconds -ge $pollIntervalSeconds) {
            $lastPollTime = $now

            # Pull web edits (committed back by mist) before scanning for changes
            if (Sync-ContentFromGitHub) {
                $global:lastChangeTime = $now
                if (-not $global:firstChangeTime) { $global:firstChangeTime = $now }
                $global:pendingBuild = $true
            }

            $changedFiles = @()
            
            # Scan for .md files and check mtimes
            Get-ChildItem -Path $sourceFolder -Recurse -Filter "*.md" -ErrorAction SilentlyContinue | ForEach-Object {
                $filePath = $_.FullName
                $currentMtime = $_.LastWriteTime
                
                if ($lastKnownMtimes.ContainsKey($filePath)) {
                    if ($currentMtime -gt $lastKnownMtimes[$filePath]) {
                        $changedFiles += $_.Name
                    }
                }
                $lastKnownMtimes[$filePath] = $currentMtime
            }
            
            if ($changedFiles.Count -gt 0) {
                Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Poll detected $($changedFiles.Count) changed file(s): $($changedFiles[0])..." -ForegroundColor Magenta
                $global:lastChangeTime = $now
                if (-not $global:firstChangeTime) {
                    $global:firstChangeTime = $now
                }
                $global:pendingBuild = $true
            }
        }
        
        # Check if we have a pending build and enough time has passed
        if ($global:pendingBuild -and $global:lastChangeTime) {
            $elapsedSinceLastChange = ($now - $global:lastChangeTime).TotalSeconds
            $elapsedSinceFirstChange = if ($global:firstChangeTime) { ($now - $global:firstChangeTime).TotalSeconds } else { 0 }
            
            # Build if: debounce period passed OR max wait time exceeded
            if ($elapsedSinceLastChange -ge $debounceSeconds) {
                Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $debounceSeconds seconds elapsed since last change, starting build..." -ForegroundColor Cyan
                $global:pendingBuild = $false
                $global:lastChangeTime = $null
                $global:firstChangeTime = $null
                Run-Build
            } elseif ($elapsedSinceFirstChange -ge $maxWaitSeconds) {
                Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Max wait time ($maxWaitSeconds s) exceeded, starting build..." -ForegroundColor Cyan
                $global:pendingBuild = $false
                $global:lastChangeTime = $null
                $global:firstChangeTime = $null
                Run-Build
            }
        }
    }
} finally {
    Write-Host "`nStopping watcher..." -ForegroundColor Yellow
    $watcher.EnableRaisingEvents = $false
    $watcher.Dispose()
    Get-EventSubscriber | Unregister-Event -ErrorAction SilentlyContinue
}
