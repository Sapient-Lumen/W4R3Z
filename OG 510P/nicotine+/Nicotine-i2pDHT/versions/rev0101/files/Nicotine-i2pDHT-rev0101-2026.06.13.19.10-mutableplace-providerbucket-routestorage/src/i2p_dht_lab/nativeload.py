"""rev0087 native load gate.

A native artifact selected/promoted by earlier lanes is still not loaded by
accident.  Loading is modeled as a no-network, exact-boundary permission that
binds selection, promotion, fallback-journal memory, artifact/source/fallback
digests, loader identity, sequence memory, and diversity pressure.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .bencode import bencode
from .ids import DOMAIN, sha256
from .fallbackjournal import FallbackJournalReport
from .nativepromotion import NativePromotionReport
from .nativeselection import NativeSelectionReport

NATIVE_LOAD_DOMAIN = DOMAIN + b":native-load-v1:"


class NativeLoadDecisionKind(str, Enum):
    ACCEPT_NATIVE_LOAD = "accept_native_load"
    ACCEPT_STAY_FALLBACK = "accept_stay_fallback"
    HOLD_PROMOTION_OR_SELECTION_WATCH = "hold_promotion_or_selection_watch"
    QUARANTINE_DIGEST_DRIFT = "quarantine_digest_drift"
    QUARANTINE_SCOPE_DRIFT = "quarantine_scope_drift"
    QUARANTINE_NATIVE_DISABLED_BUT_REQUIRED = "quarantine_native_disabled_but_required"
    QUARANTINE_REPLAY_OR_ROLLBACK = "quarantine_replay_or_rollback"
    QUARANTINE_SAME_SEQUENCE_FORK = "quarantine_same_sequence_fork"
    QUARANTINE_PREVIOUS_LINK_MISMATCH = "quarantine_previous_link_mismatch"
    QUARANTINE_LOW_DIVERSITY = "quarantine_low_diversity"


@dataclass(frozen=True)
class NativeLoadIntent:
    component: str
    profile: str
    operation: str
    request_id: str
    sequence: int
    previous_digest: bytes
    selection_digest: bytes
    promotion_digest: bytes
    fallback_journal_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    loader_id: str
    load_mode: str
    native_enabled: bool
    native_required: bool
    family_id: str
    path_family_id: str
    note: str = ""

    @property
    def intent_digest(self) -> bytes:
        return sha256(NATIVE_LOAD_DOMAIN + b":intent:" + bencode({
            b"component": self.component,
            b"profile": self.profile,
            b"operation": self.operation,
            b"request": self.request_id,
            b"seq": self.sequence,
            b"prev": self.previous_digest,
            b"selection": self.selection_digest,
            b"promotion": self.promotion_digest,
            b"fallback_journal": self.fallback_journal_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"loader": self.loader_id,
            b"mode": self.load_mode,
            b"native_enabled": 1 if self.native_enabled else 0,
            b"native_required": 1 if self.native_required else 0,
            b"family": self.family_id,
            b"path_family": self.path_family_id,
            b"note": self.note,
        }))


@dataclass(frozen=True)
class NativeLoadReport:
    decision_kind: NativeLoadDecisionKind
    accepted: bool
    native_load_allowed: bool
    fallback_active: bool
    watch: bool
    quarantine: bool
    obligations: tuple[str, ...]
    intent_digest: bytes
    selection_digest: bytes
    promotion_digest: bytes
    fallback_journal_digest: bytes
    artifact_digest: bytes
    source_digest: bytes
    fallback_digest: bytes
    loader_id: str
    family_count: int
    path_family_count: int

    @property
    def report_digest(self) -> bytes:
        return sha256(NATIVE_LOAD_DOMAIN + b":report:" + bencode({
            b"decision": NativeLoadDecisionKind(self.decision_kind).value,
            b"accepted": 1 if self.accepted else 0,
            b"native_load_allowed": 1 if self.native_load_allowed else 0,
            b"fallback_active": 1 if self.fallback_active else 0,
            b"watch": 1 if self.watch else 0,
            b"quarantine": 1 if self.quarantine else 0,
            b"obligations": list(self.obligations),
            b"intent": self.intent_digest,
            b"selection": self.selection_digest,
            b"promotion": self.promotion_digest,
            b"fallback_journal": self.fallback_journal_digest,
            b"artifact": self.artifact_digest,
            b"source": self.source_digest,
            b"fallback": self.fallback_digest,
            b"loader": self.loader_id,
            b"family_count": self.family_count,
            b"path_family_count": self.path_family_count,
        }))


def assess_native_load(
    selection: NativeSelectionReport,
    promotion: NativePromotionReport,
    fallback_journal: FallbackJournalReport,
    intent: NativeLoadIntent,
    *,
    previous: NativeLoadIntent | None = None,
    prior_intent_digests: tuple[bytes, ...] = (),
    observed_families: tuple[str, ...] = (),
    observed_path_families: tuple[str, ...] = (),
    min_families: int = 2,
    min_path_families: int = 2,
) -> NativeLoadReport:
    families = set(observed_families or (intent.family_id,))
    path_families = set(observed_path_families or (intent.path_family_id,))

    def report(kind: NativeLoadDecisionKind, accepted: bool, native: bool, fallback: bool, watch: bool, quarantine: bool, obligations: tuple[str, ...]) -> NativeLoadReport:
        return NativeLoadReport(kind, accepted, native, fallback, watch, quarantine, obligations, intent.intent_digest, selection.report_digest, promotion.report_digest, fallback_journal.report_digest, intent.artifact_digest, intent.source_digest, intent.fallback_digest, intent.loader_id, len(families), len(path_families))

    if intent.intent_digest in prior_intent_digests:
        return report(NativeLoadDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, True, ("native-load-replay", "use-python-fallback"))
    if previous is not None:
        if intent.sequence < previous.sequence:
            return report(NativeLoadDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK, False, False, True, False, True, ("native-load-rollback",))
        if intent.sequence == previous.sequence and intent.intent_digest != previous.intent_digest:
            return report(NativeLoadDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK, False, False, True, False, True, ("native-load-same-sequence-fork",))
        if intent.sequence > previous.sequence and intent.previous_digest != previous.intent_digest:
            return report(NativeLoadDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH, False, False, True, False, True, ("native-load-previous-link-mismatch",))
    if len(families) < min_families or len(path_families) < min_path_families:
        return report(NativeLoadDecisionKind.QUARANTINE_LOW_DIVERSITY, False, False, True, False, True, ("native-load-low-diversity", "fallback-only"))
    if not all((intent.component, intent.profile, intent.operation, intent.request_id, intent.loader_id, intent.load_mode)):
        return report(NativeLoadDecisionKind.QUARANTINE_SCOPE_DRIFT, False, False, True, False, True, ("native-load-missing-scope-or-loader",))
    if intent.selection_digest != selection.report_digest or intent.promotion_digest != promotion.report_digest or intent.fallback_journal_digest != fallback_journal.report_digest:
        return report(NativeLoadDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, True, ("native-load-component-digest-drift",))
    if intent.artifact_digest != selection.artifact_digest or intent.source_digest != selection.source_digest or intent.fallback_digest != selection.fallback_digest:
        return report(NativeLoadDecisionKind.QUARANTINE_DIGEST_DRIFT, False, False, True, False, True, ("native-load-artifact-source-or-fallback-drift",))
    if not intent.native_enabled:
        if intent.native_required:
            return report(NativeLoadDecisionKind.QUARANTINE_NATIVE_DISABLED_BUT_REQUIRED, False, False, True, False, True, ("native-required-but-disabled",))
        return report(NativeLoadDecisionKind.ACCEPT_STAY_FALLBACK, True, False, True, False, False, ("profile-disabled-native-load", "python-fallback-active"))
    if selection.watch or promotion.watch or fallback_journal.watch:
        return report(NativeLoadDecisionKind.HOLD_PROMOTION_OR_SELECTION_WATCH, False, False, True, True, False, ("native-load-watch-from-selection-promotion-or-fallback",))
    if not selection.accepted or not selection.native_selected or not promotion.accepted or not promotion.native_active:
        if intent.native_required:
            return report(NativeLoadDecisionKind.QUARANTINE_NATIVE_DISABLED_BUT_REQUIRED, False, False, True, False, True, ("native-required-but-selection-or-promotion-not-native",))
        return report(NativeLoadDecisionKind.ACCEPT_STAY_FALLBACK, True, False, True, selection.watch or promotion.watch, selection.quarantine or promotion.quarantine, ("selection-or-promotion-keeps-fallback", "do-not-load-native"))
    if selection.quarantine or promotion.quarantine or fallback_journal.quarantine:
        return report(NativeLoadDecisionKind.HOLD_PROMOTION_OR_SELECTION_WATCH, False, False, True, True, selection.quarantine or promotion.quarantine or fallback_journal.quarantine, ("native-load-held-by-quarantine-memory",))
    return report(NativeLoadDecisionKind.ACCEPT_NATIVE_LOAD, True, True, True, False, False, ("native-load-dry-permission-only", "python-fallback-remains-bound", "no-parser-no-crypto-no-transport"))
