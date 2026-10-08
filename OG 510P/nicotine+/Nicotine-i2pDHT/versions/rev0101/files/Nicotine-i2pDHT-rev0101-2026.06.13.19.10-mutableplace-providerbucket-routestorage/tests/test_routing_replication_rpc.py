from dataclasses import replace

from i2p_dht_lab.identity import DhtKeypair, NodeIdentity
from i2p_dht_lab.replication import ReplicationPolicy, select_replicas
from i2p_dht_lab.routing import Contact, RoutingTable
from i2p_dht_lab.rpc import make_find_node_request


def make_contact(index: int) -> Contact:
    keypair = DhtKeypair.from_seed(index.to_bytes(4, "big") * 8)
    identity = NodeIdentity.create(destination=f"dest-{index}", keypair=keypair)
    return Contact(node_id=identity.node_id, destination=identity.destination, public_key=identity.public_key, last_seen=index)


def test_routing_table_nearest_orders_by_xor_distance():
    local = make_contact(100)
    table = RoutingTable(local.node_id, k=20)
    contacts = [make_contact(i) for i in range(20)]
    for contact in contacts:
        table.insert(contact)
    target = make_contact(200).node_id
    nearest = table.nearest(target, count=5)
    distances = [int.from_bytes(c.node_id, "big") ^ int.from_bytes(target, "big") for c in nearest]
    assert distances == sorted(distances)
    assert len(nearest) == 5


def test_replacement_cache_promotes_after_failures():
    local = make_contact(300)
    table = RoutingTable(local.node_id, k=1, replacement_cache_size=2)
    first = make_contact(1)
    second = make_contact(2)
    # Force same bucket by using raw contacts with explicit node ids near each other.
    first = replace(first, node_id=bytes.fromhex("80" + "00" * 31))
    second = replace(second, node_id=bytes.fromhex("80" + "00" * 30 + "01"))
    table = RoutingTable(bytes.fromhex("00" * 32), k=1, replacement_cache_size=2)
    assert table.insert(first) == "inserted"
    assert table.insert(second) == "queued_replacement"
    removed = table.mark_failed(first.node_id, max_failures=1)
    assert removed == first
    assert table.nearest(second.node_id, count=1)[0].node_id == second.node_id


def test_replica_selection_uses_xor_nearest():
    contacts = [make_contact(i) for i in range(1, 10)]
    target = make_contact(99).node_id
    policy = ReplicationPolicy(k=4)
    selected = select_replicas(contacts, target, policy=policy)
    assert len(selected) == 4
    assert selected == sorted(contacts, key=lambda c: int.from_bytes(c.node_id, "big") ^ int.from_bytes(target, "big"))[:4]


def test_signed_rpc_envelope_verifies_and_tamper_fails():
    keypair = DhtKeypair.from_seed(b"\x55" * 32)
    identity = NodeIdentity.create(destination="rpc-dest", keypair=keypair)
    req = make_find_node_request(sender_node_id=identity.node_id, sender_keypair=keypair, target=b"\x99" * 32, message_id="m1", now=1000)
    assert req.verify()
    tampered = replace(req, body={"target": (b"\x98" * 32).hex()})
    assert not tampered.verify()
