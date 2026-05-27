from scripts.governance import (
    Tier,
)


def classify(product, artifacts, pii_scan_results=None, lineage_graph=None):
    results = {}
    for a in artifacts:
        tier = Tier.ONE
        if pii_scan_results and a["id"] in pii_scan_results:
            if not pii_scan_results[a["id"]].get("passed", True):
                tier = Tier.TWO
        entry = {"baseline_tier": tier, "columns": {}}
        results[a["id"]] = entry
    return results
