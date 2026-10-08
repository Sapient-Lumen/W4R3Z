"""Deterministic in-memory DHT simulation for the datacube."""
from __future__ import annotations

from dataclasses import dataclass, field

from .identity import DhtKeypair, NodeIdentity
from .mutable import MutableRecord, MutableSlotStore
from .records import ImmutableRecord, ProviderRecord, RecordBook
from .replication import ReplicationPolicy, select_replicas
from .routing import Contact, RoutingTable


def synthetic_destination(index: int) -> str:
    return f"substrate-node-{index:04d}.example.i2p-destination"


def seed_for_index(index: int) -> bytes:
    return index.to_bytes(4, "big") * 8


@dataclass
class InMemoryNode:
    identity: NodeIdentity
    k: int = 8
    records: RecordBook = field(default_factory=RecordBook.empty)
    mutable_slots: MutableSlotStore = field(default_factory=MutableSlotStore.empty)

    def __post_init__(self) -> None:
        self.contact = Contact(
            node_id=self.identity.node_id,
            destination=self.identity.destination,
            public_key=self.identity.public_key,
            capabilities=("stream", "mutable", "provider"),
            work_bits=self.identity.admission_work_bits,
        )
        self.routing = RoutingTable(self.identity.node_id, k=self.k)

    def learn(self, contact: Contact) -> str:
        return self.routing.insert(contact)

    def query_nearest(self, target: bytes, *, count: int) -> list[Contact]:
        return self.routing.nearest(target, count=count)

    def put_mutable_local(self, record: MutableRecord, *, now: int):
        return self.mutable_slots.put(record, now=now)

    def get_mutable_local(self, target_hex: str, *, now: int):
        return self.mutable_slots.get(target_hex, now=now)


@dataclass
class InMemoryNetwork:
    nodes: list[InMemoryNode]

    @classmethod
    def deterministic(cls, count: int, *, k: int = 8, min_work_bits: int = 0) -> "InMemoryNetwork":
        nodes: list[InMemoryNode] = []
        for index in range(count):
            keypair = DhtKeypair.from_seed(seed_for_index(index + 1))
            identity = NodeIdentity.create(destination=synthetic_destination(index), keypair=keypair, min_work_bits=min_work_bits)
            nodes.append(InMemoryNode(identity=identity, k=k))
        return cls(nodes)

    def node_by_id(self, node_id: bytes) -> InMemoryNode | None:
        for node in self.nodes:
            if node.identity.node_id == node_id:
                return node
        return None

    def connect_all(self) -> None:
        contacts = [node.contact for node in self.nodes]
        for node in self.nodes:
            for contact in contacts:
                node.learn(contact)

    def closest_nodes(self, target: bytes, *, count: int) -> list[InMemoryNode]:
        contacts = select_replicas([node.contact for node in self.nodes], target, policy=ReplicationPolicy(k=count))
        by_id = {node.identity.node_id: node for node in self.nodes}
        return [by_id[contact.node_id] for contact in contacts]

    def store_mutable(self, record: MutableRecord, *, policy: ReplicationPolicy, now: int) -> list[str]:
        stored_at: list[str] = []
        for node in self.closest_nodes(record.target_i2p256, count=policy.k):
            decision = node.put_mutable_local(record, now=now)
            if decision.accepted:
                stored_at.append(node.identity.node_id.hex())
        return stored_at

    def find_mutable(self, target_hex: str, *, now: int) -> tuple[MutableRecord | None, list[str]]:
        target = bytes.fromhex(target_hex)
        path: list[str] = []
        for node in self.closest_nodes(target, count=len(self.nodes)):
            path.append(node.identity.node_id.hex())
            record = node.get_mutable_local(target_hex, now=now)
            if record is not None:
                return record, path
        return None, path

    def store_immutable(self, record: ImmutableRecord, *, policy: ReplicationPolicy, now: int) -> list[str]:
        stored_at: list[str] = []
        for node in self.closest_nodes(record.target, count=policy.k):
            result = node.records.put_immutable(record, now=now)
            if result.ok:
                stored_at.append(node.identity.node_id.hex())
        return stored_at

    def store_provider(self, record: ProviderRecord, *, policy: ReplicationPolicy, now: int) -> list[str]:
        stored_at: list[str] = []
        for node in self.closest_nodes(record.target, count=policy.k):
            result = node.records.put_provider(record, now=now)
            if result.ok:
                stored_at.append(node.identity.node_id.hex())
        return stored_at
