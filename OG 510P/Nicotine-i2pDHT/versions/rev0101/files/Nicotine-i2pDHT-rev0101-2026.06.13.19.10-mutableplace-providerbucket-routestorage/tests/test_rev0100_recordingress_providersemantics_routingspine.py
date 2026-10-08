from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.recordingress import (
    RecordIngressCapsule,
    RecordIngressDecisionKind,
    assess_record_ingress,
)
from i2p_dht_lab.providersemantics import (
    ProviderSemanticsCapsule,
    ProviderSemanticsDecisionKind,
    assess_provider_semantics,
)
from i2p_dht_lab.routinganchor import (
    RoutingAnchorCapsule,
    RoutingAnchorDecisionKind,
    assess_routing_anchor,
)
from i2p_dht_lab.substratecenturyfold import audit_substrate_century_fold
from i2p_dht_lab.substratespine import audit_substrate_spine

ROOT = Path(__file__).resolve().parents[1]
SUBSTRATE = sha256(b"rev0100-substrate-reentry")
ORACLE = sha256(b"rev0100-record-oracle")
PARSE = sha256(b"rev0100-parse")
VALIDATOR = sha256(b"rev0100-validator")
ADMISSION = sha256(b"rev0100-admission")
PROOF = sha256(b"rev0100-proof")
BUDGET = sha256(b"rev0100-budget")
WITNESS = sha256(b"rev0100-witness")
LEASE = sha256(b"rev0100-lease")
ATTEST = sha256(b"rev0100-attestation")
PAYLOAD = sha256(b"rev0100-payload")
DEST = sha256(b"rev0100-dest")
NODE = sha256(b"rev0100-node")


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


def _ingress_capsule(**kw):
    data = dict(
        component="record-ingress",
        profile="generic-i2p-dht",
        namespace="dht.providers",
        record_kind="provider",
        record_key="provider-key-1",
        request_id="rev0100-record-ingress",
        sequence=1,
        previous_digest=b"",
        substrate_reentry_digest=SUBSTRATE,
        record_plane_oracle_digest=ORACLE,
        parse_report_digest=PARSE,
        validator_report_digest=VALIDATOR,
        admission_report_digest=ADMISSION,
        payload_digest=PAYLOAD,
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


def _ingress(capsule=None, substrate=None, oracle=None, parse=None, validator=None, admission=None):
    return assess_record_ingress(
        substrate or FakeSubstrateReentry(),
        oracle or FakeRecordPlaneOracle(),
        parse or FakeComponent(report_digest=PARSE),
        validator or FakeComponent(report_digest=VALIDATOR),
        admission or FakeComponent(report_digest=ADMISSION),
        capsule or _ingress_capsule(),
        observed_families=("family-a", "family-b"),
        observed_path_families=("path-a", "path-b"),
    )


def _provider_capsule(ingress_report=None, **kw):
    ingress_report = ingress_report or _ingress()
    data = dict(
        component="provider-semantics",
        profile="generic-i2p-dht",
        namespace="dht.providers",
        content_key_digest=sha256(b"content-key"),
        provider_destination_digest=DEST,
        request_id="rev0100-provider-semantics",
        sequence=1,
        previous_digest=b"",
        record_ingress_digest=ingress_report.report_digest,
        provider_claim_digest=sha256(b"claim"),
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


def _provider(capsule=None, ingress_report=None, proof=None, budget=None, witness=None):
    ingress_report = ingress_report or _ingress()
    return assess_provider_semantics(
        ingress_report,
        proof or FakeComponent(report_digest=PROOF),
        budget or FakeComponent(report_digest=BUDGET),
        witness or FakeComponent(report_digest=WITNESS),
        capsule or _provider_capsule(ingress_report),
        observed_families=("family-a", "family-b"),
        observed_path_families=("path-a", "path-b"),
    )


def _routing_ingress():
    return _ingress(_ingress_capsule(namespace="dht.routing", record_kind="routing", record_key="node-contact"))


def _route_capsule(ingress_report=None, **kw):
    ingress_report = ingress_report or _routing_ingress()
    data = dict(
        component="routing-anchor",
        profile="generic-i2p-dht",
        purpose="bootstrap",
        request_id="rev0100-routing-anchor",
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


def _route(capsule=None, ingress_report=None, lease=None, attest=None):
    ingress_report = ingress_report or _routing_ingress()
    return assess_routing_anchor(
        ingress_report,
        lease or FakeComponent(report_digest=LEASE),
        attest or FakeComponent(report_digest=ATTEST),
        capsule or _route_capsule(ingress_report),
        observed_contact_families=("contact-a", "contact-b"),
        observed_introducer_families=("intro-a", "intro-b"),
        observed_path_families=("path-a", "path-b"),
    )


def test_record_ingress_accepts_python_parsed_validated_admitted_provider_record():
    report = _ingress()
    assert report.decision_kind == RecordIngressDecisionKind.ACCEPT_RECORD_INGRESS
    assert report.accepted and report.record_admitted
    assert report.record_kind == "provider"


def test_record_ingress_rejects_native_leak_parse_validator_admission_and_memory_drop():
    assert _ingress(_ingress_capsule(native_validation_attempted=True)).decision_kind == RecordIngressDecisionKind.QUARANTINE_NATIVE_PERMISSION_LEAK
    assert _ingress(_ingress_capsule(canonical_wire=False)).decision_kind == RecordIngressDecisionKind.QUARANTINE_PARSE_NOT_CANONICAL
    assert _ingress(_ingress_capsule(python_validator_accepted=False)).decision_kind == RecordIngressDecisionKind.QUARANTINE_VALIDATOR_REJECTED
    assert _ingress(_ingress_capsule(admission_accepted=False)).decision_kind == RecordIngressDecisionKind.QUARANTINE_ADMISSION_REJECTED
    assert _ingress(_ingress_capsule(preserve_provider_false_memory=False)).decision_kind == RecordIngressDecisionKind.QUARANTINE_MEMORY_DROP


def test_record_ingress_detects_digest_size_sequence_and_diversity_pressure():
    assert _ingress(_ingress_capsule(parse_report_digest=sha256(b"wrong"))).decision_kind == RecordIngressDecisionKind.QUARANTINE_DIGEST_DRIFT
    assert _ingress(_ingress_capsule(value_size=5000)).decision_kind == RecordIngressDecisionKind.QUARANTINE_SIZE_OR_TTL
    first = _ingress_capsule()
    second = replace(first, sequence=2, previous_digest=sha256(b"wrong-prev"))
    report = assess_record_ingress(
        FakeSubstrateReentry(), FakeRecordPlaneOracle(), FakeComponent(report_digest=PARSE), FakeComponent(report_digest=VALIDATOR), FakeComponent(report_digest=ADMISSION),
        second, previous=first, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"),
    )
    assert report.decision_kind == RecordIngressDecisionKind.QUARANTINE_PREVIOUS_LINK_MISMATCH
    report = assess_record_ingress(
        FakeSubstrateReentry(), FakeRecordPlaneOracle(), FakeComponent(report_digest=PARSE), FakeComponent(report_digest=VALIDATOR), FakeComponent(report_digest=ADMISSION),
        first, observed_families=("family-a",), observed_path_families=("path-a", "path-b"),
    )
    assert report.decision_kind == RecordIngressDecisionKind.QUARANTINE_LOW_DIVERSITY


def test_provider_semantics_accepts_challenge_bound_true_provider_without_raw_key_leak():
    report = _provider()
    assert report.decision_kind == ProviderSemanticsDecisionKind.ACCEPT_PROVIDER_SEMANTICS
    assert report.accepted and report.provider_semantically_confirmed


def test_provider_semantics_separates_false_provider_refusal_and_metadata_leak():
    assert _provider(_provider_capsule(proof_result="false")).decision_kind == ProviderSemanticsDecisionKind.QUARANTINE_FALSE_PROVIDER
    refused = _provider(_provider_capsule(proof_result="refused"))
    assert refused.decision_kind == ProviderSemanticsDecisionKind.WATCH_USEFUL_REFUSAL
    assert refused.useful_refusal and refused.watch and not refused.accepted
    assert _provider(_provider_capsule(raw_content_key_exposed=True)).decision_kind == ProviderSemanticsDecisionKind.QUARANTINE_METADATA_LEAK
    assert _provider(_provider_capsule(witness_preserved=False)).decision_kind == ProviderSemanticsDecisionKind.QUARANTINE_MEMORY_DROP


def test_provider_semantics_rejects_non_provider_ingress_digest_drift_and_forks():
    routing_ingress = _routing_ingress()
    cap = _provider_capsule(routing_ingress, record_ingress_digest=routing_ingress.report_digest)
    assert _provider(cap, routing_ingress).decision_kind == ProviderSemanticsDecisionKind.QUARANTINE_NOT_PROVIDER_INGRESS
    ingress_report = _ingress()
    assert _provider(_provider_capsule(ingress_report, record_ingress_digest=sha256(b"wrong")), ingress_report).decision_kind == ProviderSemanticsDecisionKind.QUARANTINE_DIGEST_DRIFT
    first = _provider_capsule(ingress_report)
    second = replace(first, note="same-seq-fork")
    report = assess_provider_semantics(
        ingress_report, FakeComponent(report_digest=PROOF), FakeComponent(report_digest=BUDGET), FakeComponent(report_digest=WITNESS), second, previous=first,
        observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"),
    )
    assert report.decision_kind == ProviderSemanticsDecisionKind.QUARANTINE_SAME_SEQUENCE_FORK


def test_routing_anchor_accepts_i2p_contact_with_lease_attestation_and_family_diversity():
    report = _route()
    assert report.decision_kind == RoutingAnchorDecisionKind.ACCEPT_ROUTING_ANCHOR
    assert report.accepted and report.route_anchor_accepted


def test_routing_anchor_rejects_raw_ip_native_transport_expiry_node_drift_and_intro_monoculture():
    assert _route(_route_capsule(raw_ip_endpoint_present=True)).decision_kind == RoutingAnchorDecisionKind.QUARANTINE_RAW_IP_OR_NATIVE_TRANSPORT
    assert _route(_route_capsule(native_transport_attempted=True)).decision_kind == RoutingAnchorDecisionKind.QUARANTINE_RAW_IP_OR_NATIVE_TRANSPORT
    assert _route(_route_capsule(lease_expires_at=999)).decision_kind == RoutingAnchorDecisionKind.QUARANTINE_EXPIRED_OR_PURPOSE_DRIFT
    assert _route(_route_capsule(node_id_digest=sha256(b"wrong"))).decision_kind == RoutingAnchorDecisionKind.QUARANTINE_DESTINATION_OR_NODE_DRIFT
    ingress_report = _routing_ingress()
    cap = _route_capsule(ingress_report)
    report = assess_routing_anchor(
        ingress_report, FakeComponent(report_digest=LEASE), FakeComponent(report_digest=ATTEST), cap,
        observed_contact_families=("contact-a", "contact-b"), observed_introducer_families=("intro-a",), observed_path_families=("path-a", "path-b"),
    )
    assert report.decision_kind == RoutingAnchorDecisionKind.QUARANTINE_INTRODUCER_MONOCULTURE


def test_routing_anchor_rejects_non_routing_ingress_digest_drift_and_memory_drop():
    provider_ingress = _ingress()
    cap = _route_capsule(provider_ingress, record_ingress_digest=provider_ingress.report_digest)
    assert _route(cap, provider_ingress).decision_kind == RoutingAnchorDecisionKind.QUARANTINE_NOT_ROUTING_INGRESS
    routing_ingress = _routing_ingress()
    assert _route(_route_capsule(routing_ingress, record_ingress_digest=sha256(b"wrong")), routing_ingress).decision_kind == RoutingAnchorDecisionKind.QUARANTINE_DIGEST_DRIFT
    assert _route(_route_capsule(routing_ingress, preserve_route_gossip_memory=False), routing_ingress).decision_kind == RoutingAnchorDecisionKind.QUARANTINE_MEMORY_DROP


def test_substrate_spine_and_century_fold_pass_current_path():
    spine = audit_substrate_spine(ROOT, revision="rev0100")
    assert spine.status == "pass", spine.findings
    fold = audit_substrate_century_fold(ROOT, revision="rev0100")
    assert fold.status == "pass", fold.findings
