# Architecture

See `docs/architecture/` for detail.

## Overview

This is a data-publishing repository — not a long-lived application. The architecture is a directed acyclic pipeline:

```
raw data (FOAA PDFs/CSVs) → normalized intermediates → analysis transforms → verified outputs
```

## C4 summary

| Level | Description |
|-------|-------------|
| System | Data-publishing repo for press-release evidence |
| Container | Python/uv scripts reading flat files, writing flat files |
| Component | Per-analysis scripts in `analysis/`, shared utils in `scripts/` |
| Code | Idempotent transform functions, provenance-tracked writes |

## Key diagrams

- **Pipeline DAG** — see `docs/architecture/pipeline-flow.md`
- **Data lineage** — see `docs/architecture/data-lineage.md`

## Cross-context communication

None. This is a single-context, batch-processing pipeline with no services, no APIs, no databases.
