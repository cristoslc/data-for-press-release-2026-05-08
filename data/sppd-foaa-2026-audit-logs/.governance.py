from scripts.governance import (
    govt_record,
)


def classify(product, artifacts, pii_scan_results=None, lineage_graph=None):
    results = {}
    for a in artifacts:
        tier = govt_record(
            product.get("provenance-class", "government-record"),
            product.get("restrictions", {}),
            pii_scan_results.get(a["id"]) if pii_scan_results else None,
        )
        entry = {"baseline_tier": tier, "columns": {}}
        results[a["id"]] = entry
    return results
