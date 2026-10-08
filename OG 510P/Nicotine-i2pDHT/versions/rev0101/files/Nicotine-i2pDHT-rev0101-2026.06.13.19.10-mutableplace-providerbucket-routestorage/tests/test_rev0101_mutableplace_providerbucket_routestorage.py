from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.mutableplacement import (
    MutablePlacementCapsule,
    MutablePlacementDecisionKind,
    assess_mutable_placement,
)
from i2p_dht_lab.providerbucket import (
    ProviderBucketCapsule,
    ProviderBucketDecisionKind,
    assess_provider_bucket,
)
from i2p_dht_lab.providersemantics import ProviderSemanticsCapsule, assess_provider_semantics
from i2p_dht_lab.recordingress import RecordIngressCapsule, assess_record_ingress
from i2p_dht_lab.routestorage import (
    RouteStorageCapsule,
    RouteStorageDecisionKind,
    assess_route_storage,
)
from i2p_dht_lab.routinganchor import RoutingAnchorCapsule, assess_routing_anchor
from i2p_dht_lab.substrateplacementfold import audit_substrate_placement_fold
from i2p_dht_lab.substratespine import audit_substrate_spine

ROOT = Path(__file__).resolve().parents[1]
SUBSTRATE = sha256(b"rev0101-substrate-reentry")
ORACLE = sha256(b"rev0101-record-oracle")
PARSE = sha256(b"rev0101-parse")
VALIDATOR = sha256(b"rev0101-validator")
ADMISSION = sha256(b"rev0101-admission")
WITNESS = sha256(b"rev0101-witness")
MUTABLE_HEAD = sha256(b"rev0101-mutable-head")
PUBLISHER = sha256(b"rev0101-publisher")
SALT = sha256(b"rev0101-salt")
TARGET = sha256(b"rev0101-target")
PROOF = sha256(b"rev0101-proof")
BUDGET = sha256(b"rev0101-budget")
CLAIM = sha256(b"rev0101-claim")
REGION = sha256(b"rev0101-region")
CONTENT = sha256(b"rev0101-content-key")
DEST = sha256(b"rev0101-destination")
ENTRY = sha256(b"rev0101-index-entry")
LEASE = sha256(b"rev0101-lease")
ATTEST = sha256(b"rev0101-attestation")
NODE = sha256(b"rev0101-node")
BUCKET_REGION = sha256(b"rev0101-bucket-region")
STALE = sha256(b"rev0101-stale-contact")


@dataclass(frozen=True)
class FakeSubstrateReentry:
    accepted: bool = True
    substrate_reentered: bool = True
    native_permission_leak: bool = False
    report_digest: bytes = SUBSTRATE


@dataclass(frozen=True)
class FakeRecordPlaneOracle:
    accepted: bool = True
    python_record_truth: bool = True
    native_record_permission: bool = False
    report_digest: bytes = ORACLE


@dataclass(frozen=True)
class FakeComponent:
    accepted: bool = True
    report_digest: bytes = b""


def _ingress_capsule(kind="mutable", namespace="dht.mutable", key="mutable-key", payload=None, **kw):
    data = dict(
        component="record-ingress",
        profile="generic-i2p-dht",
        namespace=namespace,
        record_kind=kind,
        record_key=key,
        request_id="rev0101-record-ingress",
        sequence=1,
        previous_digest=b"",
        substrate_reentry_digest=SUBSTRATE,
        record_plane_oracle_digest=ORACLE,
        parse_report_digest=PARSE,
        validator_report_digest=VALIDATOR,
        admission_report_digest=ADMISSION,
        payload_digest=payload or sha256(b"rev0101-payload"),
        value_size=512,
        max_value_size=4096,
        ttl_seconds=1800,
        max_ttl_seconds=3600,
        canonical_wire=True,
        untrusted_bytes_parsed_by_python=True,
        python_validator_accepted=True,
        admission_accepted=True,
        native_validation_attempted=False,
        native_parser_attempted=False,
        signature_checked_by_python=True,
        preserve_record_plane_oracle_memory=True,
        preserve_substrate_reentry_memory=True,
        preserve_mutable_head_memory=True,
        preserve_provider_false_memory=True,
        preserve_tombstone_memory=True,
        preserve_witness_memory=True,
        preserve_garden_refusal_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return RecordIngressCapsule(**data)


def _ingress(capsule=None):
    return assess_record_ingress(
        FakeSubstrateReentry(),
        FakeRecordPlaneOracle(),
        FakeComponent(report_digest=PARSE),
        FakeComponent(report_digest=VALIDATOR),
        FakeComponent(report_digest=ADMISSION),
        capsule or _ingress_capsule(),
        observed_families=("family-a", "family-b"),
        observed_path_families=("path-a", "path-b"),
    )


def _mutable_capsule(ingress_report=None, **kw):
    ingress_report = ingress_report or _ingress()
    data = dict(
        component="mutable-placement",
        profile="generic-i2p-dht",
        mutable_key="mutable-key",
        namespace="dht.mutable",
        request_id="rev0101-mutable-placement",
        sequence=1,
        previous_digest=b"",
        record_ingress_digest=ingress_report.report_digest,
        mutable_head_digest=MUTABLE_HEAD,
        validator_report_digest=VALIDATOR,
        witness_digest=WITNESS,
        publisher_key_digest=PUBLISHER,
        salt_digest=SALT,
        computed_target_digest=TARGET,
        expected_target_digest=TARGET,
        record_sequence=11,
        highest_seen_sequence=10,
        previous_head_digest=sha256(b"prev-head"),
        expected_previous_head_digest=sha256(b"prev-head"),
        signature_valid=True,
        cas_ok=True,
        value_digest_matches=True,
        epoch_window_valid=True,
        same_sequence_fork_seen=False,
        rollback_seen=False,
        live_tombstone_seen=False,
        missing_previous_link=False,
        native_mutable_truth_attempted=False,
        preserve_head_memory=True,
        preserve_fork_memory=True,
        preserve_tombstone_memory=True,
        preserve_witness_memory=True,
        preserve_rollback_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return MutablePlacementCapsule(**data)


def _mutable(capsule=None, ingress_report=None):
    ingress_report = ingress_report or _ingress()
    return assess_mutable_placement(
        ingress_report,
        FakeComponent(report_digest=VALIDATOR),
        FakeComponent(report_digest=WITNESS),
        capsule or _mutable_capsule(ingress_report),
        observed_families=("family-a", "family-b"),
        observed_path_families=("path-a", "path-b"),
    )


def _provider_ingress():
    return _ingress(_ingress_capsule(kind="provider", namespace="dht.providers", key="provider-key"))


def _provider_semantics_capsule(ingress_report=None, **kw):
    ingress_report = ingress_report or _provider_ingress()
    data = dict(
        component="provider-semantics",
        profile="generic-i2p-dht",
        namespace="dht.providers",
        content_key_digest=CONTENT,
        provider_destination_digest=DEST,
        request_id="rev0101-provider-semantics",
        sequence=1,
        previous_digest=b"",
        record_ingress_digest=ingress_report.report_digest,
        provider_claim_digest=CLAIM,
        proof_challenge_digest=PROOF,
        metadata_budget_digest=BUDGET,
        witness_digest=WITNESS,
        proof_result="true",
        challenge_bound=True,
        digest_matches=True,
        signed_provider_claim=True,
        semantic_confirmation_required=True,
        metadata_budget_accepted=True,
        decoy_budget_accepted=True,
        raw_content_key_exposed=False,
        witness_preserved=True,
        preserve_provider_false_memory=True,
        preserve_witness_memory=True,
        preserve_metadata_budget_memory=True,
        preserve_tombstone_memory=True,
        family_id="family-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return ProviderSemanticsCapsule(**data)


def _provider_semantics(capsule=None, ingress_report=None):
    ingress_report = ingress_report or _provider_ingress()
    return assess_provider_semantics(
        ingress_report,
        FakeComponent(report_digest=PROOF),
        FakeComponent(report_digest=BUDGET),
        FakeComponent(report_digest=WITNESS),
        capsule or _provider_semantics_capsule(ingress_report),
        observed_families=("family-a", "family-b"),
        observed_path_families=("path-a", "path-b"),
    )


def _provider_bucket_capsule(provider_report=None, **kw):
    provider_report = provider_report or _provider_semantics()
    data = dict(
        component="provider-bucket",
        profile="generic-i2p-dht",
        bucket_id="region-42",
        purpose="provider_index",
        request_id="rev0101-provider-bucket",
        sequence=1,
        previous_digest=b"",
        provider_semantics_digest=provider_report.report_digest,
        region_digest=REGION,
        content_key_digest=CONTENT,
        provider_destination_digest=DEST,
        index_entry_digest=ENTRY,
        ttl_seconds=1200,
        max_ttl_seconds=3600,
        now=1000,
        expires_at=2200,
        current_bucket_count=3,
        bucket_capacity=10,
        semantic_result="true",
        useful_refusal_seen=False,
        false_provider_seen=False,
        live_tombstone_seen=False,
        content_payload_stored=False,
        provider_claim_only=True,
        preserve_provider_false_memory=True,
        preserve_tombstone_memory=True,
        preserve_metadata_budget_memory=True,
        preserve_region_ledger_memory=True,
        source_family_id="source-a",
        provider_family_id="provider-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return ProviderBucketCapsule(**data)


def _provider_bucket(capsule=None, provider_report=None):
    provider_report = provider_report or _provider_semantics()
    return assess_provider_bucket(
        provider_report,
        capsule or _provider_bucket_capsule(provider_report),
        observed_source_families=("source-a", "source-b"),
        observed_provider_families=("provider-a", "provider-b"),
        observed_path_families=("path-a", "path-b"),
    )


def _routing_ingress():
    return _ingress(_ingress_capsule(kind="routing", namespace="dht.routing", key="node-contact"))


def _routing_anchor_capsule(ingress_report=None, **kw):
    ingress_report = ingress_report or _routing_ingress()
    data = dict(
        component="routing-anchor",
        profile="generic-i2p-dht",
        purpose="bootstrap",
        request_id="rev0101-routing-anchor",
        sequence=1,
        previous_digest=b"",
        record_ingress_digest=ingress_report.report_digest,
        contact_lease_digest=LEASE,
        route_attestation_digest=ATTEST,
        destination_digest=DEST,
        node_id_digest=NODE,
        expected_node_id_digest=NODE,
        lease_expires_at=2000,
        now=1000,
        signed_contact_lease=True,
        signed_route_attestation=True,
        route_gossip_bound=True,
        endpoint_is_i2p_destination=True,
        raw_ip_endpoint_present=False,
        native_transport_attempted=False,
        preserve_contact_lease_memory=True,
        preserve_route_gossip_memory=True,
        preserve_tombstone_memory=True,
        preserve_witness_memory=True,
        contact_family_id="contact-a",
        introducer_family_id="intro-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return RoutingAnchorCapsule(**data)


def _routing_anchor(capsule=None, ingress_report=None):
    ingress_report = ingress_report or _routing_ingress()
    return assess_routing_anchor(
        ingress_report,
        FakeComponent(report_digest=LEASE),
        FakeComponent(report_digest=ATTEST),
        capsule or _routing_anchor_capsule(ingress_report),
        observed_contact_families=("contact-a", "contact-b"),
        observed_introducer_families=("intro-a", "intro-b"),
        observed_path_families=("path-a", "path-b"),
    )


def _route_storage_capsule(anchor_report=None, **kw):
    anchor_report = anchor_report or _routing_anchor()
    data = dict(
        component="route-storage",
        profile="generic-i2p-dht",
        bucket_id="bucket-7",
        bucket_purpose="bootstrap",
        request_id="rev0101-route-storage",
        sequence=1,
        previous_digest=b"",
        routing_anchor_digest=anchor_report.report_digest,
        destination_digest=DEST,
        node_id_digest=NODE,
        bucket_region_digest=BUCKET_REGION,
        lease_expires_at=2000,
        now=1000,
        bucket_size=5,
        bucket_capacity=8,
        replacement_cache_size=1,
        replacement_cache_capacity=4,
        stale_contact_digest=STALE,
        stale_contact_probe_required=False,
        destination_bound_node_id=True,
        endpoint_is_i2p_destination=True,
        raw_ip_endpoint_present=False,
        garden_or_introducer_claims_authority=False,
        preserve_route_gossip_memory=True,
        preserve_contact_lease_memory=True,
        preserve_stale_contact_memory=True,
        preserve_witness_memory=True,
        contact_family_id="contact-a",
        introducer_family_id="intro-a",
        path_family_id="path-a",
    )
    data.update(kw)
    return RouteStorageCapsule(**data)


def _route_storage(capsule=None, anchor_report=None):
    anchor_report = anchor_report or _routing_anchor()
    return assess_route_storage(
        anchor_report,
        capsule or _route_storage_capsule(anchor_report),
        observed_contact_families=("contact-a", "contact-b"),
        observed_introducer_families=("intro-a", "intro-b"),
        observed_path_families=("path-a", "path-b"),
    )


def test_mutable_placement_accepts_observation_without_claiming_latestness():
    report = _mutable()
    assert report.decision_kind == MutablePlacementDecisionKind.ACCEPT_MUTABLE_PLACEMENT
    assert report.accepted
    assert report.mutable_observation_placed
    assert not report.latestness_claimed


def test_mutable_placement_holds_missing_previous_link_instead_of_accepting_latestness():
    ingress = _ingress()
    capsule = _mutable_capsule(ingress, missing_previous_link=True, previous_head_digest=sha256(b"unexpected"))
    report = _mutable(capsule, ingress)
    assert report.decision_kind == MutablePlacementDecisionKind.HOLD_GAP_OR_WATCH
    assert report.watch and not report.accepted


def test_mutable_placement_quarantines_live_tombstone():
    ingress = _ingress()
    report = _mutable(_mutable_capsule(ingress, live_tombstone_seen=True), ingress)
    assert report.decision_kind == MutablePlacementDecisionKind.QUARANTINE_LIVE_TOMBSTONE
    assert report.quarantine


def test_provider_bucket_indexes_claim_without_content_truth():
    report = _provider_bucket()
    assert report.decision_kind == ProviderBucketDecisionKind.ACCEPT_PROVIDER_BUCKET
    assert report.accepted
    assert report.provider_indexed
    assert not report.content_truth_claimed


def test_provider_bucket_holds_full_bucket_for_sweep():
    provider = _provider_semantics()
    report = _provider_bucket(_provider_bucket_capsule(provider, current_bucket_count=10, bucket_capacity=10), provider)
    assert report.decision_kind == ProviderBucketDecisionKind.HOLD_BUCKET_FULL_TO_SWEEP
    assert report.watch and not report.accepted


def test_provider_bucket_rejects_content_payload_storage():
    provider = _provider_semantics()
    report = _provider_bucket(_provider_bucket_capsule(provider, content_payload_stored=True), provider)
    assert report.decision_kind == ProviderBucketDecisionKind.QUARANTINE_CONTENT_STORAGE_ATTEMPT
    assert report.quarantine


def test_route_storage_accepts_i2p_bound_contact():
    report = _route_storage()
    assert report.decision_kind == RouteStorageDecisionKind.ACCEPT_ROUTE_STORAGE
    assert report.accepted
    assert report.route_stored


def test_route_storage_uses_replacement_cache_when_bucket_full_without_authority():
    anchor = _routing_anchor()
    report = _route_storage(_route_storage_capsule(anchor, bucket_size=8, bucket_capacity=8, stale_contact_probe_required=False), anchor)
    assert report.decision_kind == RouteStorageDecisionKind.HOLD_REPLACEMENT_CACHE
    assert report.accepted
    assert report.replacement_cached
    assert report.watch


def test_route_storage_quarantines_garden_authority_claim():
    anchor = _routing_anchor()
    report = _route_storage(_route_storage_capsule(anchor, garden_or_introducer_claims_authority=True), anchor)
    assert report.decision_kind == RouteStorageDecisionKind.QUARANTINE_AUTHORITY_OR_RAW_ENDPOINT
    assert report.quarantine


def test_substrate_spine_and_placement_fold_pass():
    spine = audit_substrate_spine(ROOT, revision="rev0101")
    fold = audit_substrate_placement_fold(ROOT, revision="rev0101")
    assert spine.status == "pass", spine.findings
    assert fold.status == "pass", fold.findings
