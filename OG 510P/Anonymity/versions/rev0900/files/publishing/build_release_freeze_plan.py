#!/usr/bin/env python3
"""Build a non-authorizing dry-run freeze plan for the next release target.

The plan binds the queue-level recommendation to a direct source hash and static
preflight result, then leaves publication-blocking manual gates explicit.  It
writes JSON and Markdown surfaces under release_queue/ but does not copy sources
or modify published/.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_evidence_pack_policy as ep  # noqa: E402
import check_freeze_compile_witness as fcw  # noqa: E402
import check_release_readiness as rr  # noqa: E402
import check_external_hostile_review_packet as ehrp  # noqa: E402
import release_preflight as rp  # noqa: E402
import publication_target as pt  # noqa: E402

PREFIX = "Anonymity: "


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def freeze_date_from_manifest(release_manifest: dict[str, Any]) -> str:
    # RELEASE_MANIFEST timestamp is YYYY.MM.DD.HH.MM.
    parts = str(release_manifest.get("timestamp", "YYYY.MM.DD")).split(".")
    return ".".join(parts[:3]) if len(parts) >= 3 else "YYYY.MM.DD"


def source_family(rel: str) -> str:
    parts = rel.split("/")
    if len(parts) >= 2 and parts[0] == "series":
        return parts[1]
    return "unknown"


def direct_preflight_snapshot(root: pathlib.Path, item: dict[str, Any], freeze_date: str) -> dict[str, Any]:
    rel = str(item.get("source_tex", ""))
    src = root / rel
    title = str(item.get("title", ""))
    short_title = title[len(PREFIX):] if title.startswith(PREFIX) else title
    problems: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {}
    try:
        target = pt.portable_published_path(freeze_date, title)
        prospective_published_name = pt.portable_published_dirname(freeze_date, title)
    except ValueError as exc:
        target = "published/__invalid_publication_target__"
        prospective_published_name = "__invalid_publication_target__"
        problems.append(str(exc))

    if not rel or not src.exists():
        problems.append(f"source missing: {rel}")
        text = ""
    else:
        text = src.read_text(encoding="utf-8", errors="replace")
        details["source_sha256"] = rp.sha256_file(src)
        details["source_bytes"] = src.stat().st_size
        details["queue_records"] = rp.queue_records_for_source(root, rel)
        if not rp.source_in_published_ready(root, rel):
            problems.append("source is not exactly bound to published_ready")
        closure = rp.citation_and_reference_closure(src, text)
        placeholders = rp.placeholder_findings(text)
        malformed = rp.malformed_bibliography_commands(text)
        artifact_governance = rp.source_needs_evidence_review(text)
        details["citation_reference_closure"] = closure
        details["placeholder_findings"] = placeholders
        details["malformed_bibliography_commands"] = malformed
        details["artifact_governance_likely"] = artifact_governance
        if closure["missing_bibliography_files"]:
            problems.append(f"missing bibliography files: {closure['missing_bibliography_files']}")
        if closure["undefined_citations"]:
            problems.append(f"undefined citation keys: {closure['undefined_citations'][:30]}")
        if closure["undefined_references"]:
            problems.append(f"undefined reference keys: {closure['undefined_references'][:30]}")
        if placeholders:
            problems.append(f"placeholder markers present: {len(placeholders)}")
        if malformed:
            problems.append(f"malformed bibliography command fragments present: {len(malformed)}")
        if artifact_governance:
            warnings.append("artifact-governance language detected; evidence pack attachment or explicit waiver is a freeze gate")

    return {
        "status": "pass" if not problems else "fail",
        "prospective_published_name": prospective_published_name,
        "prospective_short_title": short_title,
        "source": rel,
        "target": target,
        "warnings": warnings,
        "problems": problems,
        "details": details,
        "fail_closed_rule": "A failed static preflight blocks freeze. A passed static preflight still does not authorize publication until manual gates and an explicit decision are closed.",
    }


def gate(name: str, status: str, detail: str, blocking: bool = True) -> dict[str, Any]:
    return {"name": name, "status": status, "blocking": blocking, "detail": detail}


def hostile_review_snapshot(root: pathlib.Path, evidence_gate: dict[str, Any]) -> dict[str, Any]:
    """Read hostile arithmetic vectors from the attached evidence card.

    The selected next-release lane is allowed to have internal break vectors, but
    publication remains blocked until an external reviewer/countersigner has
    tried to break the same arithmetic and threat-transfer rows.
    """
    manifest_rel = str(evidence_gate.get("evidence_pack_manifest", ""))
    if not manifest_rel:
        return {
            "status": "missing_evidence_manifest",
            "gate_status": "pending",
            "detail": "No attached evidence-pack manifest, so hostile arithmetic vectors cannot be read.",
            "publication_blocking_until_external_review": True,
        }
    manifest_path = root / manifest_rel
    if not manifest_path.exists():
        return {
            "status": "missing_evidence_manifest",
            "gate_status": "fail",
            "detail": f"Evidence-pack manifest is declared but missing: {manifest_rel}",
            "publication_blocking_until_external_review": True,
        }
    try:
        manifest = load_json(manifest_path)
        card_rel = str(manifest.get("card_path", ""))
        card_type = str(manifest.get("card_type", ""))
        card = load_json(root / card_rel) if card_rel else {}
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "hostile_review_unreadable",
            "gate_status": "fail",
            "detail": f"Could not read hostile-review card: {exc}",
            "publication_blocking_until_external_review": True,
        }
    values = card.get("card_values", {}) if isinstance(card.get("card_values"), dict) else {}
    hostile = values.get("hostile_review", {}) if isinstance(values.get("hostile_review"), dict) else {}
    vectors = hostile.get("vectors", []) if isinstance(hostile.get("vectors"), list) else []
    failed_vectors = [row for row in vectors if isinstance(row, dict) and row.get("status") != "pass"]
    internal_ok = hostile.get("status") == "pass" and bool(vectors) and not failed_vectors
    external_missing = hostile.get("external_reviewer_signoff") == "missing"
    blocking = hostile.get("blocking_publication_until_external_review") is True
    if internal_ok and external_missing and blocking:
        status = "internal_vectors_pass_external_review_pending"
        gate_status = "pass"
        detail = f"{card_type}: {len(vectors)} internal hostile arithmetic vectors pass; external reviewer signoff remains missing and publication-blocking."
    elif internal_ok:
        status = "internal_vectors_pass_external_boundary_ambiguous"
        gate_status = "fail"
        detail = f"{card_type}: internal vectors pass but the external-review boundary is not publication-blocking."
    elif hostile:
        status = "internal_vectors_fail"
        gate_status = "fail"
        detail = f"{card_type}: hostile vectors failed or are incomplete; failed_vectors={len(failed_vectors)} total_vectors={len(vectors)}."
    else:
        status = "hostile_vectors_missing"
        gate_status = "pending"
        detail = f"{card_type}: hostile arithmetic vectors are not present in the evidence card."
    return {
        "status": status,
        "gate_status": gate_status,
        "detail": detail,
        "card_path": card_rel,
        "card_type": card_type,
        "vector_count": len(vectors),
        "failed_vector_count": len(failed_vectors),
        "failed_vectors": failed_vectors[:5],
        "external_reviewer_signoff": hostile.get("external_reviewer_signoff", "missing"),
        "publication_blocking_until_external_review": blocking,
    }


def build_plan(root: pathlib.Path) -> dict[str, Any]:
    release_manifest = load_json(root / "RELEASE_MANIFEST.json")
    readiness = rr.check(root)
    evidence = ep.check(root)
    compile_witness = fcw.check(root)
    recommendation = readiness.get("next_release_recommendation", {}) if isinstance(readiness.get("next_release_recommendation"), dict) else {}
    freeze_date = freeze_date_from_manifest(release_manifest)

    if recommendation.get("status") != "static_pass_candidate_available":
        return {
            "status": "no_static_pass_candidate",
            "generated_for_revision": release_manifest["revision"],
            "checked_bundle": release_manifest["bundle"],
            "publication_authorized": False,
            "recommendation": recommendation,
            "selected_source": None,
            "gates": [gate("published_ready_static_candidate", "fail", "No static-pass Published-ready recommendation was available.")],
            "fail_closed_rule": "No source should be frozen until the queue-level recommendation and direct preflight pass.",
        }

    source = str(recommendation.get("source_tex", ""))
    item = next((row for row in readiness.get("items", []) if row.get("source_tex") == source), {})
    direct = direct_preflight_snapshot(root, item, freeze_date)
    evidence_gate = evidence.get("next_release_evidence_gate", {}) if isinstance(evidence.get("next_release_evidence_gate"), dict) else {}
    details = direct.get("details", {}) if isinstance(direct.get("details"), dict) else {}
    queue_records = details.get("queue_records", []) if isinstance(details.get("queue_records"), list) else []
    queue_binding_ok = len(queue_records) == 1 and queue_records[0].get("queue_state") == "published_ready"
    source_hash_matches = details.get("source_sha256") == recommendation.get("source_sha256")
    direct_ok = direct.get("status") == "pass"
    evidence_pending = bool(evidence_gate.get("publication_blocking_until_resolved"))
    compile_status = compile_witness.get("status")
    compile_summary = compile_witness.get("summary", {}) if isinstance(compile_witness.get("summary"), dict) else {}
    witness_present = bool(compile_summary.get("witness_present"))
    compile_source_bound = compile_status == "pass" and compile_witness.get("selected_source") == source and compile_witness.get("selected_source_sha256") == recommendation.get("source_sha256")
    report_gate_status = str(compile_witness.get("compile_gate_status", "missing"))
    if compile_source_bound and report_gate_status == "pass":
        compile_detail = "source-bound deterministic clean final LaTeX compile witness present; pdf_sha256=" + str(compile_witness.get("compile", {}).get("output_pdf_sha256", ""))
        compile_gate_status = "pass"
    elif compile_source_bound and report_gate_status.startswith("pending"):
        compile_detail = "source-bound compile evidence exists, but the current publication compile gate remains pending: " + report_gate_status
        compile_gate_status = "pending"
    elif witness_present and compile_status == "pass":
        compile_detail = "compile witness surface is present but not bound to the selected source or gate; refresh before freeze"
        compile_gate_status = "fail"
    elif witness_present:
        compile_detail = "compile witness is present but failed integrity; repair witness before freeze"
        compile_gate_status = "fail"
    else:
        compile_detail = "No TeX compile witness is present; run release_preflight.py --compile in a TeX-equipped environment before freeze."
        compile_gate_status = "pending"

    hostile_review = hostile_review_snapshot(root, evidence_gate)
    hostile_gate_status = str(hostile_review.get("gate_status", "pending"))
    external_packet = ehrp.check(root)
    packet_summary = external_packet.get("summary", {}) if isinstance(external_packet.get("summary"), dict) else {}
    packet_ready = external_packet.get("status") == "pass" and packet_summary.get("external_signoff_status") == "missing"

    gates = [
        gate("queue_binding", "pass" if queue_binding_ok else "fail", f"exact published_ready bindings={len(queue_records)} source={source}"),
        gate("source_hash_binding", "pass" if source_hash_matches else "fail", f"recommendation={recommendation.get('source_sha256')} direct={details.get('source_sha256')}"),
        gate("direct_static_preflight", "pass" if direct_ok else "fail", f"problems={len(direct.get('problems', []))} warnings={len(direct.get('warnings', []))}"),
        gate("evidence_pack_resolution", "pending" if evidence_pending else "pass", str(evidence_gate.get("required_resolution", "not_required_by_heuristic")) + (f"; manifest={evidence_gate.get('evidence_pack_manifest')}" if evidence_gate.get("evidence_pack_manifest") else "")),
        gate("internal_hostile_arithmetic_vectors", hostile_gate_status if hostile_gate_status in {"pass", "pending", "fail"} else "pending", str(hostile_review.get("detail", "hostile arithmetic vector status unavailable"))),
        gate("external_hostile_review_packet_ready", "pass" if packet_ready else "fail", f"packet={external_packet.get('packet_json', 'release_queue/EXTERNAL_HOSTILE_REVIEW_PACKET.json')} status={external_packet.get('status')} tasks={packet_summary.get('review_tasks')} signoff={packet_summary.get('external_signoff_status')}; readiness is non-authorizing"),
        gate("external_hostile_reviewer_signoff", "pending", "Publication remains blocked until a named external/adversarial review or countersignature tries the State/MUCC arithmetic and threat-transfer rows; internal vectors and a ready packet are not enough."),
        gate("manual_clean_latex_compile", compile_gate_status, compile_detail),
        gate("explicit_publication_decision", "pending", "A new release_queue/decisions/* publication decision must name the source hash, evidence resolution, hostile-review state, compile witness, and target."),
        gate("metadata_and_provenance_refresh", "pending", "After any freeze, refresh CITATION/RO-Crate/provenance/manifest surfaces before packaging."),
    ]

    hard_fail = any(g["status"] == "fail" for g in gates)
    pending_blocking = any(g["status"] == "pending" and g.get("blocking") for g in gates)
    status = "blocked" if hard_fail else ("dry_run_pass_pending_manual_gates" if pending_blocking else "ready_for_explicit_publication_decision")

    return {
        "status": status,
        "generated_for_revision": release_manifest["revision"],
        "checked_bundle": release_manifest["bundle"],
        "publication_authorized": False,
        "freeze_date": freeze_date,
        "recommendation": recommendation,
        "selected_source": {
            "source_tex": source,
            "source_family": source_family(source),
            "title": item.get("title", recommendation.get("title")),
            "decision_note": item.get("decision_note", recommendation.get("decision_note")),
            "source_sha256": details.get("source_sha256"),
            "prospective_target": direct.get("target"),
        },
        "direct_preflight": direct,
        "evidence_gate": evidence_gate,
        "hostile_review": hostile_review,
        "external_hostile_review_packet": {
            "status": external_packet.get("status"),
            "packet_json": external_packet.get("packet_json"),
            "packet_md": external_packet.get("packet_md"),
            "packet_sha256": external_packet.get("packet_sha256"),
            "summary": packet_summary,
        },
        "compile_witness": {
            "status": compile_witness.get("status"),
            "compile_gate_status": compile_witness.get("compile_gate_status"),
            "publication_blocking_until_refreshed": compile_witness.get("publication_blocking_until_refreshed"),
            "witness_path": compile_witness.get("witness_path"),
            "source_tex": compile_witness.get("selected_source"),
            "source_sha256": compile_witness.get("selected_source_sha256"),
            "output_pdf_sha256": compile_witness.get("compile", {}).get("output_pdf_sha256") if isinstance(compile_witness.get("compile"), dict) else None,
            "final_warning_count": compile_witness.get("compile", {}).get("final_warning_count") if isinstance(compile_witness.get("compile"), dict) else None,
        },
        "gates": gates,
        "summary": {
            "gate_count": len(gates),
            "passed_gates": sum(1 for g in gates if g["status"] == "pass"),
            "pending_gates": sum(1 for g in gates if g["status"] == "pending"),
            "failed_gates": sum(1 for g in gates if g["status"] == "fail"),
        },
        "fail_closed_rule": "This plan is a dry run only. Publication remains unauthorized until every blocking gate passes and a separate written publication decision is recorded.",
    }


def render_md(plan: dict[str, Any]) -> str:
    selected = plan.get("selected_source") or {}
    lines = [
        "# Next release freeze plan",
        "",
        f"- Generated for revision: `{plan.get('generated_for_revision')}`",
        f"- Status: `{plan.get('status')}`",
        f"- Publication authorized: `{str(plan.get('publication_authorized')).lower()}`",
        "",
    ]
    if selected:
        evidence_gate = plan.get("evidence_gate") or {}
        compile_witness = plan.get("compile_witness") or {}
        hostile_review = plan.get("hostile_review") or {}
        external_packet = plan.get("external_hostile_review_packet") or {}
        packet_summary = external_packet.get("summary") or {}
        lines.extend([
            "## Selected dry-run target",
            "",
            f"- Source: `{selected.get('source_tex')}`",
            f"- Source SHA-256: `{selected.get('source_sha256')}`",
            f"- Title: `{selected.get('title')}`",
            f"- Queue note: `{selected.get('decision_note')}`",
            f"- Prospective target: `{selected.get('prospective_target')}`",
            f"- Evidence gate: `{evidence_gate.get('status')}`",
            f"- Evidence manifest: `{evidence_gate.get('evidence_pack_manifest', '')}`",
            f"- Hostile arithmetic vectors: `{hostile_review.get('status', '')}`; vectors `{hostile_review.get('vector_count', '')}`; card `{hostile_review.get('card_path', '')}`",
            f"- External hostile-review packet: `{external_packet.get('status', '')}`; tasks `{packet_summary.get('review_tasks', '')}`; signoff `{packet_summary.get('external_signoff_status', '')}`",
            f"- External hostile-review signoff: `{hostile_review.get('external_reviewer_signoff', 'missing')}`",
            f"- Compile witness: `{compile_witness.get('status')}` / gate `{compile_witness.get('compile_gate_status', '')}`",
            f"- Compile output PDF SHA-256: `{compile_witness.get('output_pdf_sha256', '')}`",
            "",
        ])
    lines.extend(["## Blocking gates", ""])
    for gate_row in plan.get("gates", []):
        lines.append(f"- `{gate_row.get('name')}`: **{gate_row.get('status')}** — {gate_row.get('detail')}")
    lines.extend([
        "",
        "## Rule",
        "",
        plan.get("fail_closed_rule", "No publication without a separate written decision."),
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write-json", default="release_queue/NEXT_RELEASE_FREEZE_PLAN.json")
    parser.add_argument("--write-md", default="release_queue/NEXT_RELEASE_FREEZE_PLAN.md")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    plan = build_plan(root)
    text = json.dumps(plan, indent=2) + "\n"
    if args.write_json:
        out = root / args.write_json
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    if args.write_md:
        out_md = root / args.write_md
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_md(plan), encoding="utf-8")
    sys.stdout.write(text)
    return 0 if plan.get("status") != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
