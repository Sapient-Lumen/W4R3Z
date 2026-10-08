from i2p_dht_lab.capability import (
    CapabilityGrant,
    CapabilityKind,
    CapabilityRevocation,
    CapabilityVerdictKind,
    RevocationSet,
    validate_capability_chain,
)
from i2p_dht_lab.chaos import FakeHeadResponder, HeadResponderMode, risky_lookup_needs_more_paths, run_head_lookup_scenario
from i2p_dht_lab.headlog import (
    HeadVerdictKind,
    LocalHeadMemory,
    VersionedHeadValue,
    WitnessClaimKind,
    WitnessReceipt,
    head_record_digest,
    make_versioned_head_record,
    summarize_receipts,
)
from i2p_dht_lab.identity import DhtKeypair


def _kp(byte: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([byte]) * 32)


def test_versioned_head_requires_prev_for_clean_advance():
    now = 1_765_000_000
    publisher = _kp(11)
    memory = LocalHeadMemory()
    source_a = b"a" * 32
    source_b = b"b" * 32
    head1 = make_versioned_head_record(
        keypair=publisher,
        kind="release_channel",
        pointer=b"manifest-v1".ljust(32, b"\0"),
        seq=1,
        salt=b"project:demo",
        prev=b"",
        now=now,
    )
    verdict1 = memory.observe(head1, source_node_id=source_a, observed_at=now, require_prev=False)
    assert verdict1.kind is HeadVerdictKind.ACCEPT_FIRST

    head2 = make_versioned_head_record(
        keypair=publisher,
        kind="release_channel",
        pointer=b"manifest-v2".ljust(32, b"\0"),
        seq=2,
        salt=b"project:demo",
        prev=head_record_digest(head1),
        now=now + 1,
    )
    verdict2 = memory.observe(head2, source_node_id=source_b, observed_at=now + 1, require_prev=True)
    assert verdict2.kind is HeadVerdictKind.ACCEPT_ADVANCE
    assert memory.state_for(head1.target_hex).max_seq == 2


def test_prev_mismatch_and_missing_prev_are_flagged_before_latest_belief_changes():
    now = 1_765_000_000
    publisher = _kp(12)
    memory = LocalHeadMemory()
    source = b"s" * 32
    head1 = make_versioned_head_record(
        keypair=publisher,
        kind="seed_head",
        pointer=b"seed-v1".ljust(32, b"\0"),
        seq=1,
        salt=b"seeds:default",
        now=now,
    )
    assert memory.observe(head1, source_node_id=source, observed_at=now).accepted

    missing_prev = make_versioned_head_record(
        keypair=publisher,
        kind="seed_head",
        pointer=b"seed-v2".ljust(32, b"\0"),
        seq=2,
        salt=b"seeds:default",
        prev=b"",
        now=now + 1,
    )
    verdict_missing = memory.observe(missing_prev, source_node_id=b"m" * 32, observed_at=now + 1, require_prev=True)
    assert verdict_missing.kind is HeadVerdictKind.SUSPICIOUS_MISSING_PREV
    assert not verdict_missing.accepted
    assert memory.state_for(head1.target_hex).max_seq == 1

    wrong_prev = make_versioned_head_record(
        keypair=publisher,
        kind="seed_head",
        pointer=b"seed-v3".ljust(32, b"\0"),
        seq=3,
        salt=b"seeds:default",
        prev=b"x" * 32,
        now=now + 2,
    )
    verdict_wrong = memory.observe(wrong_prev, source_node_id=b"w" * 32, observed_at=now + 2, require_prev=True)
    assert verdict_wrong.kind is HeadVerdictKind.REJECT_PREV_MISMATCH
    assert memory.state_for(head1.target_hex).max_seq == 1


def test_rollback_and_same_sequence_fork_generate_signed_witness_receipts():
    now = 1_765_000_000
    publisher = _kp(13)
    witness = _kp(99)
    memory = LocalHeadMemory()
    head1 = make_versioned_head_record(keypair=publisher, kind="policy_head", pointer=b"p1".ljust(32, b"\0"), seq=1, salt=b"policy:default", now=now)
    head2 = make_versioned_head_record(keypair=publisher, kind="policy_head", pointer=b"p2".ljust(32, b"\0"), seq=2, salt=b"policy:default", prev=head_record_digest(head1), now=now + 1)
    fork2 = make_versioned_head_record(keypair=publisher, kind="policy_head", pointer=b"evil".ljust(32, b"\0"), seq=2, salt=b"policy:default", prev=head_record_digest(head1), now=now + 1)
    assert memory.observe(head1, source_node_id=b"1" * 32, observed_at=now).accepted
    assert memory.observe(head2, source_node_id=b"2" * 32, observed_at=now + 1, require_prev=True).accepted

    rollback = memory.observe(head1, source_node_id=b"r" * 32, observed_at=now + 2, require_prev=True)
    assert rollback.kind is HeadVerdictKind.REJECT_ROLLBACK
    receipt1 = WitnessReceipt.create(witness_keypair=witness, verdict=rollback, known_state=memory.state_for(head1.target_hex), issued_at=now + 2)
    assert receipt1.verify()
    assert receipt1.claim is WitnessClaimKind.OBSERVED_ROLLBACK

    fork = memory.observe(fork2, source_node_id=b"f" * 32, observed_at=now + 3, require_prev=True)
    assert fork.kind is HeadVerdictKind.FORK_SAME_SEQUENCE
    receipt2 = WitnessReceipt.create(witness_keypair=witness, verdict=fork, known_state=memory.state_for(head1.target_hex), issued_at=now + 3)
    summary = summarize_receipts((receipt1, receipt2))
    assert summary[WitnessClaimKind.OBSERVED_ROLLBACK.value] == 1
    assert summary[WitnessClaimKind.OBSERVED_FORK.value] == 1


def test_versioned_head_value_roundtrips_from_mutable_record():
    now = 1_765_000_000
    publisher = _kp(14)
    rec = make_versioned_head_record(keypair=publisher, kind="mutable_torrent", pointer=b"\x44" * 20, seq=4, salt=b"torrent:demo", prev=b"\x33" * 32, manifest_digest=b"\x55" * 32, note="demo", now=now)
    parsed = VersionedHeadValue.from_record(rec)
    assert parsed.kind == "mutable_torrent"
    assert parsed.pointer == b"\x44" * 20
    assert parsed.prev == b"\x33" * 32
    assert parsed.manifest_digest == b"\x55" * 32


def test_capability_chain_validates_scope_narrowing_and_actor():
    now = 1_765_000_000
    root = _kp(21)
    garden = _kp(22)
    leaf = _kp(23)
    grant1 = CapabilityGrant.create(
        issuer_keypair=root,
        subject_public_key=garden.public_key_bytes,
        capability=CapabilityKind.GARDEN_WATCH,
        resource=b"heads/project-alpha",
        not_before=now,
        ttl=3600,
        sequence=1,
    )
    grant2 = CapabilityGrant.create(
        issuer_keypair=garden,
        subject_public_key=leaf.public_key_bytes,
        capability=CapabilityKind.GARDEN_WATCH,
        resource=b"heads/project-alpha/release",
        not_before=now,
        ttl=1200,
        sequence=1,
        parent_grant_hash=grant1.grant_hash,
    )
    check = validate_capability_chain(
        (grant1, grant2),
        authority_public_key=root.public_key_bytes,
        actor_public_key=leaf.public_key_bytes,
        capability=CapabilityKind.GARDEN_WATCH,
        resource=b"heads/project-alpha/release/channel",
        now=now + 10,
    )
    assert check.valid
    assert check.final_subject == leaf.public_key_bytes

    too_broad = validate_capability_chain(
        (grant1, grant2),
        authority_public_key=root.public_key_bytes,
        actor_public_key=leaf.public_key_bytes,
        capability=CapabilityKind.GARDEN_WATCH,
        resource=b"heads/project-beta",
        now=now + 10,
    )
    assert too_broad.kind is CapabilityVerdictKind.RESOURCE_TOO_BROAD


def test_capability_revocation_head_invalidates_otherwise_valid_chain():
    now = 1_765_000_000
    root = _kp(31)
    helper = _kp(32)
    grant = CapabilityGrant.create(
        issuer_keypair=root,
        subject_public_key=helper.public_key_bytes,
        capability=CapabilityKind.PUBLISH_SEED,
        resource=b"seed/default",
        not_before=now,
        ttl=3600,
        sequence=1,
    )
    assert validate_capability_chain((grant,), authority_public_key=root.public_key_bytes, actor_public_key=helper.public_key_bytes, capability=CapabilityKind.PUBLISH_SEED, resource=b"seed/default", now=now + 1).valid
    revocation = CapabilityRevocation.create(issuer_keypair=root, grant_hash=grant.grant_hash, issued_at=now + 2, reason="demo compromise")
    revocations = RevocationSet((revocation,))
    head = revocations.make_head(root, seq=1, salt=b"cap-revoke:default", now=now + 2)
    assert head.verify()
    denied = validate_capability_chain((grant,), authority_public_key=root.public_key_bytes, actor_public_key=helper.public_key_bytes, capability=CapabilityKind.PUBLISH_SEED, resource=b"seed/default", now=now + 3, revocations=revocations)
    assert denied.kind is CapabilityVerdictKind.REVOKED


def test_fake_head_lookup_chaos_keeps_asking_on_forks_and_rollback():
    now = 1_765_000_000
    publisher = _kp(41)
    witness = _kp(42)
    stale = make_versioned_head_record(keypair=publisher, kind="release", pointer=b"old".ljust(32, b"\0"), seq=1, salt=b"release:demo", now=now)
    latest = make_versioned_head_record(keypair=publisher, kind="release", pointer=b"new".ljust(32, b"\0"), seq=2, salt=b"release:demo", prev=head_record_digest(stale), now=now + 1)
    fork = make_versioned_head_record(keypair=publisher, kind="release", pointer=b"fork".ljust(32, b"\0"), seq=2, salt=b"release:demo", prev=head_record_digest(stale), now=now + 1)
    memory = LocalHeadMemory()
    # Prime local memory with latest; the stale responder below is now a rollback attempt.
    assert memory.observe(latest, source_node_id=b"h" * 32, observed_at=now + 1).accepted
    transcript = run_head_lookup_scenario(
        latest=latest,
        stale=stale,
        fork=fork,
        responders=(
            FakeHeadResponder(b"s" * 32, HeadResponderMode.STALE, path_index=0, latency_ms=10),
            FakeHeadResponder(b"f" * 32, HeadResponderMode.FORK, path_index=1, latency_ms=20),
            FakeHeadResponder(b"l" * 32, HeadResponderMode.HONEST_LATEST, path_index=2, latency_ms=30),
            FakeHeadResponder(b"e" * 32, HeadResponderMode.EMPTY, path_index=3, latency_ms=5),
        ),
        memory=memory,
        witness_keypair=witness,
        now=now + 2,
        require_prev=True,
    )
    assert transcript.accepted_seq == 2
    assert transcript.saw_rollback
    assert transcript.saw_fork
    assert risky_lookup_needs_more_paths(transcript)
    assert len(transcript.witness_receipts) == 2
    assert all(receipt.verify() for receipt in transcript.witness_receipts)
