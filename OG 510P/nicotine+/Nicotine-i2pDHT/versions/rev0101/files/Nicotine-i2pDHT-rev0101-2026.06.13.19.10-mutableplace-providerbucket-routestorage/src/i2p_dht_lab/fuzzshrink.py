"""Fuzz-shrink coverage compaction for adapter boundary tests.

rev0055 keeps deterministic adapter fuzz coverage from becoming either bloated
local memory or false confidence.  A shrink report says: these smaller cases
still preserve the required mutations, expected quarantine prefixes, family/path
variety, and generator/fuzz-ledger binding.  It is local test evidence, not a
production fuzzer or global proof.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable

from .bencode import bencode
from .ids import DOMAIN, sha256
from .moderationquarantine import ZERO_DIGEST

FUZZ_SHRINK_DOMAIN = DOMAIN + b":fuzz-shrink-v1:"


class FuzzShrinkDecisionKind(str, Enum):
    ACCEPT_SHRUNK_COVERAGE = "accept_shrunk_coverage"
    ACCEPT_WITH_WATCH = "accept_with_watch"
    EMPTY_NO_CANDIDATES = "empty_no_candidates"
    HOLD_FUZZ_REPORT = "hold_fuzz_report"
    HOLD_FUZZ_LEDGER = "hold_fuzz_ledger"
    HOLD_MISSING_MUTATIONS = "hold_missing_mutations"
    HOLD_LOW_SURFACE_DIVERSITY = "hold_low_surface_diversity"
    HOLD_LOW_FAMILY_DIVERSITY = "hold_low_family_diversity"
    HOLD_LOW_PATH_DIVERSITY = "hold_low_path_diversity"
    QUARANTINE_LOST_EXPECTED_DECISION = "quarantine_lost_expected_decision"
    QUARANTINE_EXPECTED_WATCH_ONLY = "quarantine_expected_watch_only"
    QUARANTINE_REPORT_DIGEST_DRIFT = "quarantine_report_digest_drift"
    QUARANTINE_GENERATOR_DRIFT = "quarantine_generator_drift"
    QUARANTINE_LEDGER_FAILURES = "quarantine_ledger_failures"


@dataclass(frozen=True)
class FuzzShrinkCandidate:
    surface: str
    mutation: str
    expected_prefix: str
    observed_decision: str
    original_report_digest: bytes
    shrunk_case_digest: bytes
    generator_digest: bytes
    payload_units_before: int
    payload_units_after: int
    family_id: str
    path_family: str

    def __post_init__(self) -> None:
        if not self.surface or not self.mutation or not self.expected_prefix or not self.observed_decision or not self.family_id or not self.path_family:
            raise ValueError("fuzz shrink candidate needs surface/mutation/decision/family/path")
        if self.payload_units_before < 0 or self.payload_units_after < 0:
            raise ValueError("payload units must be non-negative")
        if self.payload_units_after > self.payload_units_before:
            raise ValueError("shrunk payload cannot exceed original payload units")
        for name, value in (
            ("original_report_digest", self.original_report_digest),
            ("shrunk_case_digest", self.shrunk_case_digest),
            ("generator_digest", self.generator_digest),
        ):
            if len(value) != 32:
                raise ValueError(f"{name} must be 32 bytes")

    @property
    def preserves_expected(self) -> bool:
        return self.observed_decision.startswith(self.expected_prefix)

    @property
    def watch_only(self) -> bool:
        return self.observed_decision.startswith("hold_") or self.observed_decision.endswith("with_watch")

    @property
    def saved_units(self) -> int:
        return self.payload_units_before - self.payload_units_after

    def bvalue(self) -> dict[bytes, object]:
        return {
            b"surface": self.surface,
            b"mutation": self.mutation,
            b"expected": self.expected_prefix,
            b"observed": self.observed_decision,
            b"original": self.original_report_digest,
            b"shrunk": self.shrunk_case_digest,
            b"generator": self.generator_digest,
            b"before": self.payload_units_before,
            b"after": self.payload_units_after,
            b"family": self.family_id,
            b"path_family": self.path_family,
        }


@dataclass(frozen=True)
class FuzzShrinkReport:
    decision_kind: FuzzShrinkDecisionKind
    accept: bool
    watch: bool
    reason: str
    fuzz_report_digest: bytes
    fuzz_ledger_digest: bytes
    generator_digest: bytes
    required_mutations: tuple[str, ...]
    selected_mutations: tuple[str, ...]
    selected_case_digests: tuple[bytes, ...]
    candidate_count: int
    surface_count: int
    family_count: int
    path_family_count: int
    payload_units_before: int
    payload_units_after: int
    saved_units: int
    report_digest: bytes

    @property
    def quarantined(self) -> bool:
        return self.decision_kind.value.startswith("quarantine_")


def _digest(report: Any | None) -> bytes:
    if report is None:
        return ZERO_DIGEST
    for attr in ("report_digest", "transcript_digest", "canary_digest"):
        value = getattr(report, attr, None)
        if isinstance(value, bytes) and len(value) == 32:
            return value
    raise ValueError("report lacks 32-byte digest")


def assess_fuzz_shrink(
    candidates: Iterable[FuzzShrinkCandidate],
    *,
    fuzz_report: Any,
    fuzz_ledger_report: Any,
    generator_digest: bytes,
    min_surface_count: int = 2,
    min_family_count: int = 2,
    min_path_family_count: int = 2,
    allow_watch_only: bool = False,
    allow_fuzz_watch: bool = False,
) -> FuzzShrinkReport:
    cand_t = tuple(candidates)
    fuzz_digest = _digest(fuzz_report)
    ledger_digest = _digest(fuzz_ledger_report)
    required = tuple(sorted(set(getattr(fuzz_report, "required_mutations", ()))))
    common = dict(fuzz_report_digest=fuzz_digest, fuzz_ledger_digest=ledger_digest, generator_digest=generator_digest, required_mutations=required)
    if not cand_t:
        return _report(FuzzShrinkDecisionKind.EMPTY_NO_CANDIDATES, False, False, "fuzz shrink needs candidates", candidates=cand_t, selected=(), **common)
    if not bool(getattr(fuzz_report, "accept", False)) or bool(getattr(fuzz_report, "quarantined", False)):
        return _report(FuzzShrinkDecisionKind.HOLD_FUZZ_REPORT, False, True, "accepted fuzz report required before shrink", candidates=cand_t, selected=(), **common)
    if bool(getattr(fuzz_report, "watch", False)) and not allow_fuzz_watch:
        return _report(FuzzShrinkDecisionKind.HOLD_FUZZ_REPORT, False, True, "fuzz report watch pressure must be carried", candidates=cand_t, selected=(), **common)
    if not bool(getattr(fuzz_ledger_report, "accept", False)) or bool(getattr(fuzz_ledger_report, "quarantined", False)):
        return _report(FuzzShrinkDecisionKind.HOLD_FUZZ_LEDGER, False, True, "accepted fuzz ledger required before shrink", candidates=cand_t, selected=(), **common)
    if getattr(fuzz_ledger_report, "failing_count", 0):
        return _report(FuzzShrinkDecisionKind.QUARANTINE_LEDGER_FAILURES, False, False, "failing fuzz observations cannot be shrunk into coverage", candidates=cand_t, selected=(), **common)
    for candidate in cand_t:
        if candidate.original_report_digest not in tuple(getattr(fuzz_report, "observation_digests", ())) and candidate.original_report_digest != fuzz_digest:
            return _report(FuzzShrinkDecisionKind.QUARANTINE_REPORT_DIGEST_DRIFT, False, False, "candidate original digest is not in fuzz report", candidates=cand_t, selected=(), **common)
        if candidate.generator_digest != generator_digest:
            return _report(FuzzShrinkDecisionKind.QUARANTINE_GENERATOR_DRIFT, False, False, "candidate generator digest drift", candidates=cand_t, selected=(), **common)
        if not candidate.preserves_expected:
            return _report(FuzzShrinkDecisionKind.QUARANTINE_LOST_EXPECTED_DECISION, False, False, "shrunk case lost expected decision", candidates=cand_t, selected=(), **common)
        if candidate.watch_only and not allow_watch_only:
            return _report(FuzzShrinkDecisionKind.QUARANTINE_EXPECTED_WATCH_ONLY, False, False, "shrunk case only preserved a watch/hold outcome", candidates=cand_t, selected=(), **common)
    by_mutation: dict[str, FuzzShrinkCandidate] = {}
    for candidate in cand_t:
        if candidate.mutation in required:
            incumbent = by_mutation.get(candidate.mutation)
            if incumbent is None or candidate.payload_units_after < incumbent.payload_units_after:
                by_mutation[candidate.mutation] = candidate
    missing = tuple(item for item in required if item not in by_mutation)
    if missing:
        return _report(FuzzShrinkDecisionKind.HOLD_MISSING_MUTATIONS, False, True, "shrunk corpus is missing required mutation", candidates=cand_t, selected=tuple(by_mutation.values()), **common)
    selected = tuple(by_mutation[mutation] for mutation in required)
    surfaces = {item.surface for item in selected}
    families = {item.family_id for item in selected}
    paths = {item.path_family for item in selected}
    if len(surfaces) < min_surface_count:
        return _report(FuzzShrinkDecisionKind.HOLD_LOW_SURFACE_DIVERSITY, False, True, "shrunk corpus needs surface diversity", candidates=cand_t, selected=selected, **common)
    if len(families) < min_family_count:
        return _report(FuzzShrinkDecisionKind.HOLD_LOW_FAMILY_DIVERSITY, False, True, "shrunk corpus needs family diversity", candidates=cand_t, selected=selected, **common)
    if len(paths) < min_path_family_count:
        return _report(FuzzShrinkDecisionKind.HOLD_LOW_PATH_DIVERSITY, False, True, "shrunk corpus needs path diversity", candidates=cand_t, selected=selected, **common)
    if bool(getattr(fuzz_ledger_report, "watch", False)):
        return _report(FuzzShrinkDecisionKind.ACCEPT_WITH_WATCH, True, True, "shrunk fuzz coverage accepted with watch", candidates=cand_t, selected=selected, **common)
    return _report(FuzzShrinkDecisionKind.ACCEPT_SHRUNK_COVERAGE, True, False, "shrunk fuzz coverage accepted", candidates=cand_t, selected=selected, **common)


def _report(kind: FuzzShrinkDecisionKind, accept: bool, watch: bool, reason: str, *, fuzz_report_digest: bytes, fuzz_ledger_digest: bytes, generator_digest: bytes, required_mutations: tuple[str, ...], candidates: Iterable[FuzzShrinkCandidate], selected: Iterable[FuzzShrinkCandidate]) -> FuzzShrinkReport:
    cand_t = tuple(candidates)
    selected_t = tuple(selected)
    selected_mutations = tuple(item.mutation for item in selected_t)
    selected_case_digests = tuple(item.shrunk_case_digest for item in selected_t)
    surfaces = {item.surface for item in selected_t}
    families = {item.family_id for item in selected_t}
    paths = {item.path_family for item in selected_t}
    before = sum(item.payload_units_before for item in selected_t)
    after = sum(item.payload_units_after for item in selected_t)
    digest = sha256(FUZZ_SHRINK_DOMAIN + b":report:" + bencode({
        b"kind": kind.value,
        b"accept": 1 if accept else 0,
        b"watch": 1 if watch else 0,
        b"reason": reason,
        b"fuzz": fuzz_report_digest,
        b"ledger": fuzz_ledger_digest,
        b"generator": generator_digest,
        b"required": list(required_mutations),
        b"selected": list(selected_mutations),
        b"cases": list(selected_case_digests),
        b"candidate_count": len(cand_t),
        b"surfaces": sorted(surfaces),
        b"families": len(families),
        b"paths": len(paths),
        b"before": before,
        b"after": after,
        b"saved": before - after,
    }))
    return FuzzShrinkReport(kind, accept, watch, reason, fuzz_report_digest, fuzz_ledger_digest, generator_digest, required_mutations, selected_mutations, selected_case_digests, len(cand_t), len(surfaces), len(families), len(paths), before, after, before - after, digest)
