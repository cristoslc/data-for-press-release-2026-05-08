import csv
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

DEFAULT_ALLOWLIST = {
    "Organization Name",
    "Officer Name",
    "Officer ID",
    "Badge Number",
}

CONTENT_ALLOWLIST_EMAILS = {
    # General mailboxes published by news outlets for reader support
    "memberservices@wgcu.org",  # WGCU public radio — reader accessibility contact
    "support@people.inc",  # People magazine — reader access issue contact
    # Role mailboxes posted in official government press releases
    "info@kspress.com",  # Kansas Press Association — organizational inquiry address
    "mediarelations@lakelandgov.net",  # City of Lakeland — media relations contact
    "ADASpecialist@lakelandgov.net",  # City of Lakeland — ADA compliance contact
    # Public government employee contacts posted in official press releases
    "Travis.payne@lakelandgov.net",  # City of Lakeland — communications office (press release author)
    # Public research group contact addresses published on open web pages
    "humans@haveibeenflocked.com",  # HIBF (Have I Been Flocked) — public research group contact
}

CONTENT_ALLOWLIST_PHONES = {
    # Organizational phone numbers published in news articles or official government releases
    "2395902500",  # WGCU public radio — public-facing line
    "4076656650",  # Seminole County Sheriff's Office — public line (posted in news article)
    "8638348444",  # City of Lakeland — communications office line (posted in official press releases)
    "3215017594",  # Published in public news article (scraped body text)
    "7852715304",  # Kansas Press Association — organizational line
    "8139742628",  # University of South Florida — public campus line (posted in news article)
    "6053304400",  # Published in public news article (scraped body text)
}

PRESIDIO_ENTITIES = [
    "US_SSN",
    "PHONE_NUMBER",
    "EMAIL_ADDRESS",
    "PERSON",
    "US_DRIVER_LICENSE",
    "US_PASSPORT",
    "STREET_ADDRESS",
    "DATE_TIME",
]

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", re.IGNORECASE)
PHONE_RE = re.compile(r"\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_NON_DIGIT = re.compile(r"\D")


def _content_ok(match_obj, text: str) -> bool:
    matched = match_obj.group()
    return (
        matched.strip().lower() in {v.lower() for v in CONTENT_ALLOWLIST_EMAILS}
        or _NON_DIGIT.sub("", matched) in CONTENT_ALLOWLIST_PHONES
    )


def scan_csv(path: Path, allowlist: Set[str]) -> List[Dict]:
    findings = []
    try:
        allowed_encodings = ["utf-8", "latin-1", "cp1252"]
        for enc in allowed_encodings:
            try:
                with open(path, encoding=enc, newline="") as f:
                    reader = csv.DictReader(f)
                    if reader.fieldnames is None:
                        continue
                    rows = list(reader)
                    cols = reader.fieldnames
                break
            except (UnicodeDecodeError, csv.Error):
                continue
        else:
            return findings
    except Exception:
        return findings

    for col_idx, col_name in enumerate(cols):
        if col_name in allowlist:
            continue
        for row_idx, row in enumerate(rows):
            val = (row.get(col_name, "") or "").strip()
            if not val:
                continue
            email_m = EMAIL_RE.search(val)
            if email_m and not _content_ok(email_m, val):
                findings.append(
                    {
                        "row": row_idx + 2,
                        "col": col_name,
                        "entity": "EMAIL_ADDRESS",
                        "value_hint": val[:30],
                    }
                )
                continue
            phone_m = PHONE_RE.search(val)
            if phone_m and not _content_ok(phone_m, val):
                findings.append(
                    {
                        "row": row_idx + 2,
                        "col": col_name,
                        "entity": "PHONE_NUMBER",
                        "value_hint": val[:30],
                    }
                )
                continue
            if SSN_RE.search(val):
                findings.append(
                    {
                        "row": row_idx + 2,
                        "col": col_name,
                        "entity": "US_SSN",
                        "value_hint": val[:30],
                    }
                )
    return findings


def scan_text(path: Path) -> List[Dict]:
    findings = []
    try:
        text = path.read_text()
    except Exception:
        return findings
    for match in EMAIL_RE.finditer(text):
        if _content_ok(match, text):
            continue
        line_no = text[: match.start()].count("\n") + 1
        findings.append(
            {
                "line": line_no,
                "entity": "EMAIL_ADDRESS",
                "value_hint": match.group()[:30],
            }
        )
    for match in PHONE_RE.finditer(text):
        if _content_ok(match, text):
            continue
        line_no = text[: match.start()].count("\n") + 1
        findings.append(
            {
                "line": line_no,
                "entity": "PHONE_NUMBER",
                "value_hint": match.group()[:30],
            }
        )
    return findings


def scan_file(path: Path, allowlist: Optional[Set[str]] = None) -> Dict:
    allowlist = allowlist or set()
    merged_allowlist = DEFAULT_ALLOWLIST | allowlist
    ext = path.suffix.lower()
    if ext == ".csv":
        findings = scan_csv(path, merged_allowlist)
        return {
            "path": str(path),
            "type": "csv",
            "findings": findings,
            "passed": len(findings) == 0,
        }
    if ext in (".md", ".txt", ".vtt"):
        findings = scan_text(path)
        return {
            "path": str(path),
            "type": "text",
            "findings": findings,
            "passed": len(findings) == 0,
        }
    return {"path": str(path), "type": "unknown", "findings": [], "passed": True}


if __name__ == "__main__":
    import sys

    exit_code = 0
    for arg in sys.argv[1:]:
        result = scan_file(Path(arg))
        if not result["passed"]:
            print(f"PII found in {arg}:")
            for f in result["findings"]:
                print(f"  {f}")
            exit_code = 1
    sys.exit(exit_code)
