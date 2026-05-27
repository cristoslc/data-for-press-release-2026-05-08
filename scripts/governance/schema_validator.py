import csv
from pathlib import Path
from typing import Dict, Optional

FLOCK_AUDIT_SCHEMAS = {
    "flock-org-audit": {
        "required": [
            "Date and Time",
            "Case Number",
            "User",
            "Reason for Search",
            "Search",
            "Organization",
        ],
        "optional": ["Plate State", "Plate Type", "Hit"],
    },
    "flock-network-audit": {
        "required": [
            "Date and Time",
            "Searching Organization",
            "Case Number",
            "Reason for Search",
            "Search",
        ],
        "optional": ["Organization"],
    },
}


def validate_csv(path: Path, schema_name: Optional[str] = None) -> Dict:
    result = {"path": str(path), "valid": False, "violations": [], "schema_match": None}
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration:
                result["violations"].append("empty file")
                return result
            header_set = {h.strip() for h in header}
    except UnicodeDecodeError:
        try:
            with open(path, newline="", encoding="latin-1") as f:
                reader = csv.reader(f)
                try:
                    header = next(reader)
                except StopIteration:
                    result["violations"].append("empty file")
                    return result
                header_set = {h.strip() for h in header}
        except Exception as e:
            result["violations"].append(f"read error: {e}")
            return result
    except Exception as e:
        result["violations"].append(f"read error: {e}")
        return result

    best_match = None
    best_score = -1
    for sname, schema in FLOCK_AUDIT_SCHEMAS.items():
        required_set = set(schema["required"])
        matches = len(header_set & required_set)
        if matches > best_score:
            best_score = matches
            best_match = sname

    if best_match and best_score >= 2:
        schema = FLOCK_AUDIT_SCHEMAS[best_match]
        required_set = set(schema["required"])
        missing = required_set - header_set
        extra = header_set - required_set - set(schema["optional"])
        if not missing:
            result["valid"] = True
        if missing:
            result["violations"].append(
                f"missing required columns: {', '.join(sorted(missing))}"
            )
        if extra:
            result["violations"].append(
                f"unexpected columns: {', '.join(sorted(extra))}"
            )
        result["schema_match"] = best_match

    return result
