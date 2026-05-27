# Plan — GitHub Pages Static Site for Public Branch

## Goal

Publish a static site on GitHub Pages (served from the `public` branch → `main` on GitHub) that lets journalists, legal reviewers, and researchers explore the data behind the May 8, 2026 No Flock for SoPo press release — without cloning the repo.

## Why

`./run.sh` is great for auditors who want full reproducibility. Most people just want to see the numbers and understand the methodology. A static site makes the claims and evidence immediately accessible.

## Audience (from USER-EXPERIENCE.md)

1. **Journalists** — need claims + evidence links, fast
2. **Legal reviewers** — need provenance chains and methodology detail
3. **Researchers** — need reproducibility and raw data access

## Architecture

### Hosting

- GitHub Pages, served from the `public` branch (which is `main` on the GitHub remote)
- Built with a simple static-site generator, output goes to the repo root on the `public` branch
- No SPA, no JS framework — plain HTML + minimal CSS + inline data

### Tech choice: 11ty (Eleventy)

- Zero-JS output by default
- Markdown-first (we already have METHODOLOGY.md, VERIFICATION.md, synthesis.md)
- Tiny dependency footprint (`@11ty/eleventy` only)
- Builds to `_site/`; we copy `_site/` contents to branch root
- Alternative considered: hand-written HTML. Rejected because we have 7+ pages with shared layout — maintainability requires templating.

### Directory structure on public branch

```
/
├── index.html                    # Hero + 6 key claims + CTA
├── claims/                       
│   ├── 602-agencies.html         # Claim: 602+ agencies
│   ├── 44-states.html            # Claim: 44 states
│   ├── 70-ice-collaborators.html # Claim: 70+ 287(g) matches
│   ├── 2000-searches.html        # Claim: over 2,000 searches
│   ├── 107-cross-agency.html     # Claim: 107 cross-agency searches
│   └── nearly-two-thirds.html    # Claim: nearly two-thirds unnamed
├── methodology/                  
│   ├── overview.html             # Pipeline overview (5 steps)
│   ├── deduplication.html        # audit-logs-deduplicated METHODOLOGY
│   ├── 287g-crossindex.html      # crossindex METHODOLOGY + VERIFICATION
│   ├── assist-classification.html # assist-other METHODOLOGY
│   └── state-counting.html        # sppd-sharing-states methodology
├── data/                         # Raw CSV downloads (symlinks or copies from /data + /outputs)
├── reproducibility.html          # How to clone + run.sh
├── assets/
│   └── style.css                 # Minimal site-wide CSS
├── (existing public-branch files remain as-is: data/, outputs/, analysis/, etc.)
```

### Pages (7 content pages + index)

| # | Page | Primary content | Data source |
|---|------|-----------------|-------------|
| 1 | `index.html` | Hero statement + 6 claims as cards + "Verify yourself" CTA | synthesis.md |
| 2 | `claims/602-agencies.html` | 602 figure, SharedNetworks.csv snippet, methodology link | `data/derived/sppd-shared-networks-normalized.csv` |
| 3 | `claims/44-states.html` | State list, US map heatmap (CSS only, no JS) | `outputs/sppd-sharing-states/states.csv` |
| 4 | `claims/70-ice-collaborators.html` | Match table, confidence breakdown, manual-mapping note | `outputs/sppd-287g-crossindex/crossindex_results.csv` |
| 5 | `claims/2000-searches.html` | 2,007 raw / 1,572 deduped explanation | `outputs/audit-logs-deduplicated/` |
| 6 | `claims/107-cross-agency.html` | 67 assist-other + 40 statewide breakdown | `outputs/assist-other-agencies/assist-other-agencies.csv` |
| 7 | `claims/nearly-two-thirds.html` | 67/107 = 62.6% — calculation walkthrough | Same as #6 |
| 8 | `methodology/overview.html` | 5-step pipeline diagram + links to sub-pages | `run.sh` + all METHODOLOGY.md files |
| 9 | `reproducibility.html` | Clone + run instructions, SHA-256 verification | `run.sh`, `.governance.py` files |

### Design constraints

- **No JavaScript required** — all content renders server-side; interactive table sorting is nice-to-have, not required
- **Mobile-first** — journalists will check on phones
- **Dark-on-light** — maximizes readability for data tables
- **< 50 KB per page** — fast on slow connections
- **All data inline or in `/data/`** — no external API calls, no fetch at runtime
- **Cite every number** — each claim card links to the specific CSV column + methodology page

## Build & deploy workflow

### Source: `site/` directory on `main` (Forgejo)

```
site/
├── _data/                # Eleventy data files (CSV → JSON at build time)
├── _includes/            # Layouts, partials (nav, footer, claim-card)
├── claims/               # Markdown source for claim pages
├── methodology/           # Markdown source for methodology pages
├── index.md              # Homepage
├── reproducibility.md    # Clone+run page
├── assets/
│   └── style.css
└── .eleventy.js          # Config (output to ../_site)
```

### Build steps

1. `cd site/ && npx @11ty/eleventy` → writes to `_site/`
2. `_site/` contents get copied to the `public` branch root by `publish-to-github.sh` (extended)
3. Existing public-branch files (`data/`, `outputs/`, `analysis/`) remain — the site lives alongside them
4. GitHub Pages serves `index.html` from root

### Integration with `publish-to-github.sh`

Extend the script to:
1. Build the 11ty site (`cd site && npx @11ty/eleventy`)
2. Add `_site/**` to the allowlist (or hardcode the copy)
3. Copy `_site/` contents into the orphan branch before the final commit

This means the site is rebuilt fresh every publish — no stale HTML risk.

## Implementation order

| Step | Task | Depends on |
|------|------|-----------|
| 1 | Create `site/` directory with 11ty config, layout, and CSS | — |
| 2 | Build `_data/` pipeline: CSV → JSON at build time | Step 1 |
| 3 | Write `index.md` with claim cards | Step 2 |
| 4 | Write 6 claim pages (claims/*.md) | Step 3 |
| 5 | Write methodology pages | Step 2 |
| 6 | Write reproducibility page | — |
| 7 | Local build + manual QA | Steps 1–6 |
| 8 | Extend `publish-to-github.sh` to build + include site | Step 7 |
| 9 | Push to GitHub, verify GitHub Pages serves correctly | Step 8 |
| 10 | Add `docs/plans/` and `site/**` to `.public-allowlist` if needed | Step 9 |

## Decisions deferred

- **Custom domain vs `org.github.io/repo`**: Decide when we know the org name on GitHub
- **CSS framework vs hand-rolled**: Start hand-rolled (single `style.css`); add framework only if needed
- **US map on states page**: CSS-only simplified map, or skip map and use a state list. Implementation will tell.
- **Table interactivity (sort/filter)**: Nice-to-have; add `static-table.js` later if requested

## Out of scope

- Blog / news feed
- Search functionality
- User accounts / analytics
- Dynamic data visualizations (D3, Chart.js)
- Contact forms