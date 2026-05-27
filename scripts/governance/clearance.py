import importlib.util
import sys
from pathlib import Path
from typing import List, Tuple

from scripts.governance import ArtifactClassification, Tier, validate_classification


def load_sidecar(path: Path):
    spec = importlib.util.spec_from_file_location(
        f"sidecar_{path.parent.name.replace('-', '_').replace(' ', '_')}",
        str(path),
    )
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def run_sidecar(product_path: Path, sidecar_path: Path, pii_scan=None, lineage=None):
    mod = load_sidecar(sidecar_path)
    if mod is None or not hasattr(mod, "classify"):
        return None
    gov_yaml = product_path / "data-governance.yaml"
    product = {}
    artifacts = []
    if gov_yaml.exists():
        import yaml

        with open(gov_yaml) as f:
            product = yaml.safe_load(f)
        artifacts = product.get("artifacts", [])
    else:
        data_files = [
            str(f.relative_to(product_path))
            for f in product_path.iterdir()
            if f.is_file()
            and f.suffix.lower()
            in (".csv", ".tsv", ".xlsx", ".pdf", ".json", ".jsonl", ".md")
        ]
        artifacts = [{"id": name, "path": name} for name in data_files]

    try:
        result = mod.classify(
            product, artifacts, pii_scan_results=pii_scan, lineage_graph=lineage
        )
    except Exception as e:
        return {"error": str(e)}

    classifications = []
    for aid, entry in result.items():
        baseline = entry.get("baseline_tier", Tier.TWO)
        method = "sops" if baseline == Tier.TWO else "none"
        ac = ArtifactClassification(
            artifact_id=aid,
            baseline_tier=baseline,
            encrypted=(baseline == Tier.TWO),
            encryption_method=method,
            lfs_authenticated=(baseline == Tier.TWO),
            columns={},
        )
        classifications.append(ac)

    return classifications


def walk_subtrees(root_dirs: List[Path]) -> List[Tuple[Path, Path]]:
    subtrees = []

    for root in root_dirs:
        if not root.exists():
            continue
        for entry in sorted(root.iterdir()):
            if not entry.is_dir():
                continue
            if entry.name == "embargoed":
                for ds in sorted(entry.iterdir()):
                    if ds.is_dir() and ds.name not in (
                        "README.md",
                        "AGENTS.md",
                        "MANIFEST.yaml",
                    ):
                        if (ds / ".governance.py").exists():
                            subtrees.append((ds, ds / ".governance.py"))
                continue

            product_dirs = [d for d in entry.glob("*") if d.is_dir()]
            if product_dirs:
                for pd in product_dirs:
                    if (pd / ".governance.py").exists():
                        subtrees.append((pd, pd / ".governance.py"))
            else:
                if (entry / ".governance.py").exists():
                    subtrees.append((entry, entry / ".governance.py"))
    return subtrees


def classify_all(
    root_dirs: List[str],
    pii_scan=None,
    lineage=None,
) -> Tuple[List[str], List[ArtifactClassification]]:
    violations = []
    all_classifications = []
    roots = [Path(d) for d in root_dirs]
    subtrees = walk_subtrees(roots)

    seen = {}
    for product_path, sidecar_path in subtrees:
        if str(product_path) in seen:
            seen[str(product_path)] += 1
            continue
        seen[str(product_path)] = 1

        if not sidecar_path.exists():
            violations.append(f"{product_path}: expected .governance.py but not found")
            continue

        result = run_sidecar(
            product_path, sidecar_path, pii_scan=pii_scan, lineage=lineage
        )
        if result is None:
            violations.append(
                f"{product_path}: .governance.py has no classify() function"
            )
        elif isinstance(result, list):
            prod_violations = validate_classification(str(product_path), result)
            violations.extend(prod_violations)
            all_classifications.extend(result)
        elif isinstance(result, dict) and "error" in result:
            violations.append(f"{product_path}: classify() error: {result['error']}")

    return violations, all_classifications


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--roots", nargs="+", default=["data", "outputs"])
    parser.add_argument("--fail-on-missing", action="store_true")
    parser.add_argument(
        "--execute", action="store_true", help="Actually run classify() on sidecars"
    )
    args = parser.parse_args()

    pii, lineage = None, None
    violations, classifications = classify_all(
        args.roots, pii_scan=pii, lineage=lineage
    )
    if violations:
        for v in violations:
            print(f"  VIOLATION: {v}")
        if args.fail_on_missing:
            sys.exit(1)
    else:
        print(f"  all subtrees classified ({len(classifications)} artifacts)")

    if args.execute and classifications:
        for ac in classifications:
            print(
                f"  {ac.artifact_id}: tier={ac.baseline_tier}, encrypted={ac.encrypted}"
            )


if __name__ == "__main__":
    main()
