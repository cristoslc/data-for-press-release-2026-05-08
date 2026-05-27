# SPPD Flock Shared Network x ICE 287(g) — Excel Methodology Workbook

## Contents

- `sppd-287g-crossindex-methodology.xlsx` — Self-contained Excel workbook that reproduces the cross-index analysis using simple formulas
- `sppd-287g-crossindex-methodology.pdf` — Methodology & reproduction guide (PDF)
- `build_workbook.py` — Script that reads the normalized CSVs and produces the workbook
- `build_pdf.py` — Script that generates the PDF methodology document
- `README.md` — This file

## Workbook Sheets

| Sheet | Purpose |
|-------|---------|
| Read Me | Methodology overview, formula inventory, instructions |
| SPPD Normalized | 602 SPPD shared-network agencies (original + normalized names, extracted states) |
| ICE 287(g) | 1,503 ICE 287(g) agencies with pre-computed normalized core names |
| Pairs & Jaccard | 30,514 same-state SPPD×ICE pairs with Jaccard scores |
| Best Matches | Per-SPPD-agency best ICE match (live formula: change H2 threshold) |
| Manual Mappings | Hand-validated accepted/rejected pairs |
| Final Results | 73 matched agencies — the cross-index output |
| State Counts | 44 US states in SPPD's sharing network with ICE presence flags |
| Jaccard Demo | Step-by-step intersection/union walkthrough for 5 example pairs |

## Key Formula

Change cell `H2` on the "Best Matches" sheet from `0.75` to any other value (e.g. `0.80`) to see the threshold effect. All `=IF(G>=H$2,...)` formulas update automatically.
