@echo off
REM Batch script to run build_static_site.py with --clean --pdf
REM Schedule this with Task Scheduler to run once a day (full rebuild)

cd /d "%~dp0"

REM Pull web edits (committed back by mist) into the content vault before building.
REM Fast-forward only, so local Obsidian edits are never clobbered.
powershell -NoProfile -Command "Get-ChildItem -Path 'content\.git' -Filter 'desktop.ini' -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue"
git -C content pull --ff-only --no-edit

python build_static_site.py --config config.yml --clean --pdf

REM Remove Windows Explorer metadata from Git refs before Git commands
powershell -NoProfile -Command "Get-ChildItem -Path '.git\refs' -Filter 'desktop.ini' -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue"

REM Commit and push changes (only the specific output folder)
git add dist
git commit -m "Auto-build: Full rebuild with PDFs [%date% %time%]"
powershell -NoProfile -Command "Get-ChildItem -Path '.git\refs' -Filter 'desktop.ini' -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue"
git push

