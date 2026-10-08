"""Deterministic adapter/profile-edge fuzz summaries.

The cube still has no live transport, so rev0053 makes drift testing explicit:
fuzz observations record whether deliberate scope/request/payload/component
mutations reached quarantine-like decisions.  This is not a fuzzer engine; it is
an audit-friendly result algebra for generated and hand-written mismatch cases.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256

ADAPTER_FUZZ_DOMAIN = DOMAIN + b":adapter-fuzz-v1:"


class AdapterFuzzDecisionKind(str, Enum):
    ACCEPT_FUZZ_COVERAGE = "accept_fuzz_coverage"
    HOLD_MISSING_MUTATION = "hold_missing_mutation"
    HOLD_LOW_SURFACE_DIVERSITY = "hold_low_surface_diversity"
    QUARANTINE_UNEXPECTED_ACCEPT = "quarantine_unexpected_accept"
    QUARANTINE_EXPECTED_WATCH_ONLY = "quarantine_expected_watch_only"
    EMPTY_NO_OBSERVATIONS = "empty_no_observations"


@dataclass(frozen=True)
class AdapterFuzzObservation:
    surface: str
    mutation: str
    expected_prefix: str
    observed_decision: str
    report_digest: bytes
    family_id: str
    path_family: str

    def __post_init__(self) -> None:
        if not self.surface or not self.mutation or not self.expected_prefix or not self.observed_decision or not self.family_id or not self.path_family:
            raise ValueError("fuzz observation needs surface/mutation/decision/family/path")
        if len(self.report_digest) != 32:
            raise ValueError("report digest must be 32 bytes")

    @property
    def matched(self) -> bool:
        return self.observed_decision.startswith(self.expected_prefix)

    @property
    def watch_only(self) -> bool:
        return self.observed_decision.startswith("hold_") or self.observed_decision.endswith("with_watch")

    def bvalue(self) -> dict[bytes, object]:
        return {b"surface": self.surface, b"mutation": self.mutation, b"expected": self.expected_prefix, b"observed": self.observed_decision, b"digest": self.report_digest, b"family": self.family_id, b"path_family": self.path_family}


@dataclass(frozen=True)
class AdapterFuzzReport:
    decision_kind: AdapterFuzzDecisionKind
    accept: bool
    watch: bool
    reason: str
    required_mutations: tuple[str, ...]
    observed_mutations: tuple[str, ...]
    surface_count: int
    family_count: int
    path_family_count: int
    failing_observations: tuple[AdapterFuzzObservation, ...]
    observation_digests: tuple[bytes, ...]
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def summarize_adapter_fuzz(
    observations: Iterable[AdapterFuzzObservation],
    *,
    required_mutations: Iterable[str],
    min_surface_count: int = 2,
    min_family_count: int = 1,
    min_path_family_count: int = 1,
    allow_watch_only: bool = False,
) -> AdapterFuzzReport:
    obs = tuple(observations)
    required = tuple(sorted(set(required_mutations)))
    if not obs:
        return _report(AdapterFuzzDecisionKind.EMPTY_NO_OBSERVATIONS, False, False, "adapter fuzz needs observations", required, obs, ())
    observed = tuple(sorted({item.mutation for item in obs}))
    missing = tuple(item for item in required if item not in observed)
    if missing:
        return _report(AdapterFuzzDecisionKind.HOLD_MISSING_MUTATION, False, True, "missing required fuzz mutations", required, obs, ())
    surfaces = {item.surface for item in obs}
    if len(surfaces) < min_surface_count:
        return _report(AdapterFuzzDecisionKind.HOLD_LOW_SURFACE_DIVERSITY, False, True, "fuzz needs more surface diversity", required, obs, ())
    families = {item.family_id for item in obs}
    paths = {item.path_family for item in obs}
    if len(families) < min_family_count or len(paths) < min_path_family_count:
        return _report(AdapterFuzzDecisionKind.HOLD_LOW_SURFACE_DIVERSITY, False, True, "fuzz needs family/path diversity", required, obs, ())
    failing = tuple(item for item in obs if not item.matched)
    if failing:
        return _report(AdapterFuzzDecisionKind.QUARANTINE_UNEXPECTED_ACCEPT, False, False, "a deliberate mutation did not hit expected decision prefix", required, obs, failing)
    watch_only = tuple(item for item in obs if item.watch_only)
    if watch_only and not allow_watch_only:
        return _report(AdapterFuzzDecisionKind.QUARANTINE_EXPECTED_WATCH_ONLY, False, False, "mutation only produced watch/hold, not quarantine", required, obs, watch_only)
    return _report(AdapterFuzzDecisionKind.ACCEPT_FUZZ_COVERAGE, True, False, "adapter fuzz coverage accepted", required, obs, ())


def _report(kind: AdapterFuzzDecisionKind, accept: bool, watch: bool, reason: str, required: tuple[str, ...], observations: tuple[AdapterFuzzObservation, ...], failing: tuple[AdapterFuzzObservation, ...]) -> AdapterFuzzReport:
    observed = tuple(sorted({item.mutation for item in observations}))
    surfaces = {item.surface for item in observations}
    families = {item.family_id for item in observations}
    paths = {item.path_family for item in observations}
    digests = tuple(item.report_digest for item in observations)
    digest = sha256(ADAPTER_FUZZ_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"required": list(required),
        b"observed": list(observed),
        b"surfaces": sorted(surfaces),
        b"families": len(families),
        b"paths": len(paths),
        b"digests": list(digests),
        b"failing": [item.bvalue() for item in failing],
    }))
    return AdapterFuzzReport(kind, accept, watch, reason, required, observed, len(surfaces), len(families), len(paths), failing, digests, digest)
