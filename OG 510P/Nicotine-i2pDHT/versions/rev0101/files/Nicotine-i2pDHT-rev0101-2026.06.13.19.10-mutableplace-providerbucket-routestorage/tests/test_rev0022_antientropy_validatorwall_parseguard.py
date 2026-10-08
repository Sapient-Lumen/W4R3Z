from __future__ import annotations

import pytest

from i2p_dht_lab.antientropy import (
    AntiEntropyDecisionKind,
    AntiEntropyPolicy,
    AntiEntropySummary,
    LocalAntiEntropyState,
    SummaryItem,
    SummaryItemKind,
    plan_anti_entropy,
)
from i2p_dht_lab.bencode import bencode
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.parseguard import ParseGuardError, ParseGuardKind, ParseLimits, bdecode_guarded
from i2p_dht_lab.surfaceindex import audit_surface_index
from i2p_dht_lab.validatorwall import (
    PayloadEnvelope,
    PayloadRole,
    ValidatorWallDecisionKind,
    ValidatorWallPolicy,
    analyze_validator_window,
    validate_payload_wall,
)
from i2p_dht_lab.wirecanon import WireFrame, WireMessageKind


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n % 256]) * 32)


def ident(n: int) -> NodeIdentity:
    return NodeIdentity.create(destination=f"rev0022-{n}.b32.i2p", keypair=kp(n))


def digest(label: str) -> bytes:
    return sha256(label.encode("utf-8"))


def item(kind: SummaryItemKind, label: str, seq: int, *, scope: str = "scope-A") -> SummaryItem:
    return SummaryItem(kind=kind, scope_id=digest(scope), sequence=seq, digest=digest(label))


def summary(node: int, family: str, items: tuple[SummaryItem, ...], *, issued_at: int = 10_000, ttl: int = 300, sequence: int = 0) -> AntiEntropySummary:
    node_id = ident(node).node_id
    return AntiEntropySummary.create(keypair=kp(node), source_node_id=node_id, source_family=family, issued_at=issued_at, ttl=ttl, items=items, sequence=sequence)


def frame_for_payload(node: int, kind: WireMessageKind, payload: bytes, *, request_label: str = "request", flags: tuple[str, ...] = ()) -> WireFrame:
    return WireFrame.create(keypair=kp(node), sender_node_id=ident(node).node_id, message_kind=kind, request_id=digest(request_label), payload=payload, issued_at=20_000, ttl=300, flags=flags)


# --- parseguard -----------------------------------------------------------


def test_parseguard_accepts_canonical_roundtrip_and_digest_is_stable() -> None:
    data = bencode({b"a": 1, b"b": [b"x", {b"c": 2}]})
    report = bdecode_guarded(data)
    assert report.kind is ParseGuardKind.ACCEPT_CANONICAL
    assert report.consumed == len(data)
    assert bencode(report.value) == data
    assert report.digest == bdecode_guarded(data).digest


@pytest.mark.parametrize(
    "data,kind",
    [
        (b"i03e", ParseGuardKind.REJECT_INVALID_INTEGER),
        (b"i-0e", ParseGuardKind.REJECT_INVALID_INTEGER),
        (b"03:abc", ParseGuardKind.REJECT_STRING_LENGTH),
        (b"d1:b1:y1:a1:xe", ParseGuardKind.REJECT_UNSORTED_KEY),
        (b"d1:a1:x1:a1:ye", ParseGuardKind.REJECT_DUPLICATE_KEY),
        (b"1:a1:b", ParseGuardKind.REJECT_TRAILING_DATA),
    ],
)
def test_parseguard_rejects_noncanonical_or_ambiguous_inputs(data: bytes, kind: ParseGuardKind) -> None:
    with pytest.raises(ParseGuardError) as excinfo:
        bdecode_guarded(data)
    assert excinfo.value.kind is kind


def test_parseguard_enforces_depth_and_size_limits() -> None:
    with pytest.raises(ParseGuardError) as excinfo:
        bdecode_guarded(b"l" * 6 + b"e" * 6, limits=ParseLimits(max_depth=3))
    assert excinfo.value.kind is ParseGuardKind.REJECT_DEPTH_LIMIT
    with pytest.raises(ParseGuardError) as excinfo2:
        bdecode_guarded(b"5:abcde", limits=ParseLimits(max_bytes=4))
    assert excinfo2.value.kind is ParseGuardKind.REJECT_TOO_LARGE


# --- validator wall -------------------------------------------------------


def test_validatorwall_accepts_role_kind_scope_and_body_digest() -> None:
    body = b"mutable-head-body"
    env = PayloadEnvelope.create(namespace="i2p-dht-control", role=PayloadRole.MUTABLE_HEAD, scope_id=digest("scope"), body=body, issued_at=20_000, ttl=300)
    payload = env.to_bytes()
    frame = frame_for_payload(1, WireMessageKind.EPOCH_HEAD, payload, flags=("head",))
    report = validate_payload_wall(frame, payload=payload, body=body, now=20_010, expected_scope_id=digest("scope"))
    assert report.decision.kind is ValidatorWallDecisionKind.ACCEPT_VALIDATED_PAYLOAD
    assert report.decision.accept


def test_validatorwall_rejects_role_kind_confusion_even_with_valid_wire_frame() -> None:
    body = b"not really a custody proof"
    env = PayloadEnvelope.create(namespace="i2p-dht-control", role=PayloadRole.MUTABLE_HEAD, scope_id=digest("scope"), body=body, issued_at=20_000, ttl=300)
    payload = env.to_bytes()
    frame = frame_for_payload(2, WireMessageKind.CUSTODY_PROOF, payload)
    report = validate_payload_wall(frame, payload=payload, body=body, now=20_010)
    assert report.decision.kind is ValidatorWallDecisionKind.REJECT_ROLE_KIND
    assert not report.decision.accept


def test_validatorwall_rejects_body_digest_scope_namespace_and_flag_mismatches() -> None:
    body = b"store request body"
    env = PayloadEnvelope.create(namespace="i2p-dht-store", role=PayloadRole.STORE_REQUEST, scope_id=digest("scope"), body=body, issued_at=20_000, ttl=300)
    payload = env.to_bytes()
    frame = frame_for_payload(3, WireMessageKind.STORE_RECORD, payload)
    wrong_body = validate_payload_wall(frame, payload=payload, body=b"tampered", now=20_010)
    assert wrong_body.decision.kind is ValidatorWallDecisionKind.REJECT_BODY_DIGEST
    wrong_scope = validate_payload_wall(frame, payload=payload, body=body, now=20_010, expected_scope_id=digest("other-scope"))
    assert wrong_scope.decision.kind is ValidatorWallDecisionKind.REJECT_SCOPE

    bad_ns = PayloadEnvelope.create(namespace="foreign-app", role=PayloadRole.STORE_REQUEST, scope_id=digest("scope"), body=body, issued_at=20_000, ttl=300)
    bad_payload = bad_ns.to_bytes()
    bad_frame = frame_for_payload(3, WireMessageKind.STORE_RECORD, bad_payload)
    bad_ns_report = validate_payload_wall(bad_frame, payload=bad_payload, body=body, now=20_010)
    assert bad_ns_report.decision.kind is ValidatorWallDecisionKind.REJECT_NAMESPACE

    policy = ValidatorWallPolicy(required_flags_by_role={PayloadRole.STORE_REQUEST: frozenset({"store-contract"})})
    missing_flag = validate_payload_wall(frame, payload=payload, body=body, now=20_010, policy=policy)
    assert missing_flag.decision.kind is ValidatorWallDecisionKind.REJECT_REQUIRED_FLAG


def test_validatorwall_quarantines_same_request_conflicting_accepted_objects() -> None:
    body_a = b"body-a"
    body_b = b"body-b"
    env_a = PayloadEnvelope.create(namespace="i2p-dht-control", role=PayloadRole.MUTABLE_HEAD, scope_id=digest("scope"), body=body_a, issued_at=20_000, ttl=300)
    env_b = PayloadEnvelope.create(namespace="i2p-dht-control", role=PayloadRole.MUTABLE_HEAD, scope_id=digest("scope"), body=body_b, issued_at=20_000, ttl=300)
    frame_a = frame_for_payload(4, WireMessageKind.EPOCH_HEAD, env_a.to_bytes(), request_label="same-request")
    frame_b = frame_for_payload(5, WireMessageKind.EPOCH_HEAD, env_b.to_bytes(), request_label="same-request")
    report_a = validate_payload_wall(frame_a, payload=env_a.to_bytes(), body=body_a, now=20_010)
    report_b = validate_payload_wall(frame_b, payload=env_b.to_bytes(), body=body_b, now=20_010)
    window = analyze_validator_window((report_a, report_b))
    assert window.decision.kind is ValidatorWallDecisionKind.QUARANTINE_REQUEST_ID_CONFLICT
    assert len(window.conflicting_request_ids) == 1


# --- anti-entropy ---------------------------------------------------------


def test_antientropy_requests_newer_latest_only_with_family_diversity() -> None:
    local = LocalAntiEntropyState((item(SummaryItemKind.MUTABLE_HEAD, "v1", 1),))
    newer = item(SummaryItemKind.MUTABLE_HEAD, "v2", 2)
    plan = plan_anti_entropy(local, (summary(10, "fam-A", (newer,)), summary(11, "fam-B", (newer,))), now=10_050)
    assert plan.decision.kind is AntiEntropyDecisionKind.REQUEST_MISSING_LATEST
    assert plan.request_items == (newer,)

    monoculture = plan_anti_entropy(local, (summary(10, "fam-A", (newer,)), summary(12, "fam-A", (newer,))), now=10_050)
    assert monoculture.decision.kind is AntiEntropyDecisionKind.CONTINUE_NEED_FAMILY_DIVERSITY


def test_antientropy_prioritizes_newer_tombstone_over_convenient_latest() -> None:
    local = LocalAntiEntropyState((item(SummaryItemKind.MUTABLE_HEAD, "v2", 2),))
    tomb = item(SummaryItemKind.TOMBSTONE, "delete-v3", 3)
    plan = plan_anti_entropy(local, (summary(20, "fam-A", (tomb,)), summary(21, "fam-B", (tomb,))), now=10_050)
    assert plan.decision.kind is AntiEntropyDecisionKind.REQUEST_MISSING_TOMBSTONE
    assert plan.request_items == (tomb,)


def test_antientropy_quarantines_same_sequence_fork() -> None:
    local = LocalAntiEntropyState(())
    left = item(SummaryItemKind.MUTABLE_HEAD, "fork-left", 5)
    right = item(SummaryItemKind.MUTABLE_HEAD, "fork-right", 5)
    plan = plan_anti_entropy(local, (summary(30, "fam-A", (left,)), summary(31, "fam-B", (right,))), now=10_050)
    assert plan.decision.kind is AntiEntropyDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK
    assert plan.quarantined
    assert len(plan.fork_items) == 2


def test_antientropy_rejects_bad_signature_or_expired_summary() -> None:
    good_item = item(SummaryItemKind.PROVIDER_LEDGER, "providers", 1)
    expired = summary(40, "fam-A", (good_item,), issued_at=1_000, ttl=10)
    tampered = AntiEntropySummary(
        source_node_id=expired.source_node_id,
        source_family=expired.source_family,
        public_key=expired.public_key,
        issued_at=10_000,
        expires_at=10_300,
        items=expired.items,
        sequence=expired.sequence,
        signature=b"x" * 64,
    )
    plan = plan_anti_entropy(LocalAntiEntropyState(()), (expired, tampered), now=10_050)
    assert plan.decision.kind is AntiEntropyDecisionKind.REJECT_BAD_SIGNATURE_OR_TIME
    assert len(plan.invalid_summaries) == 2


def test_antientropy_quarantines_rollback_mesh_against_local_memory() -> None:
    local = LocalAntiEntropyState((item(SummaryItemKind.MUTABLE_HEAD, "local-v3-a", 3), item(SummaryItemKind.MUTABLE_HEAD, "local-v3-b", 3, scope="scope-B")))
    stale_a = item(SummaryItemKind.MUTABLE_HEAD, "old-v1-a", 1)
    stale_b = item(SummaryItemKind.MUTABLE_HEAD, "old-v1-b", 1, scope="scope-B")
    plan = plan_anti_entropy(local, (summary(50, "fam-A", (stale_a,)), summary(51, "fam-B", (stale_b,))), now=10_050, policy=AntiEntropyPolicy(rollback_mesh_threshold=2))
    assert plan.decision.kind is AntiEntropyDecisionKind.QUARANTINE_ROLLBACK_MESH


# --- surface index audit --------------------------------------------------


def test_surface_index_passes_for_current_revision_cube() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    revision = (root / "VERSION").read_text(encoding="utf-8").strip()
    report = audit_surface_index(root, revision=revision)
    assert report.status == "pass"
    assert any(path.endswith("204-rev0023-rangesketch-admissionwall-namespacefold.md") for path in report.indexed_paths)
