#!/usr/bin/env python3
"""Build and check a concrete threat-transfer matrix for the MUCC lane.

The risk this guards is not a missing registry entry; it is a scientific overstep:
quoting a MUCC committee-contact cost floor or privacy conclusion as if it automatically transferred to
IPFS delegated routing, OHTTP role separation, Tor circuits, I2P tunnels, or a
Kademlia lookup without restating the witness/adversary/availability tuple.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

MUCC_SOURCE = "series/anondht_state_series/paper2_mucc_committee_contact_privacy/paper.tex"
MUCC_CARD = "release_queue/evidence_packs/2026.06.16-committee-contact-set-privacy-in-anonymous-dht-lookups/MUCC_CONTACT_FLOOR_CARD.json"

REQUIRED_SYSTEM_IDS = {
    "native_mucc_committee_contact_floor",
    "ipfs_kademlia_provider_records",
    "ipfs_delegated_routing_http_v1",
    "peer2pir_ipfs_query_privacy",
    "ohttp_role_separation",
    "tor_low_latency_circuits",
    "i2p_netdb_floodfill_tunnels",
}

FORBIDDEN_EXTERNAL_TRANSFER_STATUSES = {
    "transferred",
    "release_safe",
    "publication_ready",
    "theorem_bearing_transfer",
    "native_contact_floor_bound",
}


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def contains_any(text: str, words: list[str]) -> bool:
    lower = text.lower()
    return any(word.lower() in lower for word in words)


def build_matrix(root: pathlib.Path, release: dict[str, Any]) -> list[dict[str, Any]]:
    source_path = root / MUCC_SOURCE
    source_hash = sha256_file(source_path)
    card = load_json(root / MUCC_CARD)
    values = card.get("card_values", {}) if isinstance(card.get("card_values"), dict) else {}
    return [
        {
            "system_id": "native_mucc_committee_contact_floor",
            "system_name": "MUCC committee-contact cost witness declared by the archive source",
            "source_boundary": "archive_local_source_and_evidence_card",
            "source_tex": MUCC_SOURCE,
            "source_sha256": source_hash,
            "evidence_card": MUCC_CARD,
            "observed_witness": "committee/contact-set projection C over M declared committees and destination set D",
            "native_tuple": {
                "M": values.get("committee_universe_M"),
                "d": values.get("destination_replication_d"),
                "t": values.get("live_threshold_t"),
                "alpha": values.get("alpha"),
                "beta": values.get("beta"),
                "expected_contact_floor": values.get("expected_contact_floor_declared"),
            },
            "claim_status": "native_contact_floor_bound",
            "transfer_rule": "The card is theorem-bearing only as a conditional contact-cost row for its own declared witness, distinct outer (d,t) and inner (n,h,q,rho) layers, committee-label equalization row, and exact/upper-yield live-factor interpretation. It is not joint contact-set privacy.",
            "publication_blocker_if_used": "external hostile review/countersignature remains missing",
        },
        {
            "system_id": "ipfs_kademlia_provider_records",
            "system_name": "IPFS Kademlia DHT provider-record lookup",
            "source_boundary": "online_spec_research_plus_archive_related_work",
            "external_sources": [
                "https://specs.ipfs.tech/routing/kad-dht/",
                "https://specs.ipfs.tech/routing/http-routing-v1/",
            ],
            "observed_witness": "closest-peer/provider-record contact path and provider set, not automatically the archive committee witness",
            "claim_status": "not_transferred_without_new_model",
            "transfer_rule": "A concrete IPFS claim must restate M, d, t, alpha, provider-record lifetime/cache behavior, routing-table/Sybil assumptions, and the observer who sees contacts.",
            "publication_blocker_if_used": "using this row as a theorem citation without a new source-bound IPFS mapping card is a fail-closed overclaim",
        },
        {
            "system_id": "ipfs_delegated_routing_http_v1",
            "system_name": "IPFS Delegated Routing V1 HTTP API",
            "source_boundary": "online_spec_research",
            "external_sources": ["https://specs.ipfs.tech/routing/http-routing-v1/"],
            "observed_witness": "HTTP routing server sees content/peer/naming lookup keys unless an added privacy layer changes that fact",
            "claim_status": "role_boundary_not_mucc_transfer",
            "transfer_rule": "Delegation changes who observes the lookup; it does not by itself instantiate MUCC contact-set equalization or the declared committee universe.",
            "publication_blocker_if_used": "must add a delegated-routing observer row and leakage statement before any MUCC-derived claim",
        },
        {
            "system_id": "peer2pir_ipfs_query_privacy",
            "system_name": "Peer2PIR / PIR-style private queries for IPFS",
            "source_boundary": "online_paper_research",
            "external_sources": ["https://arxiv.org/abs/2405.17307"],
            "observed_witness": "query-content privacy axis; contacted peer/server set remains a separate witness unless explicitly modeled",
            "claim_status": "complementary_not_substitutive",
            "transfer_rule": "PIR-style content privacy cannot be used as evidence for MUCC contact marginals or joint contact-set privacy; each requires its own source-bound witness and check.",
            "publication_blocker_if_used": "must not substitute content-query secrecy for contact-set equalization",
        },
        {
            "system_id": "ohttp_role_separation",
            "system_name": "Oblivious HTTP relay/gateway/origin role separation",
            "source_boundary": "online_rfc_research",
            "external_sources": ["https://www.ietf.org/rfc/rfc9458.html"],
            "observed_witness": "client identity/content unlinkability under relay/gateway separation, not a DHT committee-contact schedule",
            "claim_status": "analogy_only_not_transfer",
            "transfer_rule": "OHTTP can inspire role-separation vocabulary but cannot certify DHT contact-floor arithmetic or multi-committee liveness assumptions.",
            "publication_blocker_if_used": "must state a separate relay/gateway collusion and traffic-analysis model",
        },
        {
            "system_id": "tor_low_latency_circuits",
            "system_name": "Tor low-latency onion-routing circuits",
            "source_boundary": "online_spec_research",
            "external_sources": ["https://spec.torproject.org/intro/index.html"],
            "observed_witness": "guard/middle/exit circuit path and relay cells, not a MUCC destination committee-set",
            "claim_status": "analogy_only_not_transfer",
            "transfer_rule": "Tor path-selection/circuit claims require their own guard, directory, relay, and traffic-correlation assumptions; MUCC is not a Tor anonymity proof.",
            "publication_blocker_if_used": "must not quote the 152-contact floor as a Tor relay-path floor",
        },
        {
            "system_id": "i2p_netdb_floodfill_tunnels",
            "system_name": "I2P netDB floodfill lookup and tunnel routing",
            "source_boundary": "online_doc_research_plus_archive_related_work",
            "external_sources": ["https://i2p.net/en/docs/overview/intro/"],
            "observed_witness": "floodfill netDB lookup plus inbound/outbound directed tunnel paths, with object-type confidentiality differences",
            "claim_status": "mapped_example_requires_new_card",
            "transfer_rule": "I2P-like use needs a new card for floodfill count, replication, parallel lookup behavior, LeaseSet/RouterInfo confidentiality, and who observes tunnel endpoints.",
            "publication_blocker_if_used": "generic MUCC row is explanatory only until the I2P-specific tuple is source-bound",
        },
    ]


def check(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    source_text = (root / MUCC_SOURCE).read_text(encoding="utf-8", errors="replace")
    source_hash = sha256_file(root / MUCC_SOURCE)
    card = load_json(root / MUCC_CARD)
    matrix = build_matrix(root, release)
    failures: list[dict[str, Any]] = []

    if card.get("source_tex") != MUCC_SOURCE:
        failures.append({"category": "mucc_card_source_path_mismatch", "actual": card.get("source_tex"), "expected": MUCC_SOURCE})
    if card.get("source_sha256") != source_hash:
        failures.append({"category": "mucc_card_source_hash_mismatch", "actual": card.get("source_sha256"), "expected": source_hash})

    ids = [str(row.get("system_id", "")) for row in matrix]
    missing_ids = sorted(REQUIRED_SYSTEM_IDS - set(ids))
    duplicate_ids = sorted({row_id for row_id in ids if ids.count(row_id) > 1})
    if missing_ids:
        failures.append({"category": "missing_required_transfer_rows", "missing": missing_ids})
    if duplicate_ids:
        failures.append({"category": "duplicate_transfer_rows", "duplicates": duplicate_ids})

    native_rows = [row for row in matrix if row.get("claim_status") == "native_contact_floor_bound"]
    if [row.get("system_id") for row in native_rows] != ["native_mucc_committee_contact_floor"]:
        failures.append({"category": "native_transfer_status_not_unique", "native_rows": [row.get("system_id") for row in native_rows]})

    for row in matrix:
        system_id = str(row.get("system_id", ""))
        status = str(row.get("claim_status", ""))
        transfer_rule = str(row.get("transfer_rule", ""))
        blocker = str(row.get("publication_blocker_if_used", ""))
        if system_id != "native_mucc_committee_contact_floor":
            if status in FORBIDDEN_EXTERNAL_TRANSFER_STATUSES:
                failures.append({"category": "external_row_claims_native_transfer", "system_id": system_id, "claim_status": status})
            if not re.search(r"new|separate|not|cannot|must", transfer_rule, flags=re.I):
                failures.append({"category": "external_row_transfer_rule_not_fail_closed", "system_id": system_id, "transfer_rule": transfer_rule})
            if not blocker:
                failures.append({"category": "external_row_missing_publication_blocker", "system_id": system_id})
            if not row.get("external_sources"):
                failures.append({"category": "external_row_missing_source_basis", "system_id": system_id})

    source_mentions = {
        "ipfs": contains_any(source_text, ["IPFS", "Peer2PIR"]),
        "kademlia": contains_any(source_text, ["Kademlia", "DHT"]),
        "i2p": contains_any(source_text, ["I2P", "netDB", "floodfill"]),
        "mucc_protocol_mapping_section": "Protocol extraction and non-transfer checklist" in source_text,
        "mucc_excluded_channels": "Missing rows block transfer" in source_text and "joint scheduler law" in source_text,
        "mucc_nested_quorum_guard": "Nested-quorum parameter non-substitution guard" in source_text and "outer-as-inner substitution" in source_text,
        "mucc_label_symmetry_guard": "Joint key-independence is not committee-label uniformity" in source_text and "global marginal-diameter" in source_text,
        "mucc_joint_privacy_nonclaim": "Exact MUCC can leak the destination perfectly" in source_text and "\\Delta_C=1" in source_text.replace(" ", "") and "Any system claiming both must prove both axes" in source_text,
    }
    for name, present in source_mentions.items():
        if name in {"ipfs", "kademlia", "i2p", "mucc_protocol_mapping_section", "mucc_excluded_channels", "mucc_nested_quorum_guard", "mucc_label_symmetry_guard", "mucc_joint_privacy_nonclaim"} and not present:
            failures.append({"category": "expected_source_anchor_missing", "anchor": name})

    overclaim_terms = [
        "therefore IPFS is anonymous",
        "proves Tor anonymity",
        "proves I2P anonymity",
        "OHTTP satisfies MUCC",
        "Peer2PIR proves contact-set privacy",
    ]
    found_overclaim_terms = [term for term in overclaim_terms if term.lower() in source_text.lower()]
    if found_overclaim_terms:
        failures.append({"category": "source_contains_forbidden_transfer_overclaim", "terms": found_overclaim_terms})

    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "report_kind": "mucc_threat_transfer_matrix",
        "source_tex": MUCC_SOURCE,
        "source_sha256": source_hash,
        "evidence_card": MUCC_CARD,
        "matrix": matrix,
        "source_anchor_scan": source_mentions,
        "summary": {
            "checks_failed": len(failures),
            "transfer_rows": len(matrix),
            "external_rows": len([row for row in matrix if row.get("system_id") != "native_mucc_committee_contact_floor"]),
            "native_theorem_rows": len(native_rows),
            "external_transfer_authorized_rows": 0,
            "forbidden_overclaim_terms_found": len(found_overclaim_terms),
            "publication_authorized": False,
        },
        "failures": failures[:80],
        "fail_closed_rule": "MUCC may be used as the native conditional contact-cost theorem only for the source-bound witness with distinct outer/inner quorum layers and a proved committee-label equalization row; it is not joint contact-set privacy. All IPFS, delegated-routing, Peer2PIR, OHTTP, Tor, and I2P rows are blocked from theorem-bearing transfer until a new source-bound model/card exists.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = check(root)
    text = json.dumps(report, indent=2) + "\n"
    if args.write_report:
        out = root / args.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
