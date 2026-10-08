from i2p_dht_lab.identity import DhtKeypair
from i2p_dht_lab.mutable import StoreCode, make_mutable_torrent_head
from i2p_dht_lab.records import ImmutableRecord, ProviderRecord
from i2p_dht_lab.replication import ReplicationPolicy
from i2p_dht_lab.simnet import InMemoryNetwork


def test_inmemory_network_stores_and_finds_mutable_head():
    now = 1000
    network = InMemoryNetwork.deterministic(32, k=8)
    network.connect_all()
    keypair = DhtKeypair.from_seed(b"\x66" * 32)
    head = make_mutable_torrent_head(
        keypair=keypair,
        info_hash=bytes.fromhex("ab" * 20),
        seq=1,
        salt=b"feed:mutaplane-demo",
        now=now,
    )
    policy = ReplicationPolicy(k=8)
    stored_at = network.store_mutable(head, policy=policy, now=now)
    found, path = network.find_mutable(head.target_hex, now=now + 1)
    assert len(stored_at) == 8
    assert found is not None
    assert found.verify()
    assert found.target_hex == head.target_hex
    assert path


def test_inmemory_network_stores_immutable_and_provider_records():
    now = 2000
    network = InMemoryNetwork.deterministic(16, k=8)
    network.connect_all()
    policy = ReplicationPolicy(k=5)
    immutable = ImmutableRecord(namespace="demo", value={b"payload": b"hello"}, expires_at=now + 3600)
    assert len(network.store_immutable(immutable, policy=policy, now=now)) == 5

    provider_node = network.nodes[3]
    provider_keypair = DhtKeypair.from_seed((3 + 1).to_bytes(4, "big") * 8)
    provider = ProviderRecord(
        namespace="demo",
        content_key=immutable.target,
        provider_node_id=provider_node.identity.node_id,
        provider_public_key=provider_node.identity.public_key,
        sequence=1,
        expires_at=now + 3600,
        hints={"transport": "i2p-stream"},
    ).signed(provider_keypair)
    stored = network.store_provider(provider, policy=policy, now=now)
    assert len(stored) == 5
