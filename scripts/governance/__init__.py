from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Tier(int, Enum):
    ONE = 1
    TWO = 2

    def __str__(self) -> str:
        return str(self.value)


@dataclass
class ColumnClassification:
    path: str
    tier: Tier
    reason: str = ""
    stripped_covenants: List[str] = field(default_factory=list)


@dataclass
class ArtifactClassification:
    artifact_id: str
    baseline_tier: Tier
    encrypted: bool
    encryption_method: str
    lfs_authenticated: bool
    columns: Dict[str, ColumnClassification] = field(default_factory=dict)

    def column_tier(self, col_name: str) -> Tier:
        if col_name in self.columns:
            return self.columns[col_name].tier
        return self.baseline_tier

    @property
    def max_tier(self) -> Tier:
        max_t = self.baseline_tier
        for cc in self.columns.values():
            if cc.tier > max_t:
                max_t = cc.tier
        return max_t


def govt_record(
    provenance_class: str,
    restrictions: Dict,
    pii_scan_result: Optional[Dict] = None,
) -> Tier:
    if provenance_class in ("government-record", "public-domain", "open-license"):
        base = Tier.ONE
    else:
        base = Tier.TWO
    if pii_scan_result and not pii_scan_result.get("passed", True):
        return Tier.TWO
    return base


def shaky(
    concern: str = "",
    review_after: str = "",
    pii_scan_result: Optional[Dict] = None,
) -> Tier:
    return Tier.TWO


def derived_from(
    parent_tiers: List[Tier],
    covenant_stripped_count: int = 0,
    total_covenants: int = 0,
    pii_scan_result: Optional[Dict] = None,
) -> Tier:
    if pii_scan_result and not pii_scan_result.get("passed", True):
        return Tier.TWO
    if all(t == Tier.ONE for t in parent_tiers):
        return Tier.ONE
    if covenant_stripped_count >= total_covenants and total_covenants > 0:
        return Tier.ONE
    return Tier.TWO


def validate_classification(
    product_name: str, artifacts: List[ArtifactClassification]
) -> List[str]:
    violations = []
    for a in artifacts:
        if a.encrypted and a.encryption_method not in ("sops", "age"):
            violations.append(
                f"{product_name}/{a.artifact_id}: encrypted=True but invalid method '{a.encryption_method}'"
            )
        if not a.encrypted and a.encryption_method != "none":
            violations.append(
                f"{product_name}/{a.artifact_id}: encrypted=False but method '{a.encryption_method}'"
            )
        if a.baseline_tier not in (Tier.ONE, Tier.TWO):
            violations.append(
                f"{product_name}/{a.artifact_id}: invalid baseline tier {a.baseline_tier}"
            )
        for col_name, cc in a.columns.items():
            if cc.tier not in (Tier.ONE, Tier.TWO):
                violations.append(
                    f"{product_name}/{a.artifact_id}/{col_name}: invalid column tier {cc.tier}"
                )
            if cc.tier > a.baseline_tier:
                violations.append(
                    f"{product_name}/{a.artifact_id}/{col_name}: column tier {cc.tier} exceeds baseline {a.baseline_tier}"
                )
    return violations
