#!/usr/bin/env python3
"""
Thin wrapper — the canonical normalize_orgs.py now lives at:
  data/derived/sppd-shared-networks-normalized/normalize_orgs.py

This file is retained for backward compatibility only.
"""

import subprocess
import sys
from pathlib import Path

CANONICAL = (
    Path(__file__).parent.parent
    / "data"
    / "derived"
    / "sppd-shared-networks"
    / "normalize_orgs.py"
)

if __name__ == "__main__":
    sys.exit(subprocess.call([sys.executable, str(CANONICAL)]))
