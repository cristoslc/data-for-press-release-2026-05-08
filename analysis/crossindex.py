#!/usr/bin/env python3
"""
Cross-index agencies in South Portland's Flock shared network against ICE 287(g) participant list.

Primary sources (hash-stamped at time of processing):
  SharedNetworks_2026_May_5.csv
    sha256:75729defe7be5ad5454423b815fba159bb456675813dec41fa1e7342f440c19c
  ice-287g-deduped.csv
    sha256:aaf71a60705b1f8b907e2a6b1f2d35d1d49709154c5c25c147c8c2fc8110c9e9

Intermediate data source:
  data/derived/sppd-shared-networks/sppd-shared-networks-normalized.csv
    (derived from SharedNetworks_2026_May_5.csv; produced by normalize_orgs.py)
    Regenerate hash: uv run python3 -c "import hashlib; print(hashlib.sha256(open('sppd-shared-networks-normalized.csv','rb').read()).hexdigest())"

Output:
  crossindex_results.csv: agencies that are BOTH in SPPD's shared network
  AND have a 287(g) agreement, with confidence score and match method.
"""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT_DIR = Path(__file__).parent
SPPD_NORMALIZED = (
    ROOT
    / "data"
    / "derived"
    / "sppd-shared-networks"
    / "sppd-shared-networks-normalized.csv"
)
ICE_CSV = (
    ROOT
    / "data"
    / "ice-287g"
    / "ice-287g-deduped.csv"
)
MANUAL_MAP_CSV = SCRIPT_DIR / "manual_mappings.csv"
OUTPUT_CSV = ROOT / "outputs" / "sppd-287g-crossindex" / "crossindex_results.csv"

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


STRIP_WORDS = {
    "pd",
    "so",
    "lr",
    "condor",
    "flex",
    "detectives",
    "garage",
    "booking",
    "intake",
    "constable",
    "precinct",
    "office",
    "task force",
    "warrant service officer",
    "jail enforcement",
}


def normalise_name(name: str) -> str:
    name = name.lower().strip()
    name = re.sub(
        r"\s+(pd|police\s*dept|police\s*department|so|sheriff('s)?\s*office|"
        r"sheriff|county\s*sheriff|city|town|village|borough|township|campus|"
        r"college|university|system|center|network|district|corrections|jail|"
        r"prison|facility|board|commission|agency|unit|service|services|authority|"
        r"police|department|office|division|bureau|command|ofs|of\s+the|at\s+large|"
        r"detectives|garage|booking|intake|constable|precinct|"
        r"task\s+force|warrant\s+service\s+officer|jail\s+enforcement)$",
        "",
        name,
        flags=re.IGNORECASE,
    )
    name = re.sub(r"\b(PD|SO|LR|PD\s*\(|\(\s*PD)\b", "", name)
    name = re.sub(r"[^\w\s]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    tokens = name.split()
    tokens = [t for t in tokens if t not in STRIP_WORDS]
    state_codes_lower = {s.lower() for s in US_STATES}
    tokens = [t for t in tokens if t not in state_codes_lower]
    name = " ".join(tokens)
    tail_state = re.search(r"\s+[a-z]{2}\s*$", name)
    if tail_state and tail_state.group().strip() in state_codes_lower:
        name = name[: tail_state.start()].strip()
    return name


def jaccard(s1: str, s2: str) -> float:
    a = set(s1.split())
    b = set(s2.split())
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load_sppd_normalized(path: Path) -> list[tuple[str, str, str | None, str]]:
    records = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                (
                    row.get("original_org_name", "").strip(),
                    row.get("normalized_org_name", "").strip(),
                    row.get("state", "").strip() or None,
                    row.get("networks_im_sharing", "").strip(),
                )
            )
    return records


def load_ice(path: Path) -> list[tuple[str, str, str]]:
    records = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(
                (
                    row.get("state", "").strip(),
                    row.get("agency", "").strip(),
                    row.get("support_types", "").strip(),
                )
            )
    return records


def load_manual_mappings(path: Path) -> tuple[list[dict], list[dict]]:
    if not path.exists():
        return [], []
    accepted = []
    rejected = []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = {
                "sppd_original_name": row.get("sppd_original_name", "").strip(),
                "ice_agency": row.get("ice_agency", "").strip(),
                "ice_state": row.get("ice_state", "").strip().upper(),
                "support_types": row.get("support_types", "").strip(),
                "confidence": float(row.get("confidence", "0.0")),
                "verdict": row.get("verdict", "accepted").strip().lower(),
                "notes": row.get("notes", "").strip(),
            }
            if entry["verdict"] == "rejected":
                rejected.append(entry)
            else:
                accepted.append(entry)
    return accepted, rejected


def match_score(
    sppd_norm: str, sppd_state: str | None, ice_agency: str, ice_state: str
) -> float | None:
    if sppd_state is not None and ice_state.lower() != sppd_state:
        return None

    n_sppd = normalise_name(sppd_norm)
    n_ice = normalise_name(ice_agency)

    if not n_sppd or not n_ice:
        return None

    if n_sppd == n_ice:
        return 1.0

    if sppd_state is None:
        return None

    score = jaccard(n_sppd, n_ice)
    if score >= 0.75:
        return round(score, 2)

    return None


def main():
    print("Loading SPPD normalized shared-network data...")
    sppd_names = load_sppd_normalized(SPPD_NORMALIZED)
    print(f"  {len(sppd_names)} unique agency names from SPPD shared network")

    print("Loading ICE 287(g) data...")
    ice_records = load_ice(ICE_CSV)
    print(f"  {len(ice_records)} 287(g) agencies on ICE official list")

    print("Loading manual mappings...")
    manual_accepted, manual_rejected = load_manual_mappings(MANUAL_MAP_CSV)
    print(f"  {len(manual_accepted)} accepted, {len(manual_rejected)} rejected")

    matches: list[dict] = []

    for _, sppd_norm, sppd_state, sppd_sharing in sppd_names:
        best: dict | None = None
        for ice_state, ice_agency, support in ice_records:
            score = match_score(sppd_norm, sppd_state, ice_agency, ice_state)
            if score is None:
                continue
            n_ice = normalise_name(ice_agency)
            n_sppd = normalise_name(sppd_norm)
            is_exact = n_sppd == n_ice
            candidate = {
                "sppd_norm_name": sppd_norm,
                "ice_agency": ice_agency,
                "ice_state": ice_state.upper(),
                "support_types": support,
                "confidence": score,
                "match_method": "automated",
                "shared_network": sppd_sharing,
                "_is_exact": is_exact,
                "_norm_len": len(n_ice.split()),
            }
            if best is None:
                best = candidate
            elif score > best["confidence"]:
                best = candidate
            elif score == best["confidence"]:
                if is_exact and not best["_is_exact"]:
                    best = candidate
                elif (
                    is_exact == best["_is_exact"]
                    and len(n_ice.split()) < best["_norm_len"]
                ):
                    best = candidate
        if best is not None:
            del best["_is_exact"]
            del best["_norm_len"]
            matches.append(best)

    for rej in manual_rejected:
        matches = [
            m
            for m in matches
            if not (
                normalise_name(m["sppd_norm_name"])
                == normalise_name(rej["sppd_original_name"])
                and m["ice_agency"] == rej["ice_agency"]
            )
        ]

    norm_to_sharing = {
        normalise_name(norm): sharing for _, norm, _, sharing in sppd_names
    }

    for mm in manual_accepted:
        already = any(
            normalise_name(m["sppd_norm_name"])
            == normalise_name(mm["sppd_original_name"])
            for m in matches
        )
        if already:
            continue
        mm_sppd_norm = normalise_name(mm["sppd_original_name"])
        matches.append(
            {
                "sppd_norm_name": mm_sppd_norm,
                "ice_agency": mm["ice_agency"],
                "ice_state": mm["ice_state"],
                "support_types": mm["support_types"],
                "confidence": mm["confidence"],
                "match_method": "manual",
                "shared_network": norm_to_sharing.get(mm_sppd_norm, ""),
            }
        )

    print(f"\nMatched {len(matches)} SPPD network agencies to 287(g) participants")

    from collections import Counter

    ice_duplicate = Counter((m["ice_agency"], m["ice_state"]) for m in matches)
    for m in matches:
        m["duplicate_flag"] = ice_duplicate[(m["ice_agency"], m["ice_state"])] > 1

    matches.sort(key=lambda x: (x["ice_state"], -x["confidence"], x["ice_agency"]))

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "sppd_norm_name",
        "ice_agency",
        "ice_state",
        "support_types",
        "confidence",
        "match_method",
        "duplicate_flag",
        "shared_network",
    ]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(matches)

    print(f"\nResults written to: {OUTPUT_CSV}")

    from collections import Counter

    state_counts = Counter(m["ice_state"] for m in matches)
    conf_counts = Counter(m["confidence"] for m in matches)
    method_counts = Counter(m["match_method"] for m in matches)
    print(f"Total matched: {len(matches)}")
    print("\nBy state:")
    for state, count in sorted(state_counts.items(), key=lambda x: -x[1]):
        print(f"  {state}: {count}")
    print("\nBy confidence tier:")
    for score, count in sorted(conf_counts.items(), key=lambda x: -x[0]):
        label = {1.0: "exact", 0.75: "jaccard≥0.75"}.get(score, str(score))
        print(f"  {score} ({label}): {count}")
    print("\nBy match method:")
    for method, count in sorted(method_counts.items(), key=lambda x: -x[1]):
        print(f"  {method}: {count}")
    dup_count = sum(1 for m in matches if m["duplicate_flag"])
    print(
        f"\nDuplicate-flagged matches (multiple SPPD agencies → same ICE record): {dup_count}"
    )


if __name__ == "__main__":
    main()
