import subprocess
import tempfile
from pathlib import Path

OP_ITEM = "op://Homelab/audit-log-analysis-202605 age key/notesPlain"


def get_age_key() -> str:
    result = subprocess.run(
        ["op", "read", OP_ITEM],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to read age key from 1Password: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def with_key_file(fn):
    key = get_age_key()
    tmp = Path(tempfile.mkstemp(suffix="-age-key")[1])
    tmp.write_text(key + "\n")
    try:
        return fn(tmp)
    finally:
        tmp.unlink()
