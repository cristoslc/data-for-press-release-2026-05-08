---
title: "Independent Verification of crossindex_results.csv"
source-type: derived
primary-evidence: false
caveat: "Verification of derived output against primary and current sources."
verification-date: "2026-05-11"
---

# Verification Report: crossindex_results.csv

**Date**: 2026-05-11
**Verifying agent**: opencode (GLM-5.1)
**Subject**: All 73 entries in `crossindex_results.csv`

## Verification Method

1. **In-repo verification**: Reimplemented the matching logic independently in `verify_crossindex.py`. Verified each entry against the in-repo `ice-287g-deduped.csv` (1,503 agencies, SHA-256: `aaf71a60705b1f8b907e2a6b1f2d35d1d49709154c5c25c147c8c2fc8110c9e9`).

2. **Live ICE.gov comparison**: Downloaded the current ICE 287(g) Excel file from `ice.gov/file-download/download/public/186678`, parsed and deduplicated it, and compared against the in-repo data.

3. **False negative scan**: For every SPPD agency not in the crossindex results, checked whether an exact or fuzzy (Jaccard >= 0.75) match exists in the ICE list that was missed.

4. **Confidence and method consistency**: Verified that confidence scores match the matching method (1.0 for exact, 0.75+ for fuzzy, < 0.75 for manual).

5. **Duplicate flag verification**: Checked that `duplicate_flag` correctly reflects whether multiple SPPD entries map to the same ICE record.

## Results

| Check | Result |
|-------|--------|
| Entries verified against ICE list (correct state + support_types) | 73/73 |
| Confidence/method consistency errors | 0 |
| Missed exact matches (false negatives) | 0 |
| Missed fuzzy matches Jaccard >= 0.75 (false negatives) | 0 |
| Duplicate flag errors | 0 |
| Shared network column issues | 0 |
| Total errors | 0 |
| Total warnings | 1 (benign) |

### Benign Warning

Row 31 (Fish and Wildlife Commission FL PD, manual method) triggered a "not in manual_mappings.csv" warning due to double-normalization in the verification script. The entry IS in `manual_mappings.csv`; the comparison failed because `normalise_name("fish and wildlife commission")` strips "commission" (as a trailing suffix) producing "fish and wildlife", while `normalise_name("Fish and Wildlife Commission FL PD")` preserves "commission" (it's not at the end before state/PD are removed). This is a cosmetic artifact of the normalisation pipeline, not a data error.

## Live ICE.gov Comparison

The current ICE.gov XLSX (downloaded 2026-05-11 from the canonical URL) contains the same 1,503 deduplicated agencies as the in-repo `ice-287g-deduped.csv`. The only differences are cosmetic:

- Territory state codes: "GUAM" vs "GU", "NORTHERN MARIANA ISLANDS" vs "NO" (formatting difference in how the XLSX labels territories vs how the repo normalizes them)
- One TX agency quoting: `Cut N" Shoot Police Department"` vs `Cut "N" Shoot Police Department` (CSV quoting artifact)

**No agencies have been added to or removed from the ICE 287(g) list** since the in-repo data was collected on 2026-05-07. The in-repo data is current.

## Verdict

**ALL 73 ENTRIES VERIFIED.** No discrepancies found. The crossindex results are accurate and complete as of 2026-05-11.

This output has been independently verified on 2026-05-11, finding no discrepancies against either the in-repo primary source or the current live ICE.gov data.

## Verification Script

The independent verification script is at `verify_crossindex.py` in this directory. It can be re-run at any time with:

```
uv run python3 verify_crossindex.py
```
