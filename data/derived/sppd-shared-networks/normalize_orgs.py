#!/usr/bin/env python3
"""
Normalize the Organization Name column from SharedNetworks_2026_May_5.csv
into: original_org_name, normalized_org_name, state

Only rows where SPPD is actively sharing (I'm Sharing non-null) are included.

Source (hash-stamped):
  SharedNetworks_2026_May_5.csv
    sha256:75729defe7be5ad5454423b815fba159bb456675813dec41fa1e7342f440c19c
"""

import hashlib
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.parent.parent.parent
INPUT = (
    ROOT
    / "data"
    / "sppd-foaa-2026-audit-logs"
    / "raw-monthly"
    / "SharedNetworks_2026_May_5.csv"
)
OUTPUT = Path(__file__).parent / "sppd-shared-networks-normalized.csv"

US_STATES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "DC",
}

STATE_FULL_TO_CODE = {
    "alabama": "al",
    "alaska": "ak",
    "arizona": "az",
    "arkansas": "ar",
    "california": "ca",
    "colorado": "co",
    "connecticut": "ct",
    "delaware": "de",
    "florida": "fl",
    "georgia": "ga",
    "hawaii": "hi",
    "idaho": "id",
    "illinois": "il",
    "indiana": "in",
    "iowa": "ia",
    "kansas": "ks",
    "kentucky": "ky",
    "louisiana": "la",
    "maine": "me",
    "maryland": "md",
    "massachusetts": "ma",
    "michigan": "mi",
    "minnesota": "mn",
    "mississippi": "ms",
    "missouri": "mo",
    "montana": "mt",
    "nebraska": "ne",
    "nevada": "nv",
    "new hampshire": "nh",
    "new jersey": "nj",
    "new mexico": "nm",
    "new york": "ny",
    "north carolina": "nc",
    "north dakota": "nd",
    "ohio": "oh",
    "oklahoma": "ok",
    "oregon": "or",
    "pennsylvania": "pa",
    "rhode island": "ri",
    "south carolina": "sc",
    "south dakota": "sd",
    "tennessee": "tn",
    "texas": "tx",
    "utah": "ut",
    "vermont": "vt",
    "virginia": "va",
    "washington": "wa",
    "west virginia": "wv",
    "wisconsin": "wi",
    "wyoming": "wy",
    "district of columbia": "dc",
}

KNOWN_NON_STATES = {"pd", "so", "ib", "lr"}

TYPE_TOKENS_RE = re.compile(
    r"\s+(pd|police\s*dept|police\s*department|so|sheriff('s)?\s*office|"
    r"sheriff|county\s*sheriff|city|town|village|borough|township|campus|"
    r"college|university|system|center|network|district|corrections|jail|"
    r"prison|facility|board|commission|agency|unit|service|services|authority|"
    r"police|department|office|division|bureau|command|ofs|of\s+the|at\s+large)$",
    re.IGNORECASE,
)

PD_SO_RE = re.compile(r"\b(PD|SO|PD\s*\(|\(\s*PD)\b")


def normalize_name(name: str) -> str:
    n = name.lower().strip()
    n = TYPE_TOKENS_RE.sub("", n)
    n = PD_SO_RE.sub("", n)
    n = re.sub(r"[^\w\s]", "", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def extract_state(name: str) -> str | None:
    lower = name.lower().strip()
    for full, code in STATE_FULL_TO_CODE.items():
        if re.search(r"\b" + re.escape(full) + r"\b", lower):
            return code
    tokens = re.findall(r"\b([A-Z]{2})\b", name)
    for t in tokens:
        if t in US_STATES and t.lower() not in KNOWN_NON_STATES:
            return t.lower()
    return None


def strip_state_suffix(name: str) -> str:
    stripped = re.sub(r"\s+[A-Z]{2}\s*$", "", name.strip()).strip()
    for full in sorted(STATE_FULL_TO_CODE, key=len, reverse=True):
        stripped = re.sub(
            r"\s+" + re.escape(full) + r"\s*$", "", stripped, flags=re.IGNORECASE
        ).strip()
    return stripped


def main():
    with INPUT.open("rb") as f:
        source_hash = hashlib.sha256(f.read()).hexdigest()
    print(f"Source hash: {source_hash}")

    df = pd.read_csv(INPUT)
    df_sharing = df[
        df["Networks I'm Sharing"].notna()
        & (df["Networks I'm Sharing"].str.strip() != "")
    ].copy()

    rows = []
    seen = set()
    for _, row in df_sharing.iterrows():
        org = str(row["Organization Name"]).strip()
        if not org or org in seen:
            continue
        seen.add(org)
        state = extract_state(org)
        norm = normalize_name(strip_state_suffix(org))
        rows.append(
            {
                "original_org_name": org,
                "normalized_org_name": norm,
                "state": state,
                "networks_im_sharing": row["Networks I'm Sharing"],
            }
        )

    out = pd.DataFrame(rows)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT, index=False)

    with OUTPUT.open("rb") as f:
        output_hash = hashlib.sha256(f.read()).hexdigest()

    print(f"Written: {OUTPUT}")
    print(f"Output hash: {output_hash}")
    print(f"Rows: {len(out)}")
    no_state = out[out["state"].isna()]
    print(f"Rows with no state: {len(no_state)}")
    if len(no_state) > 0:
        for _, r in no_state.iterrows():
            print(f"  {r['original_org_name']}")
    print(f"States: {sorted(v for v in out['state'] if pd.notna(v))}")


if __name__ == "__main__":
    main()
