#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

[[ -d .venv ]] || { echo "Run ./scripts/setup.sh first"; exit 1; }
# shellcheck disable=SC1091
source .venv/bin/activate

python -m pytest tests/ -q

API_PORT="${KHUKRA_LOGISTICS_API_PORT:-8010}"
if curl -sf "http://127.0.0.1:${API_PORT}/api/health" >/dev/null; then
  echo "API health OK"
else
  echo "API not running (optional — start ./scripts/start-dev.sh)"
fi

echo "Smoke test passed."
