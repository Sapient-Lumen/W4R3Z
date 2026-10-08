#!/usr/bin/env python3
"""Run deterministic rev0101 substrate placement evidence."""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from i2p_dht_lab.ids import sha256
from i2p_dht_lab.mutableplacement import MutablePlacementCapsule, assess_mutable_placement
from i2p_dht_lab.providerbucket import ProviderBucketCapsule, assess_provider_bucket
from i2p_dht_lab.providersemantics import ProviderSemanticsCapsule, assess_provider_semantics
from i2p_dht_lab.recordingress import RecordIngressCapsule, assess_record_ingress
from i2p_dht_lab.routestorage import RouteStorageCapsule, assess_route_storage
from i2p_dht_lab.routinganchor import RoutingAnchorCapsule, assess_routing_anchor
from i2p_dht_lab.substrateplacementfold import audit_substrate_placement_fold
from i2p_dht_lab.substratespine import audit_substrate_spine

REVISION = "rev0101"
SUBSTRATE = sha256(b"micro-rev0101-substrate")
ORACLE = sha256(b"micro-rev0101-oracle")
PARSE = sha256(b"micro-rev0101-parse")
VALIDATOR = sha256(b"micro-rev0101-validator")
ADMISSION = sha256(b"micro-rev0101-admission")
WITNESS = sha256(b"micro-rev0101-witness")
PROOF = sha256(b"micro-rev0101-proof")
BUDGET = sha256(b"micro-rev0101-budget")
LEASE = sha256(b"micro-rev0101-lease")
ATTEST = sha256(b"micro-rev0101-attest")
DEST = sha256(b"micro-rev0101-dest")
NODE = sha256(b"micro-rev0101-node")
TARGET = sha256(b"micro-rev0101-target")


@dataclass(frozen=True)
class Component:
    accepted: bool = True
    substrate_reentered: bool = False
    python_record_truth: bool = False
    native_record_permission: bool = False
    native_permission_leak: bool = False
    report_digest: bytes = b""


def ingress(kind: str, namespace: str, key: str):
    cap = RecordIngressCapsule(
        "record-ingress", "micro", namespace, kind, key, "micro-rev0101", 1, b"",
        SUBSTRATE, ORACLE, PARSE, VALIDATOR, ADMISSION, sha256(("payload:" + key).encode()), 256, 4096, 1200, 3600,
        True, True, True, True, False, False, True, True, True, True, True, True, True, True, "family-a", "path-a"
    )
    return assess_record_ingress(
        Component(True, True, False, False, False, SUBSTRATE),
        Component(True, False, True, False, False, ORACLE),
        Component(True, report_digest=PARSE), Component(True, report_digest=VALIDATOR), Component(True, report_digest=ADMISSION), cap,
        observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b")
    )


def main() -> None:
    mutable_ingress = ingress("mutable", "dht.mutable", "mutable-key")
    mutable_cap = MutablePlacementCapsule(
        "mutable-placement", "micro", "mutable-key", "dht.mutable", "micro-rev0101-mutable", 1, b"",
        mutable_ingress.report_digest, sha256(b"head"), VALIDATOR, WITNESS, sha256(b"publisher"), sha256(b"salt"), TARGET, TARGET,
        11, 10, sha256(b"prev-head"), sha256(b"prev-head"), True, True, True, True, False, False, False, False, False,
        True, True, True, True, True, "family-a", "path-a"
    )
    mutable = assess_mutable_placement(mutable_ingress, Component(True, report_digest=VALIDATOR), Component(True, report_digest=WITNESS), mutable_cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))

    provider_ingress = ingress("provider", "dht.providers", "provider-key")
    provider_sem_cap = ProviderSemanticsCapsule(
        "provider-semantics", "micro", "dht.providers", sha256(b"content"), DEST, "micro-rev0101-provider", 1, b"",
        provider_ingress.report_digest, sha256(b"claim"), PROOF, BUDGET, WITNESS, "true", True, True, True, True,
        True, True, False, True, True, True, True, True, "family-a", "path-a"
    )
    provider_sem = assess_provider_semantics(provider_ingress, Component(True, report_digest=PROOF), Component(True, report_digest=BUDGET), Component(True, report_digest=WITNESS), provider_sem_cap, observed_families=("family-a", "family-b"), observed_path_families=("path-a", "path-b"))
    bucket_cap = ProviderBucketCapsule(
        "provider-bucket", "micro", "region-1", "provider_index", "micro-rev0101-bucket", 1, b"", provider_sem.report_digest,
        sha256(b"region"), sha256(b"content"), DEST, sha256(b"entry"), 1200, 3600, 1000, 2200, 1, 10, "true", False,
        False, False, False, True, True, True, True, True, "source-a", "provider-a", "path-a"
    )
    bucket = assess_provider_bucket(provider_sem, bucket_cap, observed_source_families=("source-a", "source-b"), observed_provider_families=("provider-a", "provider-b"), observed_path_families=("path-a", "path-b"))

    routing_ingress = ingress("routing", "dht.routing", "node-contact")
    route_anchor_cap = RoutingAnchorCapsule(
        "routing-anchor", "micro", "bootstrap", "micro-rev0101-route-anchor", 1, b"", routing_ingress.report_digest,
        LEASE, ATTEST, DEST, NODE, NODE, 2000, 1000, True, True, True, True, False, False, True, True, True, True,
        "contact-a", "intro-a", "path-a"
    )
    anchor = assess_routing_anchor(routing_ingress, Component(True, report_digest=LEASE), Component(True, report_digest=ATTEST), route_anchor_cap, observed_contact_families=("contact-a", "contact-b"), observed_introducer_families=("intro-a", "intro-b"), observed_path_families=("path-a", "path-b"))
    route_cap = RouteStorageCapsule(
        "route-storage", "micro", "bucket-1", "bootstrap", "micro-rev0101-route-store", 1, b"", anchor.report_digest,
        DEST, NODE, sha256(b"bucket-region"), 2000, 1000, 1, 8, 0, 4, sha256(b"stale"), False, True, True, False, False,
        True, True, True, True, "contact-a", "intro-a", "path-a"
    )
    route = assess_route_storage(anchor, route_cap, observed_contact_families=("contact-a", "contact-b"), observed_introducer_families=("intro-a", "intro-b"), observed_path_families=("path-a", "path-b"))

    spine = audit_substrate_spine(ROOT, revision=REVISION)
    fold = audit_substrate_placement_fold(ROOT, revision=REVISION)
    assert mutable.accepted and bucket.accepted and route.accepted
    assert spine.status == "pass", spine.findings
    assert fold.status == "pass", fold.findings
    payload = {
        "revision": REVISION,
        "status": "pass",
        "mutable_placement": mutable.decision_kind.value,
        "provider_bucket": bucket.decision_kind.value,
        "route_storage": route.decision_kind.value,
        "substrate_spine": spine.status,
        "substrateplacementfold": fold.status,
        "digests": {
            "mutable": mutable.report_digest.hex(),
            "bucket": bucket.report_digest.hex(),
            "route": route.report_digest.hex(),
            "spine": spine.report_digest.hex(),
            "fold": fold.report_digest.hex(),
        },
    }
    target = ROOT / "artifacts/process/rev0101_micro_simulation.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"micro-simulation pass: wrote {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
