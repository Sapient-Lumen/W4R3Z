from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.nativefoldspine import audit_native_fold_spine
from i2p_dht_lab.nativeoracleseal import (
    NativeOracleSealCapsule,
    NativeOracleSealDecisionKind,
    assess_native_oracle_seal,
)
from i2p_dht_lab.nativepreflight import (
    NativePreflightDecisionKind,
    NativePreflightIntent,
    assess_native_preflight,
)
from i2p_dht_lab.nativereentryjournal import (
    NativeReentryJournalDecisionKind,
    NativeReentryJournalEntry,
    assess_native_reentry_journal,
)
from i2p_dht_lab.nativereentryfold import audit_native_reentry_fold

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = "Nicotine-i2pDHT-rev0091-2026.06.12.13.41-nativereentry-oracleseal-preflight"
ART = sha256(b"artifact")
SRC = sha256(b"source")
FB = sha256(b"fallback")
ORACLE = sha256(b"python-oracle")
CORPUS = sha256(b"differential-corpus")


@dataclass(frozen=True)
class FakeHandoff:
    accepted: bool = True
    relaunch_candidate: bool = True
    fallback_active: bool = True
    native_load_forbidden: bool = True
    dispatch_forbidden: bool = True
    quarantine: bool = False
    watch: bool = False
    artifact_digest: bytes = ART
    source_digest: bytes = SRC
    fallback_digest: bytes = FB
    python_oracle_digest: bytes = ORACLE
    tombstone_carried: bool = True
    fault_memory_carried: bool = True

    @property
    def report_digest(self) -> bytes:
        return sha256(b"fake-handoff:" + self.artifact_digest + (b"1" if self.accepted else b"0") + (b"w" if self.watch else b""))


@dataclass(frozen=True)
class FakeRelaunch:
    accepted: bool = True
    relaunch_plan_ready: bool = True
    fallback_active: bool = True
    native_load_allowed: bool = False
    dispatch_allowed: bool = False
    quarantine: bool = False
    watch: bool = False
    artifact_digest: bytes = ART
    source_digest: bytes = SRC
    fallback_digest: bytes = FB
    python_oracle_digest: bytes = ORACLE

    @property
    def report_digest(self) -> bytes:
        return sha256(b"fake-relaunch:" + self.artifact_digest + (b"1" if self.relaunch_plan_ready else b"0") + (b"w" if self.watch else b""))


@dataclass(frozen=True)
class FakeLoaderSeal:
    accepted: bool = True
    sealed: bool = True
    fallback_active: bool = True
    native_load_forbidden: bool = True
    quarantine: bool = False
    watch: bool = False
    artifact_digest: bytes = ART
    source_digest: bytes = SRC
    fallback_digest: bytes = FB
    python_oracle_digest: bytes = ORACLE
    tombstone_memory: bool = True
    fault_memory: bool = True

    @property
    def report_digest(self) -> bytes:
        return sha256(b"fake-loader-seal:" + self.artifact_digest + (b"1" if self.sealed else b"0") + (b"w" if self.watch else b""))


def _oracle_capsule(loader=FakeLoaderSeal(), **kw):
    data = dict(
        component="xor_distance", profile="portable-default", operation="xor_compare", request_id="rev0091-native",
        sequence=1, previous_digest=b"", loader_seal_digest=loader.report_digest, artifact_digest=ART,
        source_digest=SRC, fallback_digest=FB, python_oracle_digest=ORACLE, differential_corpus_digest=CORPUS,
        allow_native_eval=True, parser_bytes_touched=False, crypto_or_secret_touched=False,
        transport_touched=False, persistence_touched=False, python_fallback_active=True,
        preserve_loader_seal_memory=True, preserve_fallback_memory=True, preserve_tombstone_memory=True,
        preserve_quarantine_memory=True, preserve_crash_memory=True, family_id="family-a", path_family_id="path-a",
    )
    data.update(kw)
    return NativeOracleSealCapsule(**data)


def _oracle(loader=FakeLoaderSeal(), capsule=None):
    cap = capsule or _oracle_capsule(loader)
    return assess_native_oracle_seal(loader, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), cap


def _preflight_intent(handoff=FakeHandoff(), relaunch=FakeRelaunch(), loader=FakeLoaderSeal(), oracle_report=None, **kw):
    if oracle_report is None:
        oracle_report, _ = _oracle(loader)
    data = dict(
        component="xor_distance", profile="portable-default", operation="xor_compare", request_id="rev0091-native",
        sequence=1, previous_digest=b"", handoff_digest=handoff.report_digest, relaunch_gate_digest=relaunch.report_digest,
        loader_seal_digest=loader.report_digest, oracle_seal_digest=oracle_report.report_digest, artifact_digest=ART,
        source_digest=SRC, fallback_digest=FB, python_oracle_digest=ORACLE, loader_id="ctypes-local-xor-v1",
        route_to_load_gate_requested=True, native_load_attempted=False, native_dispatch_attempted=False,
        python_fallback_active=True, preserve_handoff_memory=True, preserve_relaunch_memory=True,
        preserve_loader_seal_memory=True, preserve_oracle_seal_memory=True, preserve_fallback_memory=True,
        preserve_tombstone_memory=True, preserve_quarantine_memory=True, preserve_crash_memory=True,
        family_id="family-a", path_family_id="path-a",
    )
    data.update(kw)
    return NativePreflightIntent(**data)


def _preflight(handoff=FakeHandoff(), relaunch=FakeRelaunch(), loader=FakeLoaderSeal(), oracle_report=None, intent=None):
    if oracle_report is None:
        oracle_report, _ = _oracle(loader)
    cap = intent or _preflight_intent(handoff, relaunch, loader, oracle_report)
    return assess_native_preflight(handoff, relaunch, loader, oracle_report, cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), cap, oracle_report


def _journal_entry(preflight_report, oracle_report, **kw):
    data = dict(
        component="xor_distance", profile="portable-default", operation="xor_compare", request_id="rev0091-native",
        sequence=1, previous_digest=b"", preflight_digest=preflight_report.report_digest,
        oracle_seal_digest=oracle_report.report_digest, artifact_digest=ART, source_digest=SRC, fallback_digest=FB,
        python_oracle_digest=ORACLE, loader_id="ctypes-local-xor-v1", route_to_load_gate_only=True,
        python_fallback_active=True, preserve_preflight_memory=True, preserve_oracle_memory=True,
        preserve_fallback_memory=True, preserve_tombstone_memory=True, preserve_quarantine_memory=True,
        preserve_crash_memory=True, family_id="family-a", path_family_id="path-a",
    )
    data.update(kw)
    return NativeReentryJournalEntry(**data)


def _journal(preflight_report=None, oracle_report=None, entry=None):
    if preflight_report is None:
        preflight_report, _, oracle_report = _preflight()
    if oracle_report is None:
        _, _, oracle_report = _preflight()
    ent = entry or _journal_entry(preflight_report, oracle_report)
    return assess_native_reentry_journal(preflight_report, oracle_report, ent, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")), ent


def test_native_oracle_seal_keeps_python_oracle_as_authority() -> None:
    report, _ = _oracle()
    assert report.decision_kind is NativeOracleSealDecisionKind.ACCEPT_PYTHON_ORACLE_SEAL
    assert report.python_oracle_sealed and report.native_eval_allowed
    assert report.native_load_forbidden and report.dispatch_forbidden

    parser = _oracle_capsule(parser_bytes_touched=True)
    parser_report, _ = _oracle(capsule=parser)
    assert parser_report.decision_kind is NativeOracleSealDecisionKind.QUARANTINE_FORBIDDEN_SURFACE

    crypto = _oracle_capsule(crypto_or_secret_touched=True)
    crypto_report, _ = _oracle(capsule=crypto)
    assert crypto_report.decision_kind is NativeOracleSealDecisionKind.QUARANTINE_FORBIDDEN_SURFACE

    disabled = _oracle_capsule(allow_native_eval=False)
    disabled_report, _ = _oracle(capsule=disabled)
    assert disabled_report.decision_kind is NativeOracleSealDecisionKind.HOLD_NATIVE_EVAL_DISABLED

    bad_digest = _oracle_capsule(loader_seal_digest=sha256(b"wrong-loader"))
    digest_report, _ = _oracle(capsule=bad_digest)
    assert digest_report.decision_kind is NativeOracleSealDecisionKind.QUARANTINE_DIGEST_DRIFT

    memory_drop = _oracle_capsule(preserve_crash_memory=False)
    memory_report, _ = _oracle(capsule=memory_drop)
    assert memory_report.decision_kind is NativeOracleSealDecisionKind.QUARANTINE_MEMORY_DROP


def test_native_preflight_routes_to_load_gate_only() -> None:
    report, _, _ = _preflight()
    assert report.decision_kind is NativePreflightDecisionKind.ACCEPT_ROUTE_TO_LOAD_GATE_ONLY
    assert report.route_to_load_gate_only
    assert not report.native_load_allowed and not report.dispatch_allowed
    assert report.fallback_active and report.tombstone_memory and report.fault_memory

    dispatch_intent = _preflight_intent(native_dispatch_attempted=True)
    dispatch_report, _, _ = _preflight(intent=dispatch_intent)
    assert dispatch_report.decision_kind is NativePreflightDecisionKind.QUARANTINE_DISPATCH_OR_LOAD_ATTEMPT

    bad_oracle, _ = _oracle(capsule=_oracle_capsule(parser_bytes_touched=True))
    hold_oracle, _, _ = _preflight(oracle_report=bad_oracle)
    assert hold_oracle.decision_kind is NativePreflightDecisionKind.HOLD_ORACLE_SEAL_NOT_READY

    no_handoff = FakeHandoff(relaunch_candidate=False)
    hold_handoff, _, _ = _preflight(handoff=no_handoff)
    assert hold_handoff.decision_kind is NativePreflightDecisionKind.HOLD_HANDOFF_NOT_READY

    drift = _preflight_intent(artifact_digest=sha256(b"wrong-artifact"))
    drift_report, _, _ = _preflight(intent=drift)
    assert drift_report.decision_kind is NativePreflightDecisionKind.QUARANTINE_DIGEST_DRIFT

    memory_drop = _preflight_intent(preserve_oracle_seal_memory=False)
    memory_report, _, _ = _preflight(intent=memory_drop)
    assert memory_report.decision_kind is NativePreflightDecisionKind.QUARANTINE_MEMORY_DROP


def test_reentry_journal_preserves_preflight_and_oracle_memory() -> None:
    preflight_report, _, oracle_report = _preflight()
    report, _ = _journal(preflight_report, oracle_report)
    assert report.decision_kind is NativeReentryJournalDecisionKind.ACCEPT_REENTRY_JOURNAL
    assert report.journaled and report.route_to_load_gate_only
    assert report.native_load_forbidden and report.dispatch_forbidden

    not_ready = replace(preflight_report, accepted=False, route_to_load_gate_only=False)
    hold, _ = _journal(not_ready, oracle_report)
    assert hold.decision_kind is NativeReentryJournalDecisionKind.HOLD_PREFLIGHT_NOT_READY

    drift_entry = _journal_entry(preflight_report, oracle_report, preflight_digest=sha256(b"wrong-preflight"))
    drift, _ = _journal(preflight_report, oracle_report, drift_entry)
    assert drift.decision_kind is NativeReentryJournalDecisionKind.QUARANTINE_DIGEST_DRIFT

    drop_entry = _journal_entry(preflight_report, oracle_report, preserve_fallback_memory=False)
    drop, _ = _journal(preflight_report, oracle_report, drop_entry)
    assert drop.decision_kind is NativeReentryJournalDecisionKind.QUARANTINE_MEMORY_DROP


def test_reentry_surfaces_detect_replay_fork_link_and_low_diversity() -> None:
    first = _oracle_capsule()
    replay = assess_native_oracle_seal(FakeLoaderSeal(), first, prior_capsule_digests=(first.capsule_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert replay.decision_kind is NativeOracleSealDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK
    fork = assess_native_oracle_seal(FakeLoaderSeal(), replace(first, note="fork"), previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert fork.decision_kind is NativeOracleSealDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    bad_link = replace(first, sequence=2, previous_digest=sha256(b"bad-prev"))
    link = assess_native_oracle_seal(FakeLoaderSeal(), bad_link, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert link.decision_kind is NativeOracleSealDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    low = assess_native_oracle_seal(FakeLoaderSeal(), first, observed_families=("family-a",), observed_path_families=("path-a",))
    assert low.decision_kind is NativeOracleSealDecisionKind.QUARANTINE_LOW_DIVERSITY

    preflight_report, intent, oracle_report = _preflight()
    replay_preflight = assess_native_preflight(FakeHandoff(), FakeRelaunch(), FakeLoaderSeal(), oracle_report, intent, prior_intent_digests=(intent.intent_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert replay_preflight.decision_kind is NativePreflightDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK

    journal_entry = _journal_entry(preflight_report, oracle_report)
    replay_journal = assess_native_reentry_journal(preflight_report, oracle_report, journal_entry, prior_entry_digests=(journal_entry.entry_digest,), observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    assert replay_journal.decision_kind is NativeReentryJournalDecisionKind.QUARANTINE_REPLAY_OR_ROLLBACK


def test_native_reentry_fold_and_spine_happy_path() -> None:
    spine = audit_native_fold_spine(ROOT, revision="rev0091")
    assert spine.status == "pass"
    assert spine.checked_count >= 11
    fold = audit_native_reentry_fold(ROOT, revision="rev0091", artifact_stem=ARTIFACT)
    assert fold.status == "pass"
    assert fold.predecessor_status == "pass"
    assert fold.foldmap_status == "pass"
    assert fold.foldregistry_status == "pass"
    assert fold.surface_ledger_status == "pass"
    assert fold.native_spine_status == "pass"
