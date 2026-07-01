#!/usr/bin/env bash
# Start API + Next.js UI (Mac/Linux)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API_PORT="${KHUKRA_LOGISTICS_API_PORT:-8010}"
UI_PORT="${KHUKRA_LOGISTICS_UI_PORT:-3020}"
export KHUKRA_LOGISTICS_API_PORT="$API_PORT"
export KHUKRA_LOGISTICS_API_URL="http://127.0.0.1:${API_PORT}"
export NEXT_PUBLIC_API_URL="$KHUKRA_LOGISTICS_API_URL"
export PYTHONPATH="$ROOT/src"

cat > frontend/.env.local <<EOF
KHUKRA_LOGISTICS_API_URL=${KHUKRA_LOGISTICS_API_URL}
NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
EOF

if [[ ! -d .venv ]]; then
  echo "No .venv found — running setup first..."
  ./scripts/setup.sh
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -e ".[dev]" -q

if [[ ! -d frontend/node_modules ]]; then
  (cd frontend && npm install)
fi

cleanup() {
  [[ -n "${API_PID:-}" ]] && kill "$API_PID" 2>/dev/null || true
  [[ -n "${UI_PID:-}" ]] && kill "$UI_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting API on :${API_PORT}..."
python -m uvicorn khukra_logistics.api.main:app --host 127.0.0.1 --port "$API_PORT" &
API_PID=$!

HEALTH_URL="http://127.0.0.1:${API_PORT}/api/health"
echo "Waiting for API..."
for _ in $(seq 1 45); do
  if curl -sf "$HEALTH_URL" | grep -q '"ok"'; then
    break
  fi
  sleep 1
done

# First-run seed if cache empty
if command -v khukra-logistics >/dev/null; then
  COVERED="$(curl -sf "http://127.0.0.1:${API_PORT}/api/disruption/status" | python -c "import sys,json; print(json.load(sys.stdin).get('covered_count',0))" 2>/dev/null || echo 0)"
  if [[ "$COVERED" == "0" ]]; then
    echo "First run — ingesting demo signals (5y)..."
    khukra-logistics refresh --years 5 || true
    khukra-logistics refresh-news || true
  fi
fi

echo "Starting UI on :${UI_PORT}..."
(cd frontend && npm run dev -- --hostname localhost --port "$UI_PORT") &
UI_PID=$!

echo ""
echo "API: http://127.0.0.1:${API_PORT}/docs"
echo "UI:  http://localhost:${UI_PORT}"
echo "Press Ctrl+C to stop."

wait
