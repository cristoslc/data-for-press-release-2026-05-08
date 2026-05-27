---
source-type: primary
primary-evidence: true
chain: "FOIA response from SPPD via Muckrock → SharedNetworks_2026_May_5.csv (sha256:75729def) → normalized to sppd-shared-networks-normalized.csv (sha256:3f3d5011)"
---

## sppd-sharing-states

Identifies the unique US states represented in SPPD's active Flock sharing network.

**Source (hash-stamped):**
- `SharedNetworks_2026_May_5.csv` — sha256:`75729defe7be5ad5454423b815fba159bb456675813dec41fa1e7342f440c19c`
- Intermediate: `data/derived/sppd-shared-networks/sppd-shared-networks-normalized.csv` — sha256:`3f3d50115729d3b05eb73118bd4021a8470daf85d8a8d66ff4ed764da7d5f4fd`

**Scope:** Rows where `Networks I'm Sharing` is non-null (602 agencies SPPD shares data with).

**Intermediate data products** (in `data/derived/sppd-shared-networks/`):
- `sppd-shared-networks-normalized.csv` — `original_org_name`, `normalized_org_name`, `state`
- `org_name_state_sharing.csv` — `original_org_name`, `state`, `networks_im_sharing` (from `outputs/sppd-sharing-states/`)

**Scripts:**
- `normalize_orgs.py` — produces the shared `sppd-shared-networks-normalized.csv` in `data/derived/sppd-shared-networks/`
- `count_states.py` — reads the normalized CSV and counts unique states

**Result:** 44 unique US states across 602 agencies SPPD shares data with