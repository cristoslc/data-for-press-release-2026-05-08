---
source-type: primary
primary-evidence: true
chain: "FOIA'd from South Portland PD via Muckrock → audit log spreadsheet deduplicated → this script classifies assist-other patterns"
---

## Methodology: Flagging "Assist Other Agencies" in South Portland Flock Audit Logs

### Objective
Identify audit log entries where a South Portland officer ran a license plate search in the Flock system while assisting or coordinating with another law enforcement agency — as opposed to their own agency's primary investigations.

### Source Data
- File: `outputs/audit-logs-deduplicated/sopo-flock-audit-deduped.csv`
- Rows: 1,572 (after deduplication)
- Key field used: `Reason` (free-text search justification entered by the officer)

### Classification Logic

The classifier scans the `Reason` field using regular expressions targeting two categories:

#### Category 1 — `assist-other` (67 hits)
Explicit language indicating cross-agency assistance:
- `assist other` / `assist  other` (with or without extra spaces, lowercase variants)
- Phrases like `"File 1"` paired with another named agency (e.g., `"Auburn file 1"`, `"Scarborough file 1"`, `"Portland file 1"`)
- Specific multi-agency mentions: `"Extortion/Blackmail - Assist other agency investigation"`, `"Burglary/Breaking & Entering - File 1/Burglary assist for WPD"`, `"Drugs/Narcotics - drug investigation/ assist other agency"`

#### Category 2 — `statewide-system` (40 hits)
Searches routed through statewide information-sharing systems that by design serve multi-agency coordination:
- `MIAC` (Maine Information Analysis Center)
- `MDEA` (Maine Drug Enforcement Agency)
- `MSP` (Maine State Police)
- Case-insensitive and variantly-spaced variants of the above (e.g., `"Miac"`, `"mdea"`, `"MIAC MDEA"`, `"MDEA - MIAC"`)

### Important Caveats

1. **Not all MIAC/MDEA entries are cross-agency** — some may be South Portland officers using statewide systems to query their own cases. The `statewide-system` label is a proxy for multi-agency information sharing, not a confirmed assist.
2. **"File 1" is ambiguous** — can mean an active investigative file within South Portland, or a file number assigned by another agency (e.g., `"Portland file 1"` = Portland PD's File 1). Context matters; the script conservatively flags any cross-agency mention.
3. **Reason text is self-reported** — no verification against case records has been performed.
4. **Does not capture all assist activity** — searches conducted under a South Portland case number that happen to assist another agency would not be flagged here.

### Output
- `assist-other-agencies.csv` — all 107 flagged rows with added columns:
  - `assist_label`: category (`assist-other` or `statewide-system`)
  - `assist_pattern`: the regex pattern that matched
- `classify_assist_other.py` — the classifier script (Python, no external dependencies beyond pandas)
- `METHODOLOGY.md` — this document

### Running the Script
```bash
uv run --with pandas python3 classify_assist_other.py
```