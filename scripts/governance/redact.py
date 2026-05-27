import csv
from pathlib import Path
from typing import Dict, List, Optional


def redact_csv(
    src: Path, dst: Path, redact_columns: Optional[List[str]] = None
) -> Dict:
    redact_columns = redact_columns or []
    redactions = []
    with open(src, newline="", encoding="utf-8") as f_in:
        reader = csv.reader(f_in)
        try:
            header = next(reader)
        except StopIteration:
            return {"redactions": []}
        rows = [row for row in reader]

    col_indices = {i: col for i, col in enumerate(header) if col in redact_columns}

    for row_idx, row in enumerate(rows):
        for col_idx, col_name in col_indices.items():
            if col_idx < len(row):
                _ = row[col_idx]
                row[col_idx] = "***REDACTED***"
                redactions.append(
                    {
                        "row": row_idx + 2,
                        "col": col_name,
                        "action": "column-redact",
                        "reason": "column in redact list",
                    }
                )

    with open(dst, "w", newline="", encoding="utf-8") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(header)
        writer.writerows(rows)

    return {"redactions": redactions, "output_path": str(dst)}
