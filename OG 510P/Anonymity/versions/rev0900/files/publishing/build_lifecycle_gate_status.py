#!/usr/bin/env python3
"""Build current lifecycle-gate status report for the shipped bundle."""
from __future__ import annotations

import argparse
import json
import pathlib
import re
from collections import Counter


def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def parse_latest_decision_pointer(path: pathlib.Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.search(r"`(release_queue/decisions/[^`]+\.md)`", line)
        if m:
            return m.group(1)
    return None


def count_queue_notes(directory: pathlib.Path) -> int:
    if not directory.exists():
        return 0
    return len([p for p in directory.glob("*.md") if p.name != "README.md"])


def build(root: pathlib.Path) -> dict:
    manifest = load_json(root / "RELEASE_MANIFEST.json")
    gates = load_json(root / "publishing" / "lifecycle_gates.json")
    transient = load_json(root / "reports" / "transient_surface_audit.json")
    manifest_verify = load_json(root / "reports" / "manifest_sha256_verification.json")
    manifest_coverage = load_json(root / "reports" / "manifest_coverage_audit.json")
    review_inventory_integrity = load_json(root / "reports" / "review_inventory_integrity.json")
    operator_command_hygiene = load_json(root / "reports" / "operator_command_hygiene.json")
    context_pack_contract = load_json(root / "reports" / "context_pack_contract.json")
    context_pack = load_json(root / "CONTEXT_PACK.json")
    citation = load_json(root / "published" / "citation_heads.json")
    publication_classification = load_json(root / "published" / "publication_classification.json")
    public_surface = load_json(root / "published" / "PUBLIC_SURFACE.json")
    queue = load_json(root / "release_queue" / "QUEUE_INDEX.json")
    review_inventory = load_json(root / "release_queue" / "REVIEW_INVENTORY.json")
    decision_index = load_json(root / "release_queue" / "DECISION_INDEX.json")
    latest_pointer = parse_latest_decision_pointer(root / "release_queue" / "LATEST_DECISION.md")
    latest_json = load_json(root / "release_queue" / "LATEST_DECISION.json")
    version = (root / "VERSION").read_text(encoding="utf-8").strip()

    gate_statuses = []
    legacy_paths = [x["path"] for x in publication_classification["legacy_canonical_public_wiki_targets"]]
    new_paths = [x["path"] for x in publication_classification.get("new_post_policy_anonymity_entries", [])]
    frozen_paths = [x["path"] for x in publication_classification["repo_frozen_noncanonical_entries"]]
    expected_latest = decision_index.get("latest_decision", "")

    for gate in gates["gates"]:
        gid = gate["gate_id"]
        missing = [p for p in gate["required_surfaces"] if not (root / p).exists()]
        if missing:
            gate_statuses.append(
                {
                    "gate_id": gid,
                    "stage": gate["stage"],
                    "status": "fail",
                    "reason": "missing required surfaces: " + ", ".join(missing),
                    "required_surfaces": gate["required_surfaces"],
                }
            )
            continue

        if gid == "reentry_identity_and_trust":
            ok = (
                context_pack_contract.get("status") == "pass"
                and transient.get("status") == "pass"
                and manifest_verify.get("status") == "pass"
                and manifest_coverage.get("status") == "pass"
                and operator_command_hygiene.get("status") == "pass"
                and context_pack.get("revision") == manifest.get("revision") == version
            )
            status = "pass" if ok else "fail"
            reason = (
                f"context_pack_contract={context_pack_contract.get('status')} transient={transient.get('status')} "
                f"manifest_verify={manifest_verify.get('status')} manifest_coverage={manifest_coverage.get('status')} "
                f"operator_command_hygiene={operator_command_hygiene.get('status')} "
                f"revision={manifest.get('revision')} version={version}"
            )
        elif gid == "citation_and_public_boundary":
            ok = (
                citation["summary"]["legacy_public_head_count"] == len(legacy_paths)
                and citation["summary"]["repo_frozen_noncanonical_entry_count"] == len(frozen_paths)
                and public_surface["current_public_citation_heads"] == legacy_paths + new_paths
                and public_surface["repo_frozen_noncanonical_entries"] == frozen_paths
            )
            status = "pass" if ok else "fail"
            reason = (
                f"legacy_public_heads={citation['summary']['legacy_public_head_count']} "
                f"new_post_policy_heads={citation['summary']['new_post_policy_anonymity_head_count']} "
                f"frozen_noncanonical={citation['summary']['repo_frozen_noncanonical_entry_count']}"
            )
        elif gid == "queue_and_decision_integrity":
            ok = (
                queue["summary"]["candidate"] == count_queue_notes(root / "release_queue" / "candidates")
                and queue["summary"]["published_ready"] == count_queue_notes(root / "release_queue" / "published_ready")
                and queue["summary"]["hold"] == count_queue_notes(root / "release_queue" / "hold")
                and queue["summary"].get("published", 0) == count_queue_notes(root / "release_queue" / "published")
                and review_inventory["reviewable_unpublished_papers"] == queue["summary"]["reviewable_unpublished_papers"]
                and review_inventory_integrity.get("status") == "pass"
                and expected_latest == latest_pointer == latest_json.get("path")
            )
            status = "pass" if ok else "fail"
            reason = (
                f"candidate={queue['summary']['candidate']} published_ready={queue['summary']['published_ready']} "
                f"hold={queue['summary']['hold']} published={queue['summary'].get('published', 0)} "
                f"decision_notes={decision_index.get('decision_count')} review_inventory_integrity={review_inventory_integrity.get('status')} latest={expected_latest}"
            )
        elif gid == "review_move_readiness":
            status = "manual"
            reason = "review surfaces are present, but any queue move still requires paper-level judgment and a new written decision note"
        elif gid == "publication_execution":
            latest_decision = (root / latest_pointer).read_text(encoding="utf-8").lower() if latest_pointer else ""
            explicit_no_publication = "no publication" in latest_decision
            if explicit_no_publication and queue["summary"].get("published", 0) == 0:
                status = "closed"
                reason = "latest decision is no publication and there are zero executed post-policy releases"
            else:
                status = "manual"
                reason = "publication gate requires an explicit publish decision plus preflight"
        elif gid == "post_publication_audit":
            if citation["summary"]["new_post_policy_anonymity_head_count"] == 0:
                status = "not_applicable"
                reason = "no post-policy Anonymity public heads exist yet"
            else:
                status = "manual"
                reason = "post-policy public heads exist, so run a fresh post-publication audit"
        else:
            status = "manual"
            reason = "unclassified gate"

        gate_statuses.append(
            {
                "gate_id": gid,
                "stage": gate["stage"],
                "status": status,
                "reason": reason,
                "required_surfaces": gate["required_surfaces"],
            }
        )

    counts = Counter(g["status"] for g in gate_statuses)
    return {
        "version": 3,
        "status": "pass" if not any(g["status"] == "fail" for g in gate_statuses) else "fail",
        "generated_for_revision": manifest["revision"],
        "checked_bundle": manifest["bundle"],
        "bundle": manifest["bundle"],
        "publication_authorized": False,
        "default_rule": gates["fail_closed_rule"],
        "gates": gate_statuses,
        "summary": dict(sorted(counts.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-report", default="reports/lifecycle_gate_status.json")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    data = build(root)
    out = root / args.write_report
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(data, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
