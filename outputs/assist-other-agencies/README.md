---
source-type: derived
primary-evidence: false
contents: "Classification of 'assist other agencies' rows in SPPD Flock audit logs."
chain: "SPPD FOAA response → audit CSVs → classify_assist_other.py → this output"
---

## sppd-assist-other-agencies

Identifies rows in SPPD's Flock audit logs where the search reason is "Assist Other Agency" and classifies which agencies were assisted.

**Source:** `outputs/audit-logs-deduplicated/sopo-flock-audit-deduped.csv`

**Script:** `classify_assist_other.py`

## assist-other-agencies

Classifies South Portland Flock audit log entries indicating officers assisting or coordinating with other law enforcement agencies.

**Contents:**
- `classify_assist_other.py` — Python classifier script
- `METHODOLOGY.md` — detailed classification logic and caveats
- `assist-other-agencies.csv` — derived output: 107 flagged rows