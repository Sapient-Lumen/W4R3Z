from __future__ import annotations

from i2p_dht_lab.garden import GardenServiceKind
from i2p_dht_lab.garden_churn import ChurnBehavior, ChurnGarden, ChurnLookupEngine, GardenRefusalBook, GardenRefusalReason, GardenRefusalReceipt
from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.ids import sha256
from i2p_dht_lab.mutable import MutableRecord
from i2p_dht_lab.provider_poison import ProviderPoisonBook, ProviderProbeOutcome, ProviderProbeReceipt, ProviderRecordAssessmentKind
from i2p_dht_lab.records import ProviderRecord


def kp(n: int) -> DhtKeypair:
    return DhtKeypair.from_seed(bytes([n]) * 32)


def node(n: int, prefix: str) -> NodeIdentity:
    return NodeIdentity.create(destination=f"{prefix}-{n}.b32.i2p", keypair=kp(n))


def provider_record(n: int, *, content_key: bytes, now: int) -> ProviderRecord:
    ident = node(n, "provider")
    return ProviderRecord(
        namespace="rev0011.providerbook",
        content_key=content_key,
        provider_node_id=ident.node_id,
        provider_public_key=kp(n).public_key_bytes,
        sequence=n,
        expires_at=now + 10_000,
        hints={"transport": "i2p-stream"},
    ).signed(kp(n))


def probe(record: ProviderRecord, *, witness: int, outcome: ProviderProbeOutcome, now: int, retry_after: int = 0, received_digest: bytes | None = None) -> ProviderProbeReceipt:
    expected = sha256(b"expected-block")
    if received_digest is None:
        received_digest = expected if outcome is ProviderProbeOutcome.CONTENT_MATCH else (sha256(b"wrong-block") if outcome is ProviderProbeOutcome.CONTENT_MISMATCH else b"")
    return ProviderProbeReceipt.create(
        witness_keypair=kp(witness),
        witness_node_id=node(witness, "witness").node_id,
        provider_node_id=record.provider_node_id,
        namespace=record.namespace,
        content_key=record.content_key,
        outcome=outcome,
        issued_at=now,
        expected_digest=expected,
        received_digest=received_digest,
        retry_after=retry_after,
    )


def mutable_head(n: int, *, seq: int, salt: bytes, now: int) -> MutableRecord:
    return MutableRecord.create(keypair=kp(n), seq=seq, salt=salt, value={b"seq": seq}, now=now, ttl=3600)


def test_provider_poison_book_quarantines_wrong_content_and_honors_useful_backoff() -> None:
    now = 50_000
    key = sha256(b"provider-book-key")
    honest = provider_record(1, content_key=key, now=now)
    liar = provider_record(2, content_key=key, now=now)
    busy = provider_record(3, content_key=key, now=now)
    book = ProviderPoisonBook()

    assert book.observe_probe(probe(honest, witness=91, outcome=ProviderProbeOutcome.CONTENT_MATCH, now=now + 1), now=now + 2).severe is False
    assert book.observe_probe(probe(liar, witness=92, outcome=ProviderProbeOutcome.CONTENT_MISMATCH, now=now + 1), now=now + 2).severe is True
    assert book.observe_probe(probe(busy, witness=93, outcome=ProviderProbeOutcome.USEFUL_REFUSAL, now=now + 1, retry_after=now + 600), now=now + 2).severe is False

    selected_during_backoff = book.select_provider_records((honest, liar, busy), now=now + 3, max_count=8)
    selected_after_backoff = book.select_provider_records((honest, liar, busy), now=now + 601, max_count=8)

    assert liar.provider_node_id not in {record.provider_node_id for record in selected_after_backoff}
    assert busy.provider_node_id not in {record.provider_node_id for record in selected_during_backoff}
    assert busy.provider_node_id in {record.provider_node_id for record in selected_after_backoff}
    assert book.admit_record(liar, now=now + 602).kind is ProviderRecordAssessmentKind.VALID_QUARANTINED


def test_provider_poison_book_rotates_provider_families_after_semantic_evidence() -> None:
    now = 60_000
    key = sha256(b"provider-book-family-key")
    records = tuple(provider_record(n, content_key=key, now=now) for n in range(4, 9))
    book = ProviderPoisonBook()
    for index, record in enumerate(records):
        book.observe_probe(probe(record, witness=100 + index, outcome=ProviderProbeOutcome.CONTENT_MATCH, now=now + 1), now=now + 2)

    selected = book.select_provider_records(
        records,
        now=now + 3,
        max_count=4,
        family_by_node={record.provider_node_id: ("same-family" if index < 3 else f"family-{index}") for index, record in enumerate(records)},
        max_per_family=1,
    )

    assert len(selected) == 3
    assert sum(1 for record in selected if record.provider_node_id in {records[0].provider_node_id, records[1].provider_node_id, records[2].provider_node_id}) == 1


def test_garden_churn_keeps_useful_refusal_separate_from_stale_and_latest_answers() -> None:
    now = 70_000
    latest = mutable_head(31, seq=5, salt=b"rev0011-garden-churn", now=now + 4)
    stale = mutable_head(31, seq=2, salt=b"rev0011-garden-churn", now=now)
    refusing_identity = node(40, "garden")
    engine = ChurnLookupEngine((
        ChurnGarden(node(41, "garden").node_id, "captured", GardenServiceKind.MUTABLE_STEWARD, kp(41), (ChurnBehavior.AVAILABLE_STALE,), stale_record=stale),
        ChurnGarden(node(42, "garden").node_id, "honest", GardenServiceKind.MUTABLE_STEWARD, kp(42), (ChurnBehavior.AVAILABLE_LATEST,), latest_record=latest),
        ChurnGarden(refusing_identity.node_id, "busy", GardenServiceKind.MUTABLE_STEWARD, kp(40), (ChurnBehavior.REFUSES_USEFULLY,), latest_record=latest),
    ))

    report = engine.run(target=latest.target_i2p256, now=now + 10, rounds=2, fanout=3, max_per_family=1)

    assert report.freshest_seq == 5
    assert report.useful_refusal_count == 1
    assert report.latest_families == frozenset({"honest"})
    assert report.needs_more_rounds(min_valid_families=2)


def test_garden_refusal_book_accepts_bounded_receipts_and_rejects_expired_ones() -> None:
    now = 80_000
    ident = node(50, "garden")
    receipt = GardenRefusalReceipt.create(
        garden_keypair=kp(50),
        garden_node_id=ident.node_id,
        service=GardenServiceKind.REGION_GARDENER,
        reason=GardenRefusalReason.BUDGET_EXHAUSTED,
        target=sha256(b"garden-refusal-book"),
        issued_at=now,
        retry_after=now + 300,
        ttl=600,
    )
    book = GardenRefusalBook()

    accepted = book.observe(receipt, now=now + 1)
    expired = book.observe(receipt, now=now + 601)

    assert accepted.backoff_until == now + 300
    assert book.active_backoff(ident.node_id, GardenServiceKind.REGION_GARDENER, now=now + 299)
    assert not book.active_backoff(ident.node_id, GardenServiceKind.REGION_GARDENER, now=now + 301)
    assert expired.kind.value == "invalid_refusal"
