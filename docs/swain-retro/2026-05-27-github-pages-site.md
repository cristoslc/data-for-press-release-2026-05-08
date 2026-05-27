---
title: "Retro: GitHub Pages Static Site with Encryption Gate"
artifact: RETRO-2026-05-27-github-pages-site
track: standing
status: Active
created: 2026-05-27
last-updated: 2026-05-27
scope: "Building, deploying, and debugging an encrypted static site on GitHub Pages"
period: "2026-05-26 — 2026-05-27"
---

# Retro: GitHub Pages Static Site with Encryption Gate

## Summary

Built an Eleventy (11ty) static site with client-side AES-256-GCM encryption gate, deployed to GitHub Pages via a `public` branch bifurcation model. The site presents No Flock for SoPo's FOAA-obtained Flock Safety audit data through 6 fact pages, 5 methodology pages, a reproducibility page, and an index. All HTML is encrypted at rest — users enter a passphrase to decrypt in-browser via Web Crypto API (PBKDF2 + AES-256-GCM).

## Artifacts

| Artifact | Title | Outcome |
|----------|-------|---------|
| 13 Nunjucks templates | Fact, methodology, reproducibility pages | Complete |
| `site/.eleventy.js` | CSV→JSON build pipeline | Complete |
| `site/gate.js` | Client-side decryption gate | Complete (extracted from inline) |
| `site/gate.css` | Gate styling | Complete (extracted from inline) |
| `site/encrypt-site.js` | AES-256-GCM encryption script | Complete (reads gate.js/gate.css) |
| `site/test.sh` | 46 automated tests | Complete |
| `.agents/scripts/publish-to-github.sh` | Build + encrypt + deploy pipeline | Complete |
| `.public-allowlist` | Public branch file filter | Updated (docs removed) |

## Reflection

### What went well
- 11ty's data pipeline (CSV→JSON at build time) cleanly separated data from presentation
- Public branch bifurcation model keeps internal docs (AGENTS.md, .agents/, plans) off GitHub
- `site/test.sh` caught issues like double-escaping, p-wrapped tr, and variable resolution

### What was surprising
- GitHub Pages on a private repo requires a paid plan; had to make the repo public
- pathPrefix was needed because the site lives at `/data-for-press-release-2026-05-08/` not `/` — all internal links 404'd initially
- The `return;` bug in gate.js was invisible to linting because the code lived as a template literal string inside encrypt-site.js — ESLint parses it as a string, not JS
- sessionStorage cached the old passphrase after changing it, making the new one unusable until the stale key was cleared

### What would change
- **Extract gate.js and gate.css to standalone files before writing them** — the template-string approach hid syntax errors from tooling. Extraction was done in the fix, but it should have been the architecture from the start
- **Test the full deploy→decrypt flow locally** before pushing — we tested build and encryption separately but not the browser decrypt round-trip on GitHub Pages until the passcode failed in production
- **Never cache credentials before verification** — the original gate.js saved the passphrase to sessionStorage before confirming decryption succeeded, which left stale keys blocking re-entry

### Patterns observed
- Encryption gate code is security-sensitive and needs the same rigor as auth code: never persist state until success, always clear on failure, always register UI handlers regardless of auto-try path
- Template-embedded JS is a linting blind spot; standalone files are the right architecture

## Learnings captured

| Item | Type | Summary |
|------|------|---------|
| gate.js extraction | memory | Security-critical JS must be standalone files, not template strings, so linters can catch syntax errors |
| session-cache-before-verify | memory | Never persist credentials before verifying they work; always clear on failure |
| pathPrefix deployment | memory | GitHub Pages subpath sites need eleventy pathPrefix and `{{ "/path" \| url }}` filters on all internal links |
| docs-in-public-branch | memory | Internal docs (AGENTS.md, plans, troves) should not go to the public branch — only data, outputs, and the built site |