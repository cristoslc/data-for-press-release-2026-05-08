# Developer Workflows

See `docs/developer-workflows/` for detail.

| Workflow | Command |
|----------|---------|
| Reproduce all outputs | `./run.sh` |
| Run tests | `uv run pytest tests/` |
| Lint | `uv run ruff check .` |
| Type-check | `uv run pyright` |
| Add dependency | `uv add <package>` |
| Verify push-button reproducibility | `rm -rf outputs/ && ./run.sh && diff outputs/ expected/` |
| Publish to GitHub (public branch) | `.agents/scripts/publish-to-github.sh && git push github public:main --force` |
| Edit public whitelist | Edit `.public-allowlist`, then run publish-to-github.sh |
| Check what's on public branch | `git ls-tree -r public --name-only` |

## Branch bifurcation

| Branch | Remote | Purpose |
|--------|--------|---------|
| `main` | `forgejo` | Full repo — data, scripts, `.agents/` internal tools |
| `public` | `github` (as `main`) | Whitelisted only — rebuilt from `.public-allowlist` |

See `AGENTS.md#branch-bifurcation` for the full publishing protocol.
