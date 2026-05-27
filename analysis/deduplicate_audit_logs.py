#!/usr/bin/env python3
"""
Deduplicate SPPD Flock audit logs by collapsing multi-network hits
into single search sessions.

A single Flock search session queries multiple camera networks
simultaneously. The audit log records each network hit as a separate
row. This script collapses rows sharing the same
(Name, Reason, Time Frame, Org Name) into one session.

Reads:  data/sppd-foaa-2026-audit-logs/raw-monthly/*.csv
Writes: outputs/audit-logs-deduplicated/sopo-flock-audit-deduped.csv
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
INPUT_DIR = ROOT / "data" / "sppd-foaa-2026-audit-logs" / "raw-monthly"
OUTPUT = ROOT / "outputs" / "audit-logs-deduplicated" / "sopo-flock-audit-deduped.csv"
DEDUPE_KEY = ["Name", "Reason", "Time Frame", "Org Name"]


def main():
    csv_files = sorted(INPUT_DIR.glob("*-South Portland ME PD-Audit*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No audit log CSVs found in {INPUT_DIR}")

    frames = []
    for f in csv_files:
        df = pd.read_csv(f)
        df["Source File"] = f.name
        frames.append(df)

    raw = pd.concat(frames, ignore_index=True)
    raw.columns = [c.strip() for c in raw.columns]
    print(f"Raw rows: {len(raw)}")

    raw["Search Time parsed"] = pd.to_datetime(
        raw["Search Time"], format="mixed", utc=True, errors="coerce"
    )
    raw["Search Date"] = raw["Search Time parsed"].dt.strftime("%m/%d/%Y")
    raw["Search Time Clean"] = raw["Search Time parsed"].dt.strftime(
        "%I:%M:%S %p UTC"
    )

    raw = raw.sort_values("Search Time parsed")

    grouped = raw.groupby(DEDUPE_KEY, sort=False)
    sessions = []
    for _, group in grouped:
        first = group.iloc[0]
        sessions.append(
            {
                "Name": first["Name"],
                "Org Name": first["Org Name"],
                "Reason": first["Reason"],
                "Case #": first.get("Case #", ""),
                "Time Frame": first["Time Frame"],
                "Search Type": first.get("Search Type", ""),
                "Search Date": first.get("Search Date", ""),
                "Search Time": first.get("Search Time Clean", ""),
                "Networks Queried": len(group),
                "Source File": first["Source File"],
            }
        )

    out = pd.DataFrame(sessions)
    out = out.sort_values(["Search Date", "Search Time"])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT, index=False)

    print(f"Deduplicated sessions: {len(out)}")
    print(f"Network hits collapsed: {len(raw) - len(out)}")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()