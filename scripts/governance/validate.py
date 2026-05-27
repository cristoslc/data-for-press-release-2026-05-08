import subprocess
import sys
from pathlib import Path

from scripts.governance.clearance import classify_all
from scripts.governance.pii_detector import scan_file
from scripts.governance.schema_validator import validate_csv


def git_tracked_files(root: str, pattern: str = "*.csv") -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--", f"{root}/{pattern}"],
        capture_output=True,
        text=True,
    )
    return [Path(p.strip()) for p in result.stdout.splitlines() if p.strip()]


def validate_all(data_roots=None, fail_on_violation=False, repo_root=None) -> dict:
    if data_roots is None:
        data_roots = ["data", "outputs"]
    if repo_root is None:
        repo_root = Path.cwd()
    else:
        repo_root = Path(repo_root)

    all_violations = []
    results = {"violations": all_violations, "passed": True}

    sidecar_violations, _ = classify_all(data_roots)
    if sidecar_violations:
        all_violations.extend(sidecar_violations)
        results["passed"] = False

    for root in data_roots:
        for p in git_tracked_files(root, "*.csv"):
            result = scan_file(p)
            if not result["passed"]:
                for f in result["findings"]:
                    all_violations.append(f"PII in {p}: {f}")
                results["passed"] = False

            schema = validate_csv(p)
            if not schema["valid"] and schema["schema_match"]:
                for v in schema["violations"]:
                    all_violations.append(f"schema {p}: {v}")

    if results["passed"]:
        print("  all validations passed")
    else:
        for v in all_violations:
            print(f"  VIOLATION: {v}")
        if fail_on_violation:
            sys.exit(1)
    return results
