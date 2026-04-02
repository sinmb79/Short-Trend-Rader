#!/usr/bin/env bash
set -euo pipefail

echo "============================================"
echo "  trend-radar - One-Click Setup"
echo "  Signal survives when handoff is clean."
echo "============================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOW_DIR="$SCRIPT_DIR/n8n"
TEMP_ROOT="${TMPDIR:-/tmp}"
PATCH_DIR="$(mktemp -d "${TEMP_ROOT%/}/trend-radar-n8n-XXXXXX")"
N8N_LOG="${TEMP_ROOT%/}/trend-radar-n8n.log"
trap 'rm -rf "$PATCH_DIR"' EXIT

check_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[fail] $1 is not installed."
    echo "       Install: $2"
    exit 1
  fi
  echo "  [ok] $1 found"
}

pick_python() {
  if command -v python3 >/dev/null 2>&1; then
    echo "python3"
    return
  fi
  if command -v python >/dev/null 2>&1; then
    echo "python"
    return
  fi
  echo ""
}

n8n_running() {
  curl -sSf --max-time 3 http://localhost:5678/healthz >/dev/null 2>&1
}

prepare_workflow() {
  local source_file="$1"
  local target_file="$2"

  "$PYTHON_BIN" - "$source_file" "$target_file" "$SCRIPT_DIR" <<'PY'
import json
import re
import sys
from pathlib import Path

source_path = Path(sys.argv[1])
target_path = Path(sys.argv[2])
project_dir = sys.argv[3]

payload = json.loads(source_path.read_text(encoding="utf-8"))
project_literal = json.dumps(project_dir)
command_line = 'let command = `cd "${escapeForCmd(projectDir)}" && ${launcher}`;\n'

for node in payload.get("nodes", []):
    params = node.get("parameters", {})
    js_code = params.get("jsCode")
    if not js_code:
        continue
    js_code = re.sub(
        r"const projectDir = .*?;\n",
        f"const projectDir = body.project_dir ?? query.project_dir ?? {project_literal};\n",
        js_code,
        count=1,
    )
    js_code = re.sub(r"let command = .*?;\n", command_line, js_code, count=1)
    params["jsCode"] = js_code

target_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
}

echo "[1/5] Checking required tools..."
check_command "node" "https://nodejs.org"
check_command "npm" "https://nodejs.org"
check_command "curl" "Install curl with your package manager."

PYTHON_BIN="$(pick_python)"
if [ -z "$PYTHON_BIN" ]; then
  echo "[fail] Python 3.11+ is required."
  exit 1
fi
echo "  [ok] $PYTHON_BIN found"

if ! "$PYTHON_BIN" - <<'PY'
import sys
raise SystemExit(0 if sys.version_info >= (3, 11) else 1)
PY
then
  echo "[fail] Python 3.11+ is required for trend-radar."
  exit 1
fi
echo ""

echo "[2/5] Installing trend-radar into the current Python environment..."
if "$PYTHON_BIN" - <<'PY'
import sys
raise SystemExit(0 if getattr(sys, "base_prefix", sys.prefix) != sys.prefix else 1)
PY
then
  "$PYTHON_BIN" -m pip install --no-cache-dir -e "$SCRIPT_DIR"
else
  "$PYTHON_BIN" -m pip install --user --no-cache-dir -e "$SCRIPT_DIR"
fi
echo "  [ok] trend-radar package installed"
echo ""

echo "[3/5] Installing n8n..."
if command -v n8n >/dev/null 2>&1; then
  echo "  [ok] n8n already installed ($(n8n --version))"
else
  echo "  [info] Installing n8n with npm..."
  npm install -g n8n
  echo "  [ok] n8n installed"
fi
echo ""

echo "[4/5] Starting n8n..."
if n8n_running; then
  echo "  [ok] n8n already running on http://localhost:5678"
else
  echo "  [info] Launching n8n in the background..."
  n8n start >"$N8N_LOG" 2>&1 &
  N8N_PID=$!
  echo "  [info] Waiting for n8n to respond..."
  for _ in $(seq 1 30); do
    if n8n_running; then
      echo "  [ok] n8n started (PID: $N8N_PID)"
      break
    fi
    sleep 1
  done

  if ! n8n_running; then
    echo "[fail] n8n did not become healthy."
    echo "       Check log: $N8N_LOG"
    exit 1
  fi
fi
echo ""

echo "[5/5] Importing trend-radar workflows..."

import_workflow() {
  local file_name="$1"
  local label="$2"
  local source_file="$WORKFLOW_DIR/$file_name"
  local patched_file="$PATCH_DIR/$file_name"

  if [ ! -f "$source_file" ]; then
    echo "  [warn] Missing file: $source_file"
    return
  fi

  prepare_workflow "$source_file" "$patched_file"
  if n8n import:workflow --input="$patched_file" >/dev/null 2>&1; then
    echo "  [ok] $label"
  else
    echo "  [warn] $label import failed"
  fi
}

import_workflow "workflow.json" "Trend Radar - Collection Orchestrator"
import_workflow "workflow-digest.json" "Trend Radar - Daily Digest"

echo ""
echo "============================================"
echo "  Setup complete"
echo ""
echo "  n8n: http://localhost:5678"
echo "  Workflows imported: 2"
echo ""
echo "  Open the browser and you should see"
echo "  the trend-radar workflows already listed."
echo "============================================"

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open http://localhost:5678 >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then
  open http://localhost:5678 >/dev/null 2>&1 &
fi
