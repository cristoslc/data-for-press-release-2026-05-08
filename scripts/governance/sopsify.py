import csv
import json
import os
import subprocess
import tempfile
from pathlib import Path

from scripts.governance.keyring import with_key_file


def csv_to_json_tree(csv_path: Path) -> Path:
    tmp = Path(tempfile.mkstemp(suffix=".json")[1])
    rows = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    with open(tmp, "w") as f:
        json.dump(rows, f, indent=2)
    return tmp


def jsonl_to_json_tree(jsonl_path: Path) -> Path:
    tmp = Path(tempfile.mkstemp(suffix=".json")[1])
    rows = []
    with open(jsonl_path) as f:
        rows = [json.loads(line) for line in f if line.strip()]
    with open(tmp, "w") as f:
        json.dump(rows, f, indent=2)
    return tmp


def sops_encrypt_json(json_path: Path, dst_path: Path, key_file: Path):
    env = {**os.environ, "SOPS_AGE_KEY_FILE": str(key_file)}
    result = subprocess.run(
        ["sops", "--encrypt", str(json_path)],
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"sops encryption failed: {result.stderr}")
    dst_path.write_text(result.stdout)


def sopsify_tabular(src_path: Path, dst_path: Path):
    suffix = src_path.suffix.lower()
    if suffix == ".csv":
        json_path = csv_to_json_tree(src_path)
    elif suffix == ".jsonl":
        json_path = jsonl_to_json_tree(src_path)
    else:
        raise ValueError(f"unexpected format for SOPS conversion: {suffix}")

    with_key_file(lambda key_path: sops_encrypt_json(json_path, dst_path, key_path))
    if json_path != dst_path:
        json_path.unlink()
