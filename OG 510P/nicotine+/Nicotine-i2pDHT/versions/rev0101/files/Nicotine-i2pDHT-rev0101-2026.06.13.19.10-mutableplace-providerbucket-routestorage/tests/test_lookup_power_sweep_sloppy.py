from i2p_dht_lab.adversary import BehaviorObservation, ResponseBehavior, readout
from i2p_dht_lab.ids import key_id
from i2p_dht_lab.lookup import LookupKind, LookupPolicy, LookupTrace, PathObservation, decide_lookup_acceptance, split_disjoint_paths
from i2p_dht_lab.mutable_family import MutableFamily, MutableSlotSpec
from i2p_dht_lab.power import PowerRole, default_profiles
from i2p_dht_lab.routing import Contact
from i2p_dht_lab.simnet import InMemoryNetwork
from i2p_dht_lab.sloppy import SloppyPolicy, plan_replica_placement
from i2p_dht_lab.sweep import AdvertKind, Advertisement, SweepPolicy, key_region, plan_reprovide_sweep, stale_advertisements


def test_disjoint_lookup_trace_keeps_path_queues_isolated():
    network = InMemoryNetwork.deterministic(32, k=8)
    contacts = [node.contact for node in network.nodes]
    target = key_id("lookup", b"target")
    policy = LookupPolicy(k=8, paths=4, alpha_per_path=2, quorum=6, min_honestish_paths=3)
    paths = split_disjoint_paths(contacts, target, policy=policy)
    assert len(paths) == 4
    assert all(path.queue for path in paths)

    trace = LookupTrace.start(contacts, target, policy=policy)
    first_round = trace.next_round()
    assert len(first_round) == policy.paths * policy.alpha_per_path
    assert len({query.path_index for query in first_round}) == policy.paths
    assert trace.round_index == 1


def test_lookup_decision_resists_provider_early_termination_and_poisoning():
    policy = LookupPolicy(k=20, paths=4, quorum=4, min_honestish_paths=3, allow_early_provider_stop=False)
    observations = [
        PathObservation(path_index=0, responders=frozenset({b"a"})),
        PathObservation(path_index=1, responders=frozenset({b"b"})),
        PathObservation(path_index=2, responders=frozenset({b"c"})),
        PathObservation(path_index=3, responders=frozenset({b"d"}), contradiction=True),
    ]
    decision = decide_lookup_acceptance(observations, policy=policy, kind=LookupKind.GET_PROVIDERS)
    assert not decision.accept
    assert decision.suspected_eclipse

    clean = [
        PathObservation(path_index=0, responders=frozenset({b"a", b"e"})),
        PathObservation(path_index=1, responders=frozenset({b"b", b"f"})),
        PathObservation(path_index=2, responders=frozenset({b"c"})),
        PathObservation(path_index=3, responders=frozenset({b"d"})),
    ]
    accepted = decide_lookup_acceptance(clean, policy=policy, kind=LookupKind.GET_MUTABLE)
    assert accepted.accept
    assert accepted.confidence == "high"


def test_reprovide_sweep_groups_by_region_and_spreads_due_times():
    now = 1000
    policy = SweepPolicy(interval_seconds=256, expiration_seconds=512, region_prefix_bits=4, max_batch_weight=10)
    adverts = [
        Advertisement(key=bytes([0x10]) + b"a" * 31, kind=AdvertKind.PROVIDER, namespace="demo", weight=2, last_published_at=0),
        Advertisement(key=bytes([0x1F]) + b"b" * 31, kind=AdvertKind.MUTABLE_HEAD, namespace="demo", weight=2, last_published_at=0),
        Advertisement(key=bytes([0xA0]) + b"c" * 31, kind=AdvertKind.PROVIDER, namespace="demo", weight=2, last_published_at=900),
    ]
    assert key_region(adverts[0].key, prefix_bits=4) == key_region(adverts[1].key, prefix_bits=4)
    stale = stale_advertisements(adverts, now=now, policy=policy)
    assert adverts[0] in stale and adverts[1] in stale and adverts[2] not in stale
    batches = plan_reprovide_sweep(stale, now=now, policy=policy)
    assert len(batches) == 1
    assert batches[0].due_at == now + 16
    assert len(batches[0].advertisements) == 2


def test_sloppy_replica_placement_adds_diverse_noncanonical_breadcrumbs():
    network = InMemoryNetwork.deterministic(40, k=8)
    target = key_id("sloppy", b"hot-key")
    contacts = []
    for idx, node in enumerate(network.nodes):
        contacts.append(Contact(
            node_id=node.contact.node_id,
            destination=node.contact.destination,
            public_key=node.contact.public_key,
            rtt_ms=50 + idx,
            work_bits=idx % 7,
        ))
    placement = plan_replica_placement(
        contacts,
        target,
        policy=SloppyPolicy(canonical_k=8, sloppy_budget=5, max_same_bucket_sloppy=2),
        lookup_path=contacts[8:20],
    )
    assert len(placement.canonical) == 8
    assert len(placement.sloppy) == 5
    assert set(c.node_id for c in placement.canonical).isdisjoint({c.node_id for c in placement.sloppy})


def test_power_profiles_are_capability_hints_not_authority():
    profiles = default_profiles()
    quiet = profiles["quiet_leaf"]
    power = profiles["power_archivist"]
    assert not quiet.can_be_bootstrap_hint()
    assert power.can_be_bootstrap_hint()
    assert power.can_store_sloppy()
    tags = power.capability_tags()
    assert "role:sentinel" in tags
    assert PowerRole.GATE in power.roles


def test_adversary_readout_flags_semantic_poisoning_and_empty_clusters():
    poisoned = readout([
        BehaviorObservation(0, ResponseBehavior.HONEST),
        BehaviorObservation(1, ResponseBehavior.FALSE_PROVIDER),
        BehaviorObservation(2, ResponseBehavior.HONEST),
    ])
    assert poisoned.suspected
    assert poisoned.reason == "semantic_poisoning_seen"

    empty_cluster = readout([
        BehaviorObservation(0, ResponseBehavior.EMPTY),
        BehaviorObservation(1, ResponseBehavior.EMPTY),
        BehaviorObservation(2, ResponseBehavior.HONEST),
    ], min_honest_paths=2)
    assert empty_cluster.suspected
    assert empty_cluster.reason == "empty_path_cluster"


def test_mutable_family_targets_are_namespace_and_family_separated():
    key = b"\x22" * 32
    single = MutableSlotSpec(MutableFamily.SINGLE_WRITER, key, salt=b"feed", namespace="alpha")
    delegated = MutableSlotSpec(MutableFamily.DELEGATED, key, salt=b"feed", namespace="alpha")
    other_namespace = MutableSlotSpec(MutableFamily.SINGLE_WRITER, key, salt=b"feed", namespace="beta")
    assert single.target != delegated.target
    assert single.target != other_namespace.target
    assert single.validator_name == "mutable.single_writer.v1"
