# Project-Specific Agent Guidance

## Includes

This file is the hub. Detail lives in `.agents/agents-md-detail/`. Start with `project-navigation.md`.

## Purpose reference

This repository's purpose is defined in `PURPOSE.md` (one paragraph).

## Branch bifurcation — publishing to GitHub

This repo has **two faces** controlled by branch:

| Branch | Remote | Contains |
|--------|--------|----------|
| `main` | `forgejo` | Everything — data, scripts, agent tools, design docs |
| `public` | `github` (as `main`) | Whitelisted only — data, analysis, outputs, hub files |

**Do NOT push directly to GitHub.** Use the publishing workflow:

1. Edit `.public-allowlist` to adjust what goes public (if needed)
2. Run `.agents/scripts/publish-to-github.sh` — rebuilds `public` branch
3. `git push github public:main --force`

The `public` branch is rebuilt fresh each time from `.public-allowlist` patterns. Files not matching any allowlist pattern **do not leave Forgejo**. Never commit agent prompts, design specs, or internal architecture docs to the public branch.

## Compliance with No Flock for SoPo AGENTS.md

This project inherits the global No Flock for SoPo agent conventions (disclaimers on outputs, intermediate data materialization, SHA-256 provenance tracking, embargoed data workflows). See the parent project's `AGENTS.md` at `../audit-log-analysis-202605/AGENTS.md` for full detail.
