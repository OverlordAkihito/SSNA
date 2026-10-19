@echo off
setlocal
if not exist ".venv\Scripts\python.exe" (
  echo Set up the project first. See README.md.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m shet_shet.main
