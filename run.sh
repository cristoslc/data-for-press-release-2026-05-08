#!/usr/bin/env bash
set -euo pipefail

echo "=== Reproducing all outputs for press release May 8, 2026 ==="
echo ""

echo "[1/5] Deduplicating raw audit logs into search sessions..."
uv run python3 analysis/deduplicate_audit_logs.py
echo ""

echo "[2/5] Normalizing shared network organization names..."
uv run python3 data/derived/sppd-shared-networks/normalize_orgs.py
echo ""

echo "[3/5] Classifying assist-other-agency searches..."
uv run python3 analysis/classify_assist_other.py
echo ""

echo "[4/5] Cross-indexing SPPD shared network against ICE 287(g) participants..."
uv run python3 analysis/crossindex.py
echo ""

echo "[5/5] Counting unique states in shared network..."
uv run python3 analysis/count_states.py
echo ""

echo "Done. All outputs in outputs/."