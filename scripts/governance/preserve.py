import hashlib
import os
import subprocess
from pathlib import Path

from scripts.governance.keyring import with_key_file


def age_encrypt(src: Path, dst: Path, pubkey_path: Path) -> str:
    pubkey = pubkey_path.read_text().strip().split("\n")[0].strip()
    result = subprocess.run(
        ["age", "-r", pubkey, "-o", str(dst), str(src)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"age encryption failed: {result.stderr}")
    return sha256(dst)


def sops_encrypt(src: Path, dst: Path) -> str:
    with_key_file(lambda key_path: _sops_encrypt(src, dst, key_path))
    return sha256(dst)


def _sops_encrypt(src: Path, dst: Path, key_file: Path):
    env = {**os.environ, "SOPS_AGE_KEY_FILE": str(key_file)}
    result = subprocess.run(
        ["sops", "--encrypt", str(src)],
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"sops encryption failed: {result.stderr}")
    dst.write_text(result.stdout)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def preserve_artifact(
    artifact_path: Path,
    tier: str,
    output_dir: Path,
    pubkey_path: Path,
    key_path: Path,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    if tier == "1":
        dst = output_dir / artifact_path.name
        if artifact_path != dst:
            import shutil

            shutil.copy2(artifact_path, dst)
        return {
            "path": str(dst),
            "hash": sha256(dst),
            "encrypted": False,
            "method": "none",
        }

    if tier == "2":
        is_tabular = artifact_path.suffix.lower() in (".csv", ".tsv", ".jsonl")
        if is_tabular:
            import csv
            import json

            rows = []
            if artifact_path.suffix.lower() == ".csv":
                with open(artifact_path) as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
            elif artifact_path.suffix.lower() == ".jsonl":
                with open(artifact_path) as f:
                    rows = [json.loads(line) for line in f if line.strip()]
            tmp_json = output_dir / f"{artifact_path.stem}.tmp.json"
            with open(tmp_json, "w") as f:
                json.dump(rows, f, indent=2)
            dst = output_dir / f"{artifact_path.name}.sops"
            h = sops_encrypt(tmp_json, dst)
            tmp_json.unlink()
            return {"path": str(dst), "hash": h, "encrypted": True, "method": "sops"}
        else:
            dst = output_dir / f"{artifact_path.name}.age"
            h = age_encrypt(artifact_path, dst, pubkey_path)
            return {"path": str(dst), "hash": h, "encrypted": True, "method": "age"}

    return {
        "path": str(artifact_path),
        "hash": sha256(artifact_path),
        "encrypted": False,
        "method": "none",
    }
