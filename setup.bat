@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

echo ============================================
echo   trend-radar - One-Click Setup
echo   Signal survives when handoff is clean.
echo ============================================
echo.

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "WORKFLOW_DIR=%SCRIPT_DIR%\n8n"
set "PATCH_DIR=%TEMP%\trend-radar-n8n-%RANDOM%%RANDOM%"
set "N8N_LOG=%TEMP%\trend-radar-n8n.log"

if exist "%PATCH_DIR%" rmdir /s /q "%PATCH_DIR%" >nul 2>&1
mkdir "%PATCH_DIR%" >nul 2>&1

echo [1/5] Checking required tools...
where node >nul 2>&1 || (echo [fail] Node.js is required. https://nodejs.org && exit /b 1)
echo   [ok] node found
where npm >nul 2>&1 || (echo [fail] npm is required. Install Node.js first. && exit /b 1)
echo   [ok] npm found
where py >nul 2>&1 && (set "PY_CMD=py -3") || (
  where python >nul 2>&1 && (set "PY_CMD=python") || (echo [fail] Python 3.11+ is required. && exit /b 1)
)
echo   [ok] !PY_CMD! found
%PY_CMD% -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1 || (echo [fail] Python 3.11+ is required for trend-radar. && exit /b 1)
echo.

echo [2/5] Installing trend-radar into the current Python environment...
if defined VIRTUAL_ENV (
  %PY_CMD% -m pip install --no-cache-dir -e "%SCRIPT_DIR%" || (echo [fail] Python package install failed. && exit /b 1)
) else (
  %PY_CMD% -m pip install --user --no-cache-dir -e "%SCRIPT_DIR%" || (echo [fail] Python package install failed. && exit /b 1)
)
echo   [ok] trend-radar package installed
echo.

echo [3/5] Installing n8n...
where n8n >nul 2>&1 && (
  echo   [ok] n8n already installed
) || (
  echo   [info] Installing n8n with npm...
  npm install -g n8n || (echo [fail] n8n installation failed. && exit /b 1)
  echo   [ok] n8n installed
)
echo.

echo [4/5] Starting n8n...
powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing http://localhost:5678/healthz -TimeoutSec 3 ^| Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel%==0 (
  echo   [ok] n8n already running on http://localhost:5678
) else (
  echo   [info] Launching n8n in the background...
  start "" /B cmd /c "n8n start > \"%N8N_LOG%\" 2>&1"
  echo   [info] Waiting for n8n to respond...
  for /L %%I in (1,1,30) do (
    powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing http://localhost:5678/healthz -TimeoutSec 3 ^| Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
    if !errorlevel! EQU 0 (
      set "N8N_READY=1"
    )
    if not defined N8N_READY timeout /t 1 /nobreak >nul
  )
  if not defined N8N_READY (
    echo [fail] n8n did not become healthy.
    echo        Check log: %N8N_LOG%
    exit /b 1
  )
  echo   [ok] n8n started
)
echo.

echo [5/5] Importing trend-radar workflows...
if not exist "%WORKFLOW_DIR%\workflow.json" echo   [warn] Missing workflow.json
if not exist "%WORKFLOW_DIR%\workflow-digest.json" echo   [warn] Missing workflow-digest.json

powershell -NoProfile -Command ^
  "$scriptDir = [System.IO.Path]::GetFullPath('%SCRIPT_DIR%');" ^
  "$workflowDir = [System.IO.Path]::GetFullPath('%WORKFLOW_DIR%');" ^
  "$patchDir = [System.IO.Path]::GetFullPath('%PATCH_DIR%');" ^
  "New-Item -ItemType Directory -Force -Path $patchDir | Out-Null;" ^
  "$projectLiteral = [System.Text.Json.JsonSerializer]::Serialize($scriptDir);" ^
  "$files = @('workflow.json', 'workflow-digest.json');" ^
  "foreach ($file in $files) {" ^
  "  $source = Join-Path $workflowDir $file;" ^
  "  if (-not (Test-Path $source)) { continue }" ^
  "  $json = Get-Content $source -Raw | ConvertFrom-Json;" ^
  "  foreach ($node in $json.nodes) {" ^
  "    if ($null -ne $node.parameters -and $null -ne $node.parameters.jsCode) {" ^
  "      $code = [string]$node.parameters.jsCode;" ^
  "      $code = $code -replace 'const projectDir = .*?;\n', ('const projectDir = body.project_dir ?? query.project_dir ?? ' + $projectLiteral + ';' + [Environment]::NewLine);" ^
  "      $node.parameters.jsCode = $code;" ^
  "    }" ^
  "  }" ^
  "  $target = Join-Path $patchDir $file;" ^
  "  $json | ConvertTo-Json -Depth 100 | Set-Content -Path $target -Encoding UTF8;" ^
  "}"

if exist "%PATCH_DIR%\workflow.json" (
  n8n import:workflow --input="%PATCH_DIR%\workflow.json" >nul 2>&1 && echo   [ok] Trend Radar - Collection Orchestrator || echo   [warn] Collection workflow import failed
)
if exist "%PATCH_DIR%\workflow-digest.json" (
  n8n import:workflow --input="%PATCH_DIR%\workflow-digest.json" >nul 2>&1 && echo   [ok] Trend Radar - Daily Digest || echo   [warn] Digest workflow import failed
)

echo.
echo ============================================
echo   Setup complete
echo.
echo   n8n: http://localhost:5678
echo   Workflows imported: 2
echo.
echo   Open the browser and you should see
echo   the trend-radar workflows already listed.
echo ============================================

if exist "%PATCH_DIR%" rmdir /s /q "%PATCH_DIR%" >nul 2>&1
start "" http://localhost:5678
endlocal
