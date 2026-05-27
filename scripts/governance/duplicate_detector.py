import hashlib
from pathlib import Path
from typing import Dict, List, Set


def sha256(content: bytes | str) -> str:
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def index_committed_data(repo_root: Path) -> Set[str]:
    hashes: Set[str] = set()
    for root_dir in [repo_root / "data", repo_root / "outputs"]:
        if not root_dir.exists():
            continue
        for p in root_dir.rglob("*"):
            if p.is_file() and p.name not in (
                ".gitignore",
                ".governance.py",
                "data-governance.yaml",
                "README.md",
            ):
                if p.suffix.lower() in (".csv", ".tsv", ".json", ".jsonl", ".py"):
                    hashes.add(sha256(p.read_bytes()))
    return hashes


def detect_duplicates(
    staged_paths: List[Path], committed_hashes: Set[str]
) -> List[Dict]:
    violations = []
    for p in staged_paths:
        if not p.is_file():
            continue
        if p.suffix.lower() in (".csv", ".tsv", ".json", ".jsonl", ".py"):
            h = sha256(p.read_bytes())
            if h in committed_hashes:
                violations.append(
                    {
                        "path": str(p),
                        "hash": h,
                        "violation": "byte-identical duplicate of committed data",
                    }
                )
    return violations
