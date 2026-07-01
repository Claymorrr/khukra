#!/usr/bin/env bash
# First-time setup for Khukra (Mac/Linux)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SEED_DATA=0
YEARS=5
while [[ $# -gt 0 ]]; do
  case "$1" in
    --seed-data) SEED_DATA=1; shift ;;
    --years) YEARS="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

echo "Khukra setup"
echo "======================"

command -v python3 >/dev/null || { echo "python3 required"; exit 1; }
command -v npm >/dev/null || { echo "npm required"; exit 1; }

PY_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
echo "Python $PY_VERSION"

if [[ ! -d .venv ]]; then
  echo "Creating virtualenv..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip -q
python -m pip install -e ".[dev]" -q

echo "Installing frontend dependencies..."
(cd frontend && npm install)

mkdir -p data

if [[ "$SEED_DATA" -eq 1 ]]; then
  echo "Seeding disruption signal cache (${YEARS}y)..."
  khukra refresh --years "$YEARS"
  khukra refresh-news || true
fi

echo ""
echo "Setup complete."
echo "  Run:  ./scripts/start-dev.sh"
echo "  Test: ./scripts/smoke-test.sh"
