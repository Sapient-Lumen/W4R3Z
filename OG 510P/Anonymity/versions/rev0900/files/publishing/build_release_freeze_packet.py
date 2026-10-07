#!/usr/bin/env python3
"""Materialize a non-public freeze packet for the selected next-release target.

The packet is deliberately not a published entry.  It copies the selected source
into release_queue/freeze_packets/, binds it to the evidence pack, compile
witness, queue note, and freeze plan, and leaves publication_authorized=false.

Current hardening: the packet embeds a source-bound compile-witness snapshot
inside the packet.  A later publication receipt can therefore point at immutable
per-packet evidence instead of relying only on the singleton
release_queue/FREEZE_COMPILE_WITNESS.json surface, which may be regenerated when
the freeze lane advances to a different source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
from typing import Any


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: pathlib.Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def slugify(text: str) -> str:
    text = re.sub(r"^Anonymity:\s*", "", text, flags=re.I)
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "release-target"


def existing_packet_id_for_source(root: pathlib.Path, source: str) -> str | None:
    registry_path = root / "release_queue" / "FREEZE_PACKET_REGISTRY.json"
    if not registry_path.exists():
        return None
    try:
        registry = load_json(registry_path)
    except Exception:
        return None
    for entry in registry.get("entries", []):
        if isinstance(entry, dict) and entry.get("source_tex") == source and entry.get("freeze_packet_id"):
            return str(entry["freeze_packet_id"])
    return None




def registry_manifest_exists(root: pathlib.Path, entry: dict[str, Any]) -> bool:
    manifest = entry.get("manifest") if isinstance(entry, dict) else None
    if not manifest:
        return False
    try:
        path = (root / str(manifest)).resolve()
        path.relative_to(root)
    except Exception:
        return False
    return path.exists()


def preserved_registry_entries(root: pathlib.Path, current_source: str) -> list[dict[str, Any]]:
    registry_path = root / "release_queue" / "FREEZE_PACKET_REGISTRY.json"
    if not registry_path.exists():
        return []
    try:
        registry = load_json(registry_path)
    except Exception:
        return []
    preserved: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in registry.get("entries", []):
        if not isinstance(entry, dict):
            continue
        manifest = str(entry.get("manifest", ""))
        if not manifest or manifest in seen:
            continue
        if entry.get("source_tex") == current_source:
            continue
        if not registry_manifest_exists(root, entry):
            continue
        preserved.append(dict(entry))
        seen.add(manifest)
    return preserved

def rel_inside(root: pathlib.Path, rel: str) -> pathlib.Path:
    path = (root / rel).resolve()
    path.relative_to(root)
    return path


def selected_evidence_manifest(plan: dict[str, Any], integrity: dict[str, Any]) -> str:
    gate = plan.get("evidence_gate", {}) if isinstance(plan.get("evidence_gate"), dict) else {}
    manifest = str(gate.get("evidence_pack_manifest", ""))
    if manifest:
        return manifest
    entries = integrity.get("entries", []) if isinstance(integrity.get("entries"), list) else []
    selected = (plan.get("selected_source") or {}).get("source_tex") if isinstance(plan.get("selected_source"), dict) else ""
    for entry in entries:
        if isinstance(entry, dict) and entry.get("source_tex") == selected and entry.get("manifest"):
            return str(entry["manifest"])
    return ""


def compile_pdf_sha256(compile_report: dict[str, Any], witness: dict[str, Any]) -> str | None:
    comp = compile_report.get("compile") if isinstance(compile_report.get("compile"), dict) else {}
    if comp.get("output_pdf_sha256"):
        return str(comp.get("output_pdf_sha256"))
    details = witness.get("preflight_report", {}).get("details", {}) if isinstance(witness.get("preflight_report"), dict) else {}
    comp2 = details.get("compile", {}) if isinstance(details.get("compile"), dict) else {}
    return str(comp2.get("output_pdf_sha256")) if comp2.get("output_pdf_sha256") else None


def build(root: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    plan = load_json(root / "release_queue" / "NEXT_RELEASE_FREEZE_PLAN.json")
    evidence_integrity = load_json(root / "reports" / "evidence_pack_integrity.json")
    compile_report = load_json(root / "reports" / "freeze_compile_witness.json")
    compile_witness_live_rel = "release_queue/FREEZE_COMPILE_WITNESS.json"
    compile_witness_live_path = root / compile_witness_live_rel
    compile_witness_live = load_json(compile_witness_live_path)

    selected = plan.get("selected_source") if isinstance(plan.get("selected_source"), dict) else {}
    source = str(selected.get("source_tex", ""))
    title = str(selected.get("title", ""))
    source_sha = str(selected.get("source_sha256", ""))
    decision_note = str(selected.get("decision_note", ""))
    prospective_target = str(selected.get("prospective_target", ""))
    if not source or not title or not source_sha:
        raise RuntimeError("freeze plan has no selected source")
    if plan.get("publication_authorized") is not False:
        raise RuntimeError("freeze plan must be non-authorizing")
    if evidence_integrity.get("status") != "pass":
        raise RuntimeError("evidence-pack integrity must pass before building freeze packet")

    evidence_manifest_rel = selected_evidence_manifest(plan, evidence_integrity)
    if not evidence_manifest_rel:
        registry_path = root / "release_queue" / "FREEZE_PACKET_REGISTRY.json"
        registry = load_json(registry_path) if registry_path.exists() else {"version": 3, "entries": []}
        registry["generated_for_revision"] = release["revision"]
        registry["checked_bundle"] = release["bundle"]
        registry["publication_authorized"] = False
        registry["automatic_packet_opening"] = False
        registry["lane_opening_policy"] = "A queue recommendation without an explicitly attached evidence pack remains pending; rebuild does not materialize a new freeze packet."
        write_json(registry_path, registry)
        return {
            "status": "pass",
            "action": "no_packet_built_pending_evidence_attachment",
            "source_tex": source,
            "source_sha256": source_sha,
            "compile_gate_status": str(compile_report.get("compile_gate_status", "pending")),
        }

    if compile_report.get("status") != "pass":
        raise RuntimeError("compile witness integrity surface must pass before building freeze packet")
    if compile_report.get("selected_source") != source or compile_report.get("selected_source_sha256") != source_sha:
        raise RuntimeError("compile witness report does not match freeze-plan selected source")
    if compile_witness_live.get("source_tex") != source or compile_witness_live.get("source_sha256") != source_sha:
        raise RuntimeError("live compile witness is not bound to selected source")
    if compile_witness_live.get("generated_for_revision") != release["revision"] or compile_witness_live.get("checked_bundle") != release["bundle"]:
        raise RuntimeError("live compile witness is stale for this release")
    compile_gate_status = str(compile_report.get("compile_gate_status", compile_witness_live.get("compile_gate_status", "pass")))

    source_path = rel_inside(root, source)
    actual_source_sha = sha256_file(source_path)
    if actual_source_sha != source_sha:
        raise RuntimeError(f"selected source hash drift: {source_sha} != {actual_source_sha}")

    evidence_manifest_path = rel_inside(root, evidence_manifest_rel)
    evidence_manifest = load_json(evidence_manifest_path)
    evidence_pack_id = str(evidence_manifest.get("evidence_pack_id", ""))
    if evidence_manifest.get("source_tex") != source or evidence_manifest.get("source_sha256") != source_sha:
        raise RuntimeError("evidence manifest is not bound to selected source")

    freeze_date = str(plan.get("freeze_date") or release.get("timestamp", "YYYY.MM.DD")[:10])
    packet_id = existing_packet_id_for_source(root, source) or evidence_pack_id or f"{freeze_date}-{slugify(title)}"
    packet_rel = f"release_queue/freeze_packets/{packet_id}"
    packet_dir = root / packet_rel
    packet_dir.mkdir(parents=True, exist_ok=True)

    frozen_source_rel = f"{packet_rel}/FROZEN_SOURCE.tex"
    frozen_source_path = root / frozen_source_rel
    shutil.copy2(source_path, frozen_source_path)

    compile_snapshot_rel = f"{packet_rel}/FREEZE_COMPILE_WITNESS.snapshot.json"
    compile_snapshot_path = root / compile_snapshot_rel
    shutil.copy2(compile_witness_live_path, compile_snapshot_path)
    compile_snapshot_sha = sha256_file(compile_snapshot_path)
    compile_live_sha = sha256_file(compile_witness_live_path)
    if compile_snapshot_sha != compile_live_sha:
        raise RuntimeError("compile witness snapshot did not preserve live witness digest")

    checklist = f"""# Pre-publication checklist: {title}

- Freeze packet id: `{packet_id}`
- Source: `{source}`
- Source SHA-256: `{source_sha}`
- Prospective target: `{prospective_target}`
- Publication authorized: `false`

Resolved gates:

- queue binding
- source hash binding
- direct static preflight
- evidence-pack resolution
- frozen-source copy bound to the same source hash
- source-bound compile-witness snapshot embedded in the packet

Compile gate status:

- `{compile_gate_status}`

Still required before a public move:

- a current deterministic clean LaTeX compile witness when the compile gate is not `pass`
- an explicit publication decision note with `Publication action: publish`
- execution through the guarded publication helper
- post-publication metadata, public-surface, provenance, and manifest rebuild
"""
    (packet_dir / "PREPUBLICATION_CHECKLIST.md").write_text(checklist, encoding="utf-8")

    readme = f"""# Freeze packet: {title}

This is a non-public, source-bound release freeze packet.  It is designed to make
the next publication step auditable without itself creating a public citation
head.

- Source: `{source}`
- Source SHA-256: `{source_sha}`
- Evidence manifest: `{evidence_manifest_rel}`
- Compile witness live path: `{compile_witness_live_rel}`
- Compile witness packet snapshot: `{compile_snapshot_rel}`
- Compile gate status: `{compile_gate_status}`
- Prospective target: `{prospective_target}`
- Publication authorized: `false`

The packet may be used only with a later explicit publication decision and the
guarded publication helper.  Until that happens, `published/` remains unchanged.
"""
    (packet_dir / "README.md").write_text(readme, encoding="utf-8")

    packet_paths = [
        ("README.md", "freeze_packet_readme"),
        ("FROZEN_SOURCE.tex", "frozen_source_tex"),
        ("PREPUBLICATION_CHECKLIST.md", "prepublication_checklist"),
        ("FREEZE_COMPILE_WITNESS.snapshot.json", "source_bound_compile_witness_snapshot"),
    ]
    gates = {row.get("name"): row.get("status") for row in plan.get("gates", []) if isinstance(row, dict)}
    manifest = {
        "version": 2,
        "freeze_packet_id": packet_id,
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "status": "materialized_non_public_freeze_packet",
        "source_tex": source,
        "source_sha256": source_sha,
        "title": title,
        "decision_note": decision_note,
        "prospective_target": prospective_target,
        "freeze_packet_root": packet_rel,
        "frozen_source_path": frozen_source_rel,
        "frozen_source_sha256": sha256_file(frozen_source_path),
        "evidence_pack_manifest": evidence_manifest_rel,
        "evidence_pack_manifest_sha256": sha256_file(evidence_manifest_path),
        "compile_witness": compile_witness_live_rel,
        "compile_witness_sha256_at_freeze": compile_live_sha,
        "compile_witness_snapshot": compile_snapshot_rel,
        "compile_witness_snapshot_sha256": compile_snapshot_sha,
        "compile_witness_snapshot_source_tex": compile_witness_live.get("source_tex"),
        "compile_witness_snapshot_source_sha256": compile_witness_live.get("source_sha256"),
        "compile_witness_snapshot_revision": compile_witness_live.get("generated_for_revision"),
        "compile_witness_snapshot_bundle": compile_witness_live.get("checked_bundle"),
        "compile_witness_snapshot_toolchain_version_line": (compile_witness_live.get("toolchain", {}) if isinstance(compile_witness_live.get("toolchain"), dict) else {}).get("version_line", ""),
        "compile_witness_snapshot_toolchain_version_output_sha256": (compile_witness_live.get("toolchain", {}) if isinstance(compile_witness_live.get("toolchain"), dict) else {}).get("version_output_sha256", ""),
        "compile_gate_status": compile_gate_status,
        "compile_output_pdf_sha256": compile_pdf_sha256(compile_report, compile_witness_live),
        "freeze_plan": "release_queue/NEXT_RELEASE_FREEZE_PLAN.json",
        "freeze_plan_sha256": sha256_file(root / "release_queue" / "NEXT_RELEASE_FREEZE_PLAN.json"),
        "freeze_plan_gate_snapshot": gates,
        "packet_paths": [
            {"path": f"{packet_rel}/{name}", "role": role, "sha256": sha256_file(packet_dir / name)}
            for name, role in packet_paths
        ],
        "remaining_publication_gates": (["current_deterministic_clean_latex_compile_witness"] if compile_gate_status != "pass" else []) + [
            "explicit_publication_decision",
            "guarded_create_published_entry_execution",
            "post_publication_metadata_and_provenance_refresh",
        ],
        "non_authorization_notice": "This packet freezes source evidence for review only; it does not publish the paper or authorize publication.",
    }
    write_json(packet_dir / "FREEZE_PACKET_MANIFEST.json", manifest)

    current_entry = {
        "freeze_packet_id": packet_id,
        "status": "materialized_non_public_freeze_packet",
        "source_tex": source,
        "source_sha256": source_sha,
        "title": title,
        "decision_note": decision_note,
        "prospective_target": prospective_target,
        "manifest": f"{packet_rel}/FREEZE_PACKET_MANIFEST.json",
        "evidence_pack_manifest": evidence_manifest_rel,
        "compile_witness": compile_witness_live_rel,
        "compile_witness_sha256_at_freeze": compile_live_sha,
        "compile_witness_snapshot": compile_snapshot_rel,
        "compile_witness_snapshot_sha256": compile_snapshot_sha,
        "compile_witness_snapshot_toolchain_version_output_sha256": (compile_witness_live.get("toolchain", {}) if isinstance(compile_witness_live.get("toolchain"), dict) else {}).get("version_output_sha256", ""),
        "publication_scope": "staged_freeze_packet_only",
    }
    registry = {
        "version": 3,
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "entries": preserved_registry_entries(root, source) + [current_entry],
        "preservation_note": "Registry rebuilds preserve earlier source-bound freeze packets so publication receipts do not become unregistered when the next-release lane advances.",
        "fail_closed_rule": "Freeze packets are non-public staging artifacts. Publication still requires a separate written decision and a guarded published/ copy.",
    }
    write_json(root / "release_queue" / "FREEZE_PACKET_REGISTRY.json", registry)
    return {"status": "pass", "freeze_packet_id": packet_id, "manifest": current_entry["manifest"], "compile_witness_snapshot": compile_snapshot_rel, "source_tex": source, "source_sha256": source_sha}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = build(root)
    print(json.dumps(report, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
