#!/usr/bin/env python3
"""
Classifier: Flag audit log entries indicating South Portland officers
assisting other agencies, based on Reason field text patterns.
"""

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
INPUT = ROOT / "outputs" / "audit-logs-deduplicated" / "sopo-flock-audit-deduped.csv"
OUTPUT = ROOT / "outputs" / "assist-other-agencies" / "assist-other-agencies.csv"
REASON_COL = "Reason"

PATTERNS = [
    # Explicit "assist other" / agency coordination
    (r"assist\s*other", "assist-other"),
    (
        r"(Auburn|Bath|Scarborough|Portland|Westbrook|Windham|Sanford|Bangor|Brunswick|Freeport|Cape\s*Elizabeth|Lewiston|Saco)\b.*file\s*1",
        "assist-other-file1",
    ),
    (
        r"(Auburn|Bath|Scarborough|Portland|Westbrook|Windham|Sanford|Bangor|Brunswick|Freeport|Cape\s*Elizabeth|Lewiston|Saco)\s+(file|bolo|request)",
        "assist-other-named-agency",
    ),
    (
        r"file\s*1.*(Auburn|Bath|Scarborough|Portland|Westbrook|Windham|Sanford|Bangor|Brunswick|Freeport|Cape\s*Elizabeth|Lewiston|Saco)",
        "assist-other-file1",
    ),
    # MIAC / MDEA / MSP — statewide info-sharing systems often tied to multi-agency ops
    (r"\bMIAC\b", "statewide-system"),
    (r"\bMDEA\b", "statewide-system"),
    (r"\bMSP\b", "statewide-system"),
    (r"\bMiac\b", "statewide-system"),
    (r"\bMdea\b", "statewide-system"),
    (r"\bMIAC\s", "statewide-system"),
    (r"\bMDEA\s", "statewide-system"),
    (r"miac\s", "statewide-system"),
    (r"mdea\s", "statewide-system"),
    # Specific multi-agency indicators
    (r"help\s*(other|another)", "assist-other"),
    (r"assist\s*$", "assist-other"),
    (r"Extortion/Blackmail - Assist other agency investigation", "assist-other"),
    (r"Burglary/Breaking & Entering - File 1/Burglary assist for WPD", "assist-other"),
    (r"Drugs/Narcotics - drug investigation/ assist other agency", "assist-other"),
]


def classify_reason(reason: str) -> tuple[str | None, str | None]:
    if pd.isna(reason) or str(reason).strip() == "":
        return None, None
    reason_lower = str(reason).lower()
    for pattern, label in PATTERNS:
        if re.search(pattern, reason_lower):
            return label, pattern
    return None, None


def main():
    df = pd.read_csv(INPUT)
    df["assist_label"] = None
    df["assist_pattern"] = None

    for idx, row in df.iterrows():
        label, pattern = classify_reason(row[REASON_COL])
        df.at[idx, "assist_label"] = label
        df.at[idx, "assist_pattern"] = pattern

    hits = df[df["assist_label"].notna()].copy()
    hits = hits.sort_values(["Search Date", "Search Time"])

    hits.to_csv(OUTPUT, index=False)
    print(f"Total rows:     {len(df)}")
    print(f"Assist hits:    {len(hits)}")
    print(f"Output:         {OUTPUT}")


if __name__ == "__main__":
    main()
