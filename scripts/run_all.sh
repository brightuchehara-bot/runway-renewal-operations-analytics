#!/usr/bin/env bash
set -euo pipefail

echo "== Runway Ops Analytics: Full Pipeline =="

# Ensure we're in repo root
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# Activate venv if present and not already active
if [[ -z "${VIRTUAL_ENV:-}" && -d ".venv" ]]; then
  echo "Activating venv..."
  source .venv/bin/activate
fi

echo "1) Verifying DB connection..."
python scripts/test_db.py

echo "2) Creating tables..."
mysql --login-path=runway_ops "${DB_NAME:-runway_ops}" < sql/schema/01_create_tables.sql

echo "3) Generating sample data (data/raw/*.csv)..."
python scripts/01_generate_sample_data.py

echo "4) Loading data into MySQL..."
python scripts/02_load_to_mysql.py

echo "5) Creating KPI views..."
mysql --login-path=runway_ops "${DB_NAME:-runway_ops}" < sql/kpis/03_kpi_views.sql

echo "6) Generating reports..."
python scripts/04_generate_reports.py

echo "Done. Outputs in reports/generated/"

