from __future__ import annotations

from dataclasses import replace

from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.migrationlane import (
    MigrationDecisionKind,
    MigrationManifest,
    MigrationPolicy,
    StateAtom,
    StateAtomKind,
    assess_state_migration,
    state_digest,
)
from i2p_dht_lab.negotiationlane import (
    NegotiationDecisionKind,
    NegotiationPolicy,
    ProtocolOffer,
    ProtocolSelection,
    assess_protocol_negotiation,
)
from i2p_dht_lab.safestart import SafeStartDecisionKind, SafeStartIntent, assess_safe_start
from i2p_dht_lab.samtrace import SamTraceDecisionKind, SamTraceReport


def kp(label: str) -> DhtKeypair:
    return DhtKeypair.from_seed(sha256(("rev0033:" + label).encode("utf-8")))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def node(label: str) -> bytes:
    return NodeIdentity.create(destination=f"{label}.b32.i2p", keypair=kp("node:" + label)).node_id


def offer(label: str, *, versions=(1, 2), features=("stream-v1", "mutable-heads", "range-sketch"), required=("stream-v1",), policy_digest=None, max_frame=8192, seq=1, now=1_766_800_000) -> ProtocolOffer:
    return ProtocolOffer.create(
        keypair=kp("offer:" + label),
        node_id=node(label),
        source_family="source-" + label,
        path_family="path-" + label,
        versions=versions,
        features=features,
        required_features=required,
        namespace_policy_digest=policy_digest or digest("namespace-policy"),
        max_frame_bytes=max_frame,
        sequence=seq,
        issued_at=now,
        ttl=300,
    )


def atom(label: str, kind: StateAtomKind, *, seq=1, scope="scope", now=1_766_800_000, expires=None) -> StateAtom:
    return StateAtom(
        kind=kind,
        scope_id=digest(scope),
        object_digest=digest("object:" + label),
        value_digest=digest("value:" + label + ":" + str(seq)),
        sequence=seq,
        issued_at=now,
        expires_at=expires or now + 10_000,
        source_family="source-A",
        path_family="path-A",
    )


def manifest_for(input_atoms, output_atoms, *, label="main", soft_drop=0, seq=1, generation=1, now=1_766_800_000) -> MigrationManifest:
    return MigrationManifest.create(
        keypair=kp("migration:" + label),
        from_schema="rev0032-local-state",
        to_schema="rev0033-local-state",
        generation=generation,
        prev_manifest_digest=b"\x00" * 32,
        input_atoms=input_atoms,
        output_atoms=output_atoms,
        dropped_soft_count=soft_drop,
        sequence=seq,
        issued_at=now,
        ttl=300,
    )


def sam_report(kind: SamTraceDecisionKind = SamTraceDecisionKind.ACCEPT_SCOPE_BOUND_TRACE, *, accept=True) -> SamTraceReport:
    return SamTraceReport(
        decision_kind=kind,
        accept=accept,
        reason="toy samtrace report",
        scope_report_digest=digest("scope-report"),
        sam_report_digest=digest("sam-report"),
        egress_report_digest=digest("egress-report"),
        shadow_report_digests=(digest("shadow-report"),),
        send_count=1,
        reconnect_count=0,
        pressure_digests=(),
        report_digest=digest("samtrace-report:" + kind.value + str(accept)),
    )


def test_negotiation_accepts_highest_shared_signed_selection() -> None:
    now = 1_766_800_000
    local = offer("local", now=now)
    remote = offer("remote", now=now)
    selection = ProtocolSelection.create(
        keypair=kp("selector"),
        request_id=digest("request"),
        local_offer=local,
        remote_offer=remote,
        chosen_version=2,
        chosen_features=("stream-v1", "mutable-heads"),
        sequence=1,
        issued_at=now + 1,
        ttl=200,
    )
    report = assess_protocol_negotiation(local, remote, now=now + 2, selection=selection, policy=NegotiationPolicy(max_version=2, required_features=("stream-v1", "mutable-heads")))
    assert report.decision_kind is NegotiationDecisionKind.ACCEPT_NEGOTIATION
    assert report.accept
    assert report.chosen_version == 2
    assert "mutable-heads" in report.chosen_features


def test_negotiation_blocks_downgrade_policy_mismatch_and_missing_feature() -> None:
    now = 1_766_800_100
    local = offer("local-dg", versions=(1, 2), now=now)
    remote = offer("remote-dg", versions=(1, 2), now=now)
    downgrade = ProtocolSelection.create(keypair=kp("selector-dg"), request_id=digest("request-dg"), local_offer=local, remote_offer=remote, chosen_version=1, chosen_features=("stream-v1",), sequence=1, issued_at=now, ttl=300)
    report = assess_protocol_negotiation(local, remote, now=now + 1, selection=downgrade, policy=NegotiationPolicy(max_version=2, required_features=("stream-v1",)))
    assert report.decision_kind is NegotiationDecisionKind.QUARANTINE_DOWNGRADE

    bad_policy = assess_protocol_negotiation(local, offer("remote-policy", policy_digest=digest("other-policy"), now=now), now=now + 1, policy=NegotiationPolicy(max_version=2))
    assert bad_policy.decision_kind is NegotiationDecisionKind.QUARANTINE_POLICY_DIGEST_MISMATCH

    missing = assess_protocol_negotiation(local, offer("remote-missing", features=("stream-v1",), required=("stream-v1",), now=now), now=now + 1, policy=NegotiationPolicy(max_version=2, required_features=("range-sketch",)))
    assert missing.decision_kind is NegotiationDecisionKind.QUARANTINE_REQUIRED_FEATURE_MISSING


def test_negotiation_catches_offer_replay_sequence_fork_and_frame_budget() -> None:
    now = 1_766_800_200
    local = offer("local-replay", now=now)
    replay = assess_protocol_negotiation(local, local, now=now + 1, policy=NegotiationPolicy(max_version=2))
    assert replay.decision_kind is NegotiationDecisionKind.QUARANTINE_REPLAYED_OFFER

    fork_base = offer("fork-base", now=now)
    fork_other = replace(fork_base, max_frame_bytes=fork_base.max_frame_bytes + 1)
    fork_report = assess_protocol_negotiation(fork_base, fork_other, now=now + 1, policy=NegotiationPolicy(max_version=2))
    assert fork_report.decision_kind in {NegotiationDecisionKind.QUARANTINE_BAD_OFFER_SIGNATURE, NegotiationDecisionKind.QUARANTINE_SEQUENCE_FORK}

    small = assess_protocol_negotiation(offer("small-local", max_frame=512, now=now), offer("small-remote", max_frame=2048, now=now), now=now + 1, policy=NegotiationPolicy(max_version=2, min_frame_bytes=1024))
    assert small.decision_kind is NegotiationDecisionKind.QUARANTINE_FRAME_BUDGET_TOO_SMALL


def test_migration_preserves_hard_negatives_and_allows_counted_soft_drop() -> None:
    now = 1_766_801_000
    tomb = atom("gone", StateAtomKind.TOMBSTONE, now=now)
    provider_false = atom("liar", StateAtomKind.PROVIDER_FALSE, now=now)
    soft = atom("cache", StateAtomKind.SOFT_CACHE, now=now)
    migrated = (tomb, provider_false)
    manifest = manifest_for((tomb, provider_false, soft), migrated, soft_drop=1, now=now)
    report = assess_state_migration((tomb, provider_false, soft), migrated, manifest, now=now + 1)
    assert report.decision_kind is MigrationDecisionKind.ACCEPT_WITH_SOFT_DROP
    assert report.accept
    assert report.hard_negative_count == 2
    assert report.dropped_soft_count == 1


def test_migration_blocks_dropped_hard_negative_scope_widening_and_rollback() -> None:
    now = 1_766_801_100
    tomb = atom("gone", StateAtomKind.TOMBSTONE, now=now)
    soft = atom("cache", StateAtomKind.SOFT_CACHE, now=now)
    dropped_manifest = manifest_for((tomb, soft), (soft,), soft_drop=0, label="drop-hard", now=now)
    dropped = assess_state_migration((tomb, soft), (soft,), dropped_manifest, now=now + 1)
    assert dropped.decision_kind is MigrationDecisionKind.QUARANTINE_DROPPED_HARD_NEGATIVE

    stable = atom("same", StateAtomKind.PROVIDER_FALSE, seq=3, now=now)
    moved_scope = StateAtom(kind=stable.kind, scope_id=digest("other-scope"), object_digest=stable.object_digest, value_digest=stable.value_digest, sequence=stable.sequence, issued_at=stable.issued_at, expires_at=stable.expires_at, source_family=stable.source_family, path_family=stable.path_family)
    scope_manifest = manifest_for((stable,), (moved_scope,), label="scope-widen", now=now)
    widened = assess_state_migration((stable,), (moved_scope,), scope_manifest, now=now + 1)
    assert widened.decision_kind is MigrationDecisionKind.QUARANTINE_SCOPE_WIDENING

    rolled = StateAtom(kind=stable.kind, scope_id=stable.scope_id, object_digest=stable.object_digest, value_digest=digest("rolled-value"), sequence=2, issued_at=now, expires_at=now + 10_000, source_family=stable.source_family, path_family=stable.path_family)
    roll_manifest = manifest_for((stable,), (rolled,), label="rollback", now=now)
    rolled_report = assess_state_migration((stable,), (rolled,), roll_manifest, now=now + 1)
    assert rolled_report.decision_kind is MigrationDecisionKind.QUARANTINE_SEQUENCE_ROLLBACK


def test_migration_catches_digest_mismatch_replay_and_schema_window() -> None:
    now = 1_766_801_200
    soft = atom("cache", StateAtomKind.SOFT_CACHE, now=now)
    migrated = (soft,)
    manifest = manifest_for((soft,), migrated, now=now)
    tampered = replace(manifest, output_digest=state_digest(()))
    bad_output = assess_state_migration((soft,), migrated, tampered, now=now + 1)
    assert bad_output.decision_kind in {MigrationDecisionKind.QUARANTINE_BAD_SIGNATURE, MigrationDecisionKind.QUARANTINE_OUTPUT_DIGEST_MISMATCH}

    replay = assess_state_migration((soft,), migrated, manifest, now=now + 1, previous_manifest=manifest)
    assert replay.decision_kind is MigrationDecisionKind.QUARANTINE_REPLAYED_MANIFEST

    wrong_schema = MigrationManifest.create(keypair=kp("migration:schema"), from_schema="old", to_schema="new", generation=1, prev_manifest_digest=b"\x00" * 32, input_atoms=(soft,), output_atoms=migrated, dropped_soft_count=0, sequence=1, issued_at=now, ttl=300)
    schema_report = assess_state_migration((soft,), migrated, wrong_schema, now=now + 1)
    assert schema_report.decision_kind is MigrationDecisionKind.HOLD_SCHEMA_WINDOW


def test_safe_start_joins_negotiation_migration_and_transport_trace() -> None:
    now = 1_766_802_000
    local = offer("safe-local", now=now)
    remote = offer("safe-remote", now=now)
    negotiation = assess_protocol_negotiation(local, remote, now=now + 1, policy=NegotiationPolicy(max_version=2, required_features=("stream-v1",)))
    hard = atom("crisis", StateAtomKind.KEY_CRISIS, now=now)
    migration = assess_state_migration((hard,), (hard,), manifest_for((hard,), (hard,), label="safe", now=now), now=now + 1)
    intent = SafeStartIntent(session_id=digest("session"), scope_id=digest("scope"), object_digest=digest("object"), request_id=digest("request"), purpose="bootstrap")
    report = assess_safe_start(intent, negotiation=negotiation, migration=migration, samtrace=sam_report())
    assert report.decision_kind is SafeStartDecisionKind.ACCEPT_SAFE_START
    assert report.accept


def test_safe_start_blocks_quarantined_negotiation_migration_and_samtrace() -> None:
    now = 1_766_802_100
    local = offer("bad-safe-local", now=now)
    remote = offer("bad-safe-remote", now=now)
    downgraded_selection = ProtocolSelection.create(keypair=kp("selector-bad-safe"), request_id=digest("request-bad-safe"), local_offer=local, remote_offer=remote, chosen_version=1, chosen_features=("stream-v1",), sequence=1, issued_at=now, ttl=300)
    bad_negotiation = assess_protocol_negotiation(local, remote, now=now + 1, selection=downgraded_selection, policy=NegotiationPolicy(max_version=2))

    hard = atom("lost", StateAtomKind.REVOCATION, now=now)
    bad_migration = assess_state_migration((hard,), (), manifest_for((hard,), (), label="bad-safe", now=now), now=now + 1)
    ok_migration = assess_state_migration((hard,), (hard,), manifest_for((hard,), (hard,), label="ok-safe", now=now), now=now + 1)
    intent = SafeStartIntent(session_id=digest("session-bad"), scope_id=digest("scope-bad"), object_digest=digest("object-bad"), request_id=digest("request-bad"), purpose="bootstrap")

    blocked_neg = assess_safe_start(intent, negotiation=bad_negotiation, migration=ok_migration, samtrace=sam_report())
    assert blocked_neg.decision_kind is SafeStartDecisionKind.QUARANTINE_NEGOTIATION

    ok_neg = assess_protocol_negotiation(local, remote, now=now + 1, policy=NegotiationPolicy(max_version=2))
    blocked_migration = assess_safe_start(intent, negotiation=ok_neg, migration=bad_migration, samtrace=sam_report())
    assert blocked_migration.decision_kind is SafeStartDecisionKind.QUARANTINE_MIGRATION

    blocked_sam = assess_safe_start(intent, negotiation=ok_neg, migration=ok_migration, samtrace=sam_report(SamTraceDecisionKind.QUARANTINE_EGRESS, accept=False))
    assert blocked_sam.decision_kind is SafeStartDecisionKind.QUARANTINE_SAMTRACE
