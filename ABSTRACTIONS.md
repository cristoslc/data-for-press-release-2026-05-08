# Abstractions

See `docs/abstractions/` for detail.

## Bounded context: data-publishing pipeline

| Abstraction | Description |
|-------------|-------------|
| `RawSource` | A FOAA response file (PDF, CSV) |
| `NormalizedTable` | A cleaned, schema-checked intermediate (parquet or CSV with schema manifest) |
| `ProvenanceRecord` | SHA-256 chain: which RawSource + script version produced which NormalizedTable |
| `AnalysisOutput` | A final artifact (markdown report, JSON factoid, CSV summary) with full provenance back to raw |
