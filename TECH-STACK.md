# Tech Stack

See `docs/tech-stack/` for detail.

| Layer | Choice |
|-------|--------|
| Language | Python 3.12+ |
| Package management | `uv` |
| Data transformation | Python scripts (pandas for tabular, pure Python for text) |
| Provenance tracking | Content-addressed via SHA-256, manual manifest |
| Testing | `pytest` |
| Linting | `ruff` |
| Version control | git, Forgejo remote |
