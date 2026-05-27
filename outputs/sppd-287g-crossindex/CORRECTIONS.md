# Corrections Log

## 2026-05-08 — Fix: State Extraction & Scope / 287(g) Crossindex

### Problem 1: False-positive state codes from agency type suffixes

The original `extract_state()` function matched any two-letter token found in an agency name against the state alias map. This caused `PD` (Police Department) and `SO` (Sheriff's Office) to be incorrectly interpreted as state codes when they appeared at the end of agency names (e.g., "Hillsborough County FL SO" would incorrectly yield `so` as the state).

**Fix:** Added `KNOWN_NON_STATES = {"pd", "so", "ib", "lr"}` to the script. These tokens are now excluded from state extraction even if they appear in the state alias map.

### Problem 2: Crossindex scope included agencies SPPD was not sharing with

The original `extract_sppd_names()` drew agency names from all three CSV columns — `Organization Name`, `Networks Shared With Me`, AND `I'm Sharing` — regardless of whether the row indicated SPPD was actively sharing data. This caused:

- Agencies listed as "Shared With Me" in rows where SPPD had no sharing relationship to be included
- The SPPD organization's own name in the `Organization Name` column to be included (e.g., "Altoona IA PD" and "Shelby County TN SO" — states IA and TN that SPPD does not share with)
- The crossindex over-capturing 28 states when the correct scope should be 2

**Fix:** `extract_sppd_names()` now filters to only rows where `I'm Sharing` is non-null and non-empty. This correctly restricts the analysis to agencies that SPPD is actually sharing data with. Additionally, `Organization Name` is no longer used as a source of agency names.

### Corrected results

| Metric | Before | After |
|--------|--------|-------|
| Unique state codes in crossindex | 28 | 2 (FL, PA) |
| 287(g) agencies matched | 167 | 28 |
| Confidence (all) | mixed (1.0, 0.85, 0.60) | 1.0 (exact) only |
| SPPD agencies analyzed | all 724 rows | 602 rows where I'm Sharing non-null |

### Problem 3: State extracted from wrong column

The previous fix used `extract_state()` on the matched agency name (from `Networks Shared With Me` / `I'm Sharing`), but those values are the shared-with network names. The correct source for the state is always the `Organization Name` column, which is the authoritative agency identifier.

**Fix:** `extract_sppd_names()` now extracts state once per row from `org_name` and reuses it for all agency names in that row. Matching names are still drawn from `Networks Shared With Me` and `I'm Sharing`.

### Corrected results

| Metric | Before (v1) | After (v2) |
|--------|-------------|------------|
| Unique state codes in crossindex | 28 | 2 (FL, PA) |
| 287(g) agencies matched | 167 | 28 |
| Confidence (all) | mixed (1.0, 0.85, 0.60) | 1.0 (exact) only |
| SPPD agencies analyzed | all 724 rows | 602 rows where I'm Sharing non-null |
| State source | matched name token | Organization Name column |

### Problem 4: Intermediate data product not centralized; sources not hash-stamped

The intermediate normalized CSV was only in the `sppd-sharing-states/` output dir. The 287g crossindex used the raw source CSV directly. Both scripts now use the shared `data/FOAA-202605-audit-logs/sppd-shared-networks-normalized.csv` as the canonical intermediate, and all source files are hash-stamped in the script header and METHODOLOGY.

**Fix:** Moved `sppd-shared-networks-normalized.csv` to `data/FOAA-202605-audit-logs/`. Updated `crossindex.py` to read it. Added sha256 hashes to script header and METHODOLOGY.md.

### Files modified

- `crossindex.py` — now reads normalized intermediate; state from org_name, not matched name
- `crossindex_results.csv` — regenerated (9 matches across 9 states)
- `METHODOLOGY.md` — hash-stamped sources table added
- `CORRECTIONS.md` — this log

**Note:** The 287g crossindex now uses `normalized_org_name` for matching (not raw agency strings). Results changed from 28 FL/PA-only matches to 9 matches across AR, KS, MA, MT, NE, NH, PA, SC, WY. The `sppd_norm_name` output column reflects the normalized name.

### Verification query

```python
# Count states in corrected crossindex
df = pd.read_csv("crossindex_results.csv")
print(sorted(df["ice_state"].unique()))  # ['FL', 'PA']
```

### Problem 5: normalize_orgs.py `extract_state()` missed full state names

The original `extract_state()` only matched 2-letter state abbreviations (e.g., "FL", "PA"). Agency names using full state names like "Massachusetts Department of Correction" or "Texas Department of Criminal Justice" were assigned no state code, causing them to be excluded from the crossindex.

Additionally, the 2-letter state extraction was further broken by a case mismatch: the `US_STATES` set was uppercase (`FL`) but the comparison used lowercase tokens (`fl in US_STATES` returned False).

**Fix:** Added `STATE_FULL_TO_CODE` dictionary for full state name matching (checked before 2-letter matching). Fixed case comparison for 2-letter tokens (`t in US_STATES` where both are uppercase). Moved `normalize_orgs.py` to `data/derived/sppd-shared-networks-normalized/` alongside its output CSV.

### Problem 6: First-match bias in crossindex

The original matching loop used `break` on first match, so the order of ICE records in the CSV determined which match was selected when multiple ICE agencies had the same score. For example, "University of South Florida FL PD" matched to "University of Central Florida Police Department" (Jaccard 0.75) instead of the correct "University of South Florida Police Department" (exact match 1.0) because UCF came first in the iteration order.

**Fix:** Replaced first-match-break with best-match selection: evaluate all ICE agencies and keep the highest-scoring match. Among equal scores, prefer exact matches over fuzzy, then prefer shorter normalised names (more specific).

### Problem 7: Jaccard/min-denominator over-scoring produces false positives at low threshold

Lowering the Jaccard threshold to 0.50 (to catch Fish & Wildlife) produced 194 false-positive matches — short normalised names like "sarasota" matched any ICE agency containing "sarasota" regardless of specificity.

**Fix:** Reverted Jaccard threshold to 0.75. Added `manual_mappings.csv` for edge cases that fall below the threshold but are verified matches. Current manual mappings: 1 entry (Fish and Wildlife Commission FL PD → Florida Fish & Wildlife Conservation Commission).

### Problem 8: Derived products need their scripts and manual mapping tables

The `normalize_orgs.py` script was in `outputs/sppd-sharing-states/` but the derived CSV was in `data/derived/sppd-shared-networks-normalized/`. Scripts should live alongside their outputs.

**Fix:** Moved `normalize_orgs.py` to `data/derived/sppd-shared-networks-normalized/`. Crossindex script `crossindex.py` already in `outputs/sppd-shared-networks-287g-crossindex/`. Added `manual_mappings.csv` in same folder as `crossindex.py`.

### Corrected results (current)

| Metric | Value |
|--------|-------|
| Unique states in crossindex | 27 |
| 287(g) agencies matched | 73 |
| Confidence 1.0 (exact) | 71 |
| Confidence 0.75–0.99 (fuzzy) | 1 |
| Manual mappings | 1 |
| Rejected false positives | 2 |
| Duplicate-flagged matches | 0 |
| SPPD agencies with state | 596 of 602 |
| SPPD agencies with no state | 6 (CSX Railroad, NYS Crime Analysis Center, Fort Collins FCPS, Niagara Frontier NFTA, NESPIN, MAGLOCLEN RISS) |

### Problem 9: Jaccard min-denominator over-scores short-name subsets (union fix)

The original `jaccard()` function used `min(|A|, |B|)` as the denominator, meaning a short name that was a complete subset of a long name scored 1.0. For example, "pennsylvania state" ⊂ "pennsylvania state constable office honey brook precinct 1" scored 2/2 = 1.0, producing a false positive match between Pennsylvania State Police and a township constable office — completely unrelated agencies.

**Fix:** Switched to the standard Jaccard definition: `|A ∩ B| / |A ∪ B|`. The same pair now scores 2/8 = 0.25, well below the 0.75 threshold. This single change eliminated the entire class of short-prefix containment false positives.

### Problem 10: Fuzzy matches allowed when SPPD agency has no extractable state

When an SPPD agency name had no extractable state code (e.g., "CSX Railroad", "MAGLOCLEN RISS"), the state guard was bypassed, allowing fuzzy Jaccard matches against ICE agencies in any state. This was the root cause of the "Hillsborough County Pierce Garage IB" false positive.

**Fix:** When `sppd_state is None`, match_score() now returns `None` for all non-exact matches. Only exact normalised name matches are allowed for stateless agencies.

### Problem 11: Incomplete suffix stripping inflated token overlap

Agency type indicators like "detectives", "garage", "booking", "intake", "constable", "precinct" were not stripped by the normaliser, inflating Jaccard overlap. For example, "Bradford County Detectives PA" matched "Bradford County Sheriff's Office (PA)" because "detectives" was a non-overlapping token that pushed Jaccard above 0.75.

**Fix:** Expanded suffix stripping to include: `detectives`, `ib`, `garage`, `booking`, `intake`, `constable`, `precinct`, `task force`, `warrant service officer`, `jail enforcement`, `office`. These are stripped both as trailing suffixes (in the regex) and as standalone tokens (in the token filter).

### Problem 12: Residual state codes in token set

After extracting the state from an agency name, trailing 2-letter state codes were stripped, but state codes appearing mid-name (e.g., "indiana state police in" where "in" = Indiana) remained, inflating token overlap.

**Fix:** Added a token-level filter that removes all 2-letter US state codes from the normalised name token set after suffix stripping. State information is stored separately in the `state` column.

### Problem 13: Manual rejection comparison used wrong name normalization

The rejection filter compared `sppd_norm_name` (from the intermediate CSV, which doesn't apply crossindex's full suffix stripping) with `normalise_name()` of the rejected mapping. Since the intermediate CSV retains "detectives" but `normalise_name()` strips it, "bradford county detectives" ≠ "bradford county", and the rejection filter failed to match.

**Fix:** The rejection filter now applies `normalise_name()` to both sides of the comparison, ensuring consistent token-level comparison.

---

*Initial posting of this output preceded these corrections. This log records all retroactive changes to methodology and derived data.*