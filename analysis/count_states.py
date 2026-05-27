#!/usr/bin/env python3
"""
Count unique US states from the normalized shared-networks intermediate.

Reads: data/derived/sppd-shared-networks/sppd-shared-networks-normalized.csv
Produced by: data/derived/sppd-shared-networks/normalize_orgs.py
Source: SharedNetworks_2026_May_5.csv
  sha256:75729defe7be5ad5454423b815fba159bb456675813dec41fa1e7342f440c19c
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent
INPUT = (
    ROOT
    / "data"
    / "derived"
    / "sppd-shared-networks"
    / "sppd-shared-networks-normalized.csv"
)

US_STATES_LOWER = {
    "al",
    "ak",
    "az",
    "ar",
    "ca",
    "co",
    "ct",
    "de",
    "fl",
    "ga",
    "hi",
    "id",
    "il",
    "in",
    "ia",
    "ks",
    "ky",
    "la",
    "me",
    "md",
    "ma",
    "mi",
    "mn",
    "ms",
    "mo",
    "mt",
    "ne",
    "nv",
    "nh",
    "nj",
    "nm",
    "ny",
    "nc",
    "nd",
    "oh",
    "ok",
    "or",
    "pa",
    "ri",
    "sc",
    "sd",
    "tn",
    "tx",
    "ut",
    "vt",
    "va",
    "wa",
    "wv",
    "wi",
    "wy",
    "dc",
}


def main():
    df = pd.read_csv(INPUT)
    states = sorted(v for v in df["state"].dropna().unique() if v in US_STATES_LOWER)
    no_state = df[df["state"].isna()]
    print(f"Unique US states: {states}")
    print(f"Count: {len(states)}")
    print(f"Rows with no state: {len(no_state)}")
    if len(no_state) > 0:
        for _, r in no_state.iterrows():
            print(f"  {r['original_org_name']}")


if __name__ == "__main__":
    main()
