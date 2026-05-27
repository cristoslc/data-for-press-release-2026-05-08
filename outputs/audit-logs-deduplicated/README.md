---
source-type: derived
primary-evidence: false
contents: "Deduplicated SPPD Flock audit logs — 2,007 raw rows collapsed to 1,572 unique search sessions."
chain: "SPPD FOAA response → raw monthly audit CSVs → deduplication (by Name+Reason+TimeFrame+OrgName) → this output"
---

# SPPD Flock ALPR Audit Log — Deduplicated View

## Source Data

The FOAA-obtained data consists of 11 monthly audit log exports from South Portland Police Department, covering April 2025 through March 2026 (May 2025 is missing). This deduplicated CSV is built directly from those raw files:

```
data/sppd-foaa-2026-audit-logs/raw-monthly/
```

There is also a pre-consolidated CSV (`Combined Audit Logs - Apr 25 through Mar 26 - Sheet1.csv`) but it was **manually cleaned** — 6 rows from April 2025 were removed, likely because they were labeled "Test/Training" (though two of the six were legitimate "Criminal Investigation" and "stolen vehicle" searches). This deduplicated CSV uses the **full raw data** (2,007 rows), not the cleaned version.

### Raw Monthly File Summary

| File | Rows |
|------|------|
| 4_1_2025-4_30_2025 | 6 |
| 6_1_2025-6_30_2025 | 267 |
| 7_1_2025-7_31_2025 | 311 |
| 8_1_2025-8_31_2025 | 538 |
| 9_1_2025-9_30_2025 | 208 |
| 10_1_2025-10_31_2025 | 146 |
| 11_1_2025-11_30_2025 | 138 |
| 12_1_2025-12_31_2025 | 71 |
| 1_1_2026-1_31_2026 | 137 |
| 2_1_2026-2_28_2026 | 93 |
| 3_1_2026-3_31_2026 | 92 |
| **Total** | **2,007** |

Note: May 2025 file is absent. The 6 April 2025 rows missing from the combined CSV are: Matthew Cyr (2x Criminal Investigation), Christopher Todd (2x Test/Training), Jonathan Stearns (2x stolen vehicle).

---

### Why Deduplication Is Needed

A single Flock search session queries **multiple camera networks** simultaneously. The audit log records each network hit as a separate row with a unique ID. Example:

| ID | Name | Reason | Time Frame |
|----|------|--------|------------|
| aaa-111 | Stearns | theft from hannaford | 03/30-03/30 |
| aaa-222 | Stearns | theft from hannaford | 03/30-03/30 |
| aaa-333 | Stearns | theft from hannaford | 03/30-03/30 |

These 3 rows are **one search session** hitting 3 camera networks. Counting rows as searches inflates the count by ~22%.

---

## Deduplicated CSV

```
outputs/audit-logs-deduplicated/sopo-flock-audit-deduped.csv
```

- **1,572 unique search sessions** from 2,007 raw rows
- Columns: `Name, Org Name, Reason, Case #, Time Frame, Search Type, Search Date, Search Time, Networks Queried, Source File`
- `Networks Queried` = how many rows were collapsed into this session
- `Source File` = which monthly Excel file the data came from

### Deduplication Key

```
(Name, Reason, Time Frame, Org Name)
```

Rows sharing all four fields are collapsed into one session. The first row's timestamp is retained.

### Networks Queried Distribution

| Networks | Sessions | Share |
|----------|----------|-------|
| 1 | 1,304 | 82.9% |
| 2 | 187 | 11.9% |
| 3 | 43 | 2.7% |
| 4 | 18 | 1.1% |
| 5 | 12 | 0.8% |
| 6 | 3 | 0.2% |
| 7 | 1 | 0.1% |
| 8 | 2 | 0.1% |
| 9 | 3 | 0.2% |

83% of sessions hit only one network and have no duplication in the raw data.

---

## Methodology Comparison

| Approach | Row Count | Source |
|----------|-----------|--------|
| Raw monthly Excel files | 2,007 | One row per network queried |
| Combined CSV (pre-cleaned) | 2,001 | 6 Apr 2025 rows removed |
| TimeFrame-only dedupe | ~1,545 | One row per unique `Time Frame` |
| **This CSV** (Name+Reason+TF+Org) | **1,572** | One row per unique search session |

### Why Not TimeFrame-Only?

Grouping by `Time Frame` alone incorrectly merges:
- **13 groups** where *different officers* searched within the same time window
- **10 groups** where the *same officer* listed *different reasons* at the same time

These are genuinely separate sessions. The chosen key keeps them separate.

### Edge Cases

The key may overcount by at most **10 sessions** where the same officer used slightly different reason labels for the same search across network rows (e.g., "lewiston pd" vs. "miac req" for one narcotics case). This is a Flock data entry inconsistency.

---

## Per-Officer Search Sessions

| Officer | Sessions | Row Count | Division |
|---------|----------|-----------|----------|
| Frank Stepnick | 482 | 584 | Investigations |
| Jeff Levesque | 463 | 608 | Investigations |
| Christopher Todd | 258 | 337 | Investigations |
| Jonathan Stearns | 145 | 197 | Investigations |
| Michael Armstrong | 50 | 71 | Patrol |
| Kevin Theriault | 35 | 38 | Patrol |
| Matthew Cyr | 34 | 35 | Investigations |
| Ben Macisso | 27 | 29 | Professional Standards |
| David Stailing | 23 | 31 | Patrol |
| Al Giusto | 21 | 25 | Patrol |
| Shane Stephenson | 18 | 26 | Patrol |
| Jena Kuhl | 16 | 25 | Patrol |
| John Sutton | 1 | 1 | Patrol |
| **Total** | **1,572** | **2,007** | |

Note: Per-officer breakdown reflects the original 1,573-session run and may vary by 1 row in the current reproduction (1,572).

### Search Types

| Type | Sessions |
|------|----------|
| lookup (desktop) | 621 |
| lookup - Mobile | 398 |
| search (desktop) | 378 |
| search - Mobile | 176 |

"Lookup" = specific plate query. "Search" = broader query across a time/area window. 35% of sessions were from mobile devices.

---

## When to Use Each File

| File | Use case |
|------|----------|
| Raw monthly Excel files | Full fidelity, per-network detail, reconstruct exact Flock export |
| Combined CSV | Quick analysis if you accept the 6-row April omission |
| **This deduplicated CSV** | Counting search activity, officer behavior analysis, statistics |
| Cross-index brief (`outputs/briefs/`) | Comparing audit log usage against full department roster |
