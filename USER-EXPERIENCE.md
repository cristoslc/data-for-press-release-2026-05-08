# User Experience

See `docs/user-experience/` for detail.

## Audience

This repo is for:
1. **Journalists** verifying press-release claims
2. **Legal reviewers** auditing evidence chains
3. **Researchers** replicating the analysis

## Quality attributes

- **Push-button reproducibility**: `./run.sh` regenerates every output from raw data
- **Auditability**: Every output traces via SHA-256 to specific raw inputs
- **Self-contained**: `git clone && ./run.sh` — no external services, no API keys
- **Clarity over cleverness**: Simple Python scripts, flat files, no framework
