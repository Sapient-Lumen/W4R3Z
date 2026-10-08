"""rev0085 native quarantine store.

When native provenance or differential corpus evidence fails, the failure becomes
sticky local memory.  Quarantine is not a panic button; it is the thing that
prevents a later restart from rediscovering the same artifact as fresh.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .nativebudget import NativeBudgetReport
from .nativecorpus import NativeCorpusReport
from .nativeprovenance import NativeProvenanceReport

NATIVE_QUARANTINE_DOMAIN = DOMAIN + b":native-quarantine-v1:"


class NativeQuarantineDecisionKind(str, Enum):
    ACCEPT_NATIVE_NO_QUARANTINE = "accept_native_no_quarantine"
    RECORD_NATIVE_QUARANTINE = "record_native_quarantine"
    HOLD_MISSING_QUARANTINE_MARKER = "hold_missing_quarantine_marker"
    QUARANTINE_MARKER_REPLAY_OR_ROLLBACK = "quarantine_marker_replay_or_rollback"
    QUARANTINE_MARKER_FORK = "quarantine_marker_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_MARKER_DIGEST_DRIFT = "quarantine_marker_digest_drift"
    QUARANTINE_NO_FALLBACK = "quarantine_no_fallback"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeQuarantineMarker:
    component: str
    profile: str
    sequence: int
    previous_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    provenance_digest: bytes
    corpus_digest: bytes
    budget_digest: bytes
    reason: str
    fallback_digest: bytes
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def marker_digest(self) -> bytes:
        return sha256(NATIVE_QUARANTINE_DOMAIN + b":marker:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"provenance": self.provenance_digest,
            b"corpus": self.corpus_digest,
            b"budget": self.budget_digest,
            b"reason": self.reason,
            b"fallback": self.fallback_digest,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeQuarantineReport:
    decision_kind: NativeQuarantineDecisionKind
    accepted: bool
    native_allowed: bool
    fallback_only: bool
    watch: bool
    quarantine: bool
    marker_digest: bytes
    provenance_digest: bytes
    corpus_digest: bytes
    budget_digest: bytes
    family_count: int
    path_family_count: int
    obligations: tuple[str, ...]

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_QUARANTINE_DOMAIN + b":report:" + bencode({
            b"decision": NativeQuarantineDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"native_allowed": 1 if self.native_allowed else 0,
            b"fallback_only": 1 if self.fallback_only else 0,
            b"watch": 1 if self.watch else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"marker": self.marker_digest,
            b"provenance": self.provenance_digest,
            b"corpus": self.corpus_digest,
            b"budget": self.budget_digest,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
            b"obligations": list(self.obligations),
        }))


def assess_native_quarantine(
    provenance: NativeProvenanceReport,
    corpus: NativeCorpusReport,
    budget: NativeBudgetReport,
    marker: NativeQuarantineMarker | None = None,
    *,
    previous: NativeQuarantineMarker | None = None,
    prior_marker_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeQuarantineReport:
    zero = b""
    families = set(observed_families or ((marker.family_id,) if marker else ()))
    path_families = set(observed_path_families or ((marker.path_family_id,) if marker else ()))

    def digest(attr: str, fallback: bytes = zero) -> bytes:
        return getattr(marker, attr) if marker is not None else fallback

    def report(kind: NativeQuarantineDecisionKind, accepted: bool, native: bool, fallback_only: bool, watch: bool, quarantine: bool, obligations: tuple[str, ...]) -> NativeQuarantineReport:
        return NativeQuarantineReport(kind, accepted, native, fallback_only, watch, quarantine, digest("marker_digest"), provenance.report_digest, corpus.report_digest, budget.report_digest, len(families), len(path_families), obligations)

    native_healthy = provenance.accepted and corpus.accepted and budget.accepted and not corpus.quarantine and not provenance.quarantine
    if native_healthy and marker is None:
        return report(NativeQuarantineDecisionKind.ACCEPT_NATIVE_NO_QUARANTINE, True, True, False, False, False, ("native-quarantine-not-needed", "keep-python-fallback"))
    if marker is None:
        return report(NativeQuarantineDecisionKind.HOLD_MISSING_QUARANTINE_MARKER, False, False, True, True, False, ("bad-native-evidence-needs-sticky-quarantine-marker", "use-python-fallback"))

    families = set(observed_families or (marker.family_id,))
    path_families = set(observed_path_families or (marker.path_family_id,))

    if marker.marker_digest in prior_marker_digests:
        return report(NativeQuarantineDecisionKind.QUARANTINE_MARKER_REPLAY_OR_ROLLBACK, False, False, True, False, True, ("native-quarantine-marker-replay", "preserve-prior-marker"))
    if previous is not None:
        if marker.sequence < previous.sequence:
            return report(NativeQuarantineDecisionKind.QUARANTINE_MARKER_REPLAY_OR_ROLLBACK, False, False, True, False, True, ("native-quarantine-marker-rollback",))
        if marker.sequence == previous.sequence and marker.marker_digest != previous.marker_digest:
            return report(NativeQuarantineDecisionKind.QUARANTINE_MARKER_FORK, False, False, True, False, True, ("native-quarantine-marker-fork",))
        if marker.sequence > previous.sequence and marker.previous_digest != previous.marker_digest:
            return report(NativeQuarantineDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, True, ("native-quarantine-previous-link-mismatch",))

    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeQuarantineDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, True, ("native-quarantine-low-diversity", "fallback-only"))
    if marker.provenance_digest != provenance.report_digest or marker.corpus_digest != corpus.report_digest or marker.budget_digest != budget.report_digest:
        return report(NativeQuarantineDecisionKind.QUARANTINE_MARKER_DIGEST_DRIFT, False, False, True, False, True, ("native-quarantine-component-digest-drift", "do-not-load-artifact"))
    if not marker.fallback_digest:
        return report(NativeQuarantineDecisionKind.QUARANTINE_NO_FALLBACK, False, False, False, False, True, ("quarantine-needs-fallback-route",))
    if native_healthy and marker.reason == "retired-by-operator":
        return report(NativeQuarantineDecisionKind.RECORD_NATIVE_QUARANTINE, True, False, True, False, True, ("operator-retired-native-artifact", "route-to-python-fallback"))
    if native_healthy:
        return report(NativeQuarantineDecisionKind.ACCEPT_NATIVE_NO_QUARANTINE, True, True, False, False, False, ("healthy-native-evidence-overrides-stale-marker-watch", "do-not-delete-marker-without-retention-policy"))
    return report(NativeQuarantineDecisionKind.RECORD_NATIVE_QUARANTINE, True, False, True, False, True, ("record-native-quarantine", "route-all-calls-to-python", "keep-marker-through-restart"))
