"""Low-hanging Sybil and routing-table pollution controls.

This is intentionally modest. An anonymous overlay cannot get strong Sybil
resistance just from an application DHT. The goal is to make arbitrary node-id
selection and bulk identity churn less convenient, while keeping entry easy.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .identity import NodeIdentity, validate_identity


class AdmissionMode(str, Enum):
    OPEN = "open"
    CONTRIBUTOR = "contributor"
    STORAGE = "storage"
    SEED = "seed"


MODE_MIN_WORK_BITS = {
    AdmissionMode.OPEN: 0,
    AdmissionMode.CONTRIBUTOR: 8,
    AdmissionMode.STORAGE: 10,
    AdmissionMode.SEED: 12,
}


@dataclass(frozen=True)
class AdmissionDecision:
    accepted: bool
    mode: AdmissionMode
    work_bits: int
    reason: str


def evaluate_identity(identity: NodeIdentity, *, mode: AdmissionMode = AdmissionMode.OPEN) -> AdmissionDecision:
    required = MODE_MIN_WORK_BITS[mode]
    try:
        validate_identity(identity, min_work_bits=required)
    except ValueError as exc:
        return AdmissionDecision(False, mode, identity.admission_work_bits, str(exc))
    return AdmissionDecision(True, mode, identity.admission_work_bits, "identity accepted for local policy")


def local_reputation_score(*, useful_responses: int, failures: int, uptime_minutes: int) -> int:
    """Small deterministic local score; never a global social-credit system."""
    return max(0, useful_responses * 3 + min(uptime_minutes // 30, 20) - failures * 5)
