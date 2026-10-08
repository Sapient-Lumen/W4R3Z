from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.records import ImmutableRecord, ProviderRecord, RecordBook


def test_immutable_record_target_is_content_addressed():
    rec1 = ImmutableRecord(namespace="demo", value={b"hello": b"world"})
    rec2 = ImmutableRecord(namespace="demo", value={b"hello": b"world"})
    rec3 = ImmutableRecord(namespace="demo", value={b"hello": b"other"})
    assert rec1.key_hex == rec2.key_hex
    assert rec1.key_hex != rec3.key_hex
    assert rec1.validate(now=1000).ok


def test_provider_record_signature_and_recordbook_replacement():
    now = 1000
    keypair = DhtKeypair.from_seed(b"\x44" * 32)
    identity = NodeIdentity.create(destination="provider-dest", keypair=keypair)
    content = ImmutableRecord(namespace="blob", value=b"payload")
    record = ProviderRecord(
        namespace="blob",
        content_key=content.target,
        provider_node_id=identity.node_id,
        provider_public_key=identity.public_key,
        sequence=1,
        expires_at=now + 3600,
        hints={"role": "seed"},
    ).signed(keypair)
    assert record.validate(now=now).ok

    book = RecordBook.empty()
    assert book.put_provider(record, now=now).ok
    assert len(book.get_providers(record.key_hex, now=now)) == 1

    newer = ProviderRecord(
        namespace="blob",
        content_key=content.target,
        provider_node_id=identity.node_id,
        provider_public_key=identity.public_key,
        sequence=2,
        expires_at=now + 3600,
        hints={"role": "seed", "v": "2"},
    ).signed(keypair)
    assert book.put_provider(newer, now=now + 1).ok
    providers = book.get_providers(record.key_hex, now=now + 1)
    assert len(providers) == 1
    assert providers[0].sequence == 2
