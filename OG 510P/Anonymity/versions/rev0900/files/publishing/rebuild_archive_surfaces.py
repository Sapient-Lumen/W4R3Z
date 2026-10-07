#!/usr/bin/env python3
"""Rebuild compact archive surfaces to a manifest/report fixed point.

The expensive source/queue checks run once. Manifest-dependent reports then run
in a small fixed-point loop so MANIFEST.sha256 and its verification reports are
self-consistent without repeatedly regenerating every source audit.

The runner is phaseable for constrained cloudtainers: revision bindings, manifest
refresh, first-pass surfaces, and tail fixed-point surfaces can be executed
separately while preserving the all-in-one rebuild path. Helper scripts are run
as isolated subprocess groups so an interrupted or timed-out rebuild cannot
strand TeX/preflight children or leak module state across checks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import signal
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace
from typing import Iterable

SCRIPT_TIMEOUT_SECONDS = 120
SITE_REQUIRED_SCRIPTS = {
    "publishing/check_surface_schemas.py",
    "publishing/check_schema_catalog_integrity.py",
    "publishing/check_json_surface_catalog.py",
    "publishing/check_python_entrypoint_smoke.py",
}

FIRST_PASS_SCRIPTS = [
    ("publishing/render_transfer_sources.py", "--root", "."),
    ("publishing/build_decision_index.py", "--root", "."),
    ("publishing/build_review_inventory.py", "--root", "."),
    ("publishing/render_queue_surfaces.py", "--root", "."),
    ("publishing/check_review_inventory_coverage.py", "--root", ".", "--write-report", "reports/review_inventory_coverage.json"),
    ("publishing/check_review_inventory_integrity.py", "--root", ".", "--write-report", "reports/review_inventory_integrity.json"),
    ("publishing/check_operator_command_hygiene.py", "--root", ".", "--write-report", "reports/operator_command_hygiene.json"),
    ("publishing/build_tooling_inventory.py", "--root", "."),
    ("publishing/check_tooling_inventory_integrity.py", "--root", ".", "--write-report", "reports/tooling_inventory_integrity.json"),
    ("publishing/check_revision_lineage.py", "--root", ".", "--write-report", "reports/revision_lineage.json"),
    ("publishing/render_archive_invariants.py", "--root", "."),
    ("publishing/check_archive_index_integrity.py", "--root", ".", "--write-report", "reports/archive_index_integrity.json"),
    ("publishing/render_assurance_artifacts.py", "--root", "."),
    ("publishing/check_publication_decision_template.py", "--root", ".", "--write-report", "reports/publication_decision_template.json"),
    ("publishing/check_publication_decision_authorization.py", "--root", ".", "--write-report", "reports/publication_decision_authorization.json"),
    ("publishing/check_citation_closure.py", "--root", ".", "--write-report", "reports/citation_closure_audit.json"),
    ("publishing/check_release_readiness.py", "--root", ".", "--write-report", "reports/release_readiness_audit.json"),
    ("publishing/check_queue_note_source_binding.py", "--root", ".", "--write-report", "reports/queue_note_source_binding.json"),
    ("publishing/build_release_evidence_pack.py", "--root", "."),
    ("publishing/check_evidence_pack_integrity.py", "--root", ".", "--write-report", "reports/evidence_pack_integrity.json"),
    ("publishing/check_hostile_review_vectors.py", "--root", "."),
    ("publishing/check_threat_transfer_matrix.py", "--root", "."),
    ("publishing/build_external_hostile_review_packet.py", "--root", "."),
    ("publishing/check_external_hostile_review_packet.py", "--root", "."),
    ("publishing/check_freeze_toolchain.py", "--root", ".", "--write-report", "reports/freeze_toolchain.json"),
    ("publishing/build_freeze_compile_witness.py", "--root", "."),
    ("publishing/check_freeze_compile_witness.py", "--root", ".", "--write-report", "reports/freeze_compile_witness.json"),
    ("publishing/check_evidence_pack_policy.py", "--root", ".", "--write-report", "reports/evidence_pack_audit.json"),
    ("publishing/build_release_freeze_plan.py", "--root", ".", "--write-json", "release_queue/NEXT_RELEASE_FREEZE_PLAN.json", "--write-md", "release_queue/NEXT_RELEASE_FREEZE_PLAN.md"),
    ("publishing/build_release_freeze_packet.py", "--root", "."),
    ("publishing/check_freeze_packet_integrity.py", "--root", ".", "--write-report", "reports/freeze_packet_integrity.json"),
    ("publishing/check_publication_boundary.py", "--root", ".", "--write-report", "reports/publication_boundary.json"),
    ("publishing/check_publication_artifact_quarantine.py", "--root", ".", "--write-report", "reports/publication_artifact_quarantine.json"),
    ("publishing/check_support_manifest_integrity.py", "--root", ".", "--write-report", "reports/support_manifest_integrity.json"),
    ("publishing/check_worked_example_payload_pointers.py", "--root", "."),
    ("publishing/check_context_pack_budget.py", "--root", ".", "--write-report", "reports/context_pack_budget.json"),
    ("publishing/check_archive_budget.py", "--root", ".", "--write-report", "reports/archive_budget.json"),
    ("publishing/check_transfer_source_receipt.py", "--root", ".", "--write-report", "reports/transfer_source_receipt.json"),
    ("publishing/check_transient_surface.py", "--root", ".", "--write-report", "reports/transient_surface_audit.json"),
]

TAIL_SCRIPTS = [
    ("publishing/verify_manifest_sha256.py", "--root", ".", "--write-report", "reports/manifest_sha256_verification.json"),
    ("publishing/check_manifest_coverage.py", "--root", ".", "--write-report", "reports/manifest_coverage_audit.json"),
    ("publishing/check_manifest_canonicality.py", "--root", ".", "--write-report", "reports/manifest_canonicality.json"),
    ("publishing/check_path_portability.py", "--root", ".", "--write-report", "reports/path_portability.json"),
    ("publishing/check_archive_packaging_recipe.py", "--root", ".", "--write-report", "reports/archive_packaging_recipe.json"),
    ("publishing/check_archive_packaging_reproducibility.py", "--root", ".", "--write-report", "reports/archive_packaging_reproducibility.json"),
    ("publishing/check_archive_entry_security.py", "--root", ".", "--write-report", "reports/archive_entry_security.json"),
    ("publishing/build_publication_rehearsal.py", "--root", ".", "--write-report", "reports/publication_rehearsal.json"),
    ("publishing/build_publication_blockers.py", "--root", "."),
    ("publishing/check_publication_blockers.py", "--root", ".", "--write-report", "reports/publication_blockers.json"),
    ("publishing/check_publication_target_portability.py", "--root", ".", "--write-report", "reports/publication_target_portability.json"),
    ("publishing/check_freeze_warning_resolution.py", "--root", ".", "--write-report", "reports/freeze_warning_resolution.json"),
    ("publishing/check_toolchain_fingerprint.py", "--root", ".", "--write-report", "reports/toolchain_fingerprint.json"),
    ("publishing/check_bundle_identity_consistency.py", "--root", ".", "--write-report", "reports/bundle_identity_consistency.json"),
    ("publishing/check_control_surface_path_integrity.py", "--root", ".", "--write-report", "reports/control_surface_path_integrity.json"),
    ("publishing/check_duplicate_content_policy.py", "--root", ".", "--write-report", "reports/duplicate_content_policy.json"),
    ("publishing/check_release_guard_negative_controls.py", "--root", ".", "--write-report", "reports/release_guard_negative_controls.json"),
    ("publishing/check_rebuild_fixed_point_coverage.py", "--root", ".", "--write-report", "reports/rebuild_fixed_point_coverage.json"),
    ("publishing/check_context_pack_contract.py", "--root", ".", "--write-report", "reports/context_pack_contract.json"),
    ("publishing/build_lifecycle_gate_status.py", "--root", ".", "--write-report", "reports/lifecycle_gate_status.json"),
    ("publishing/check_content_leakage.py", "--root", ".", "--write-report", "reports/content_leakage.json"),
    ("publishing/check_tex_source_safety.py", "--root", ".", "--write-report", "reports/tex_source_safety.json"),
    ("publishing/check_secret_material_quarantine.py", "--root", ".", "--write-report", "reports/secret_material_quarantine.json"),
    ("publishing/check_makefile_target_integrity.py", "--root", ".", "--write-report", "reports/makefile_target_integrity.json"),
    ("publishing/check_python_entrypoint_smoke.py", "--root", ".", "--write-report", "reports/python_entrypoint_smoke.json"),
    ("publishing/check_surface_schemas.py", "--root", ".", "--write-report", "reports/surface_schema_validation.json"),
    ("publishing/check_schema_catalog_integrity.py", "--root", ".", "--write-report", "reports/schema_catalog_integrity.json"),
    ("publishing/check_report_schema_coverage.py", "--root", ".", "--write-report", "reports/report_schema_coverage.json"),
    ("publishing/check_json_surface_catalog.py", "--root", ".", "--write-report", "reports/json_surface_catalog.json"),
    ("publishing/check_decision_note_integrity.py", "--root", ".", "--write-report", "reports/decision_note_integrity.json"),
    ("publishing/check_json_key_integrity.py", "--root", ".", "--write-report", "reports/json_key_integrity.json"),
    ("publishing/check_text_surface_normalization.py", "--root", ".", "--write-report", "reports/text_surface_normalization.json"),
    ("publishing/check_unicode_control_hygiene.py", "--root", ".", "--write-report", "reports/unicode_control_hygiene.json"),
    ("publishing/check_tooling_static_integrity.py", "--root", ".", "--write-report", "reports/tooling_static_integrity.json"),
    ("publishing/check_report_warning_policy.py", "--root", ".", "--write-report", "reports/report_warning_policy.json"),
    ("publishing/check_assurance_catalog.py", "--root", ".", "--write-report", "reports/assurance_catalog_integrity.json"),
    ("publishing/check_report_identity_coverage.py", "--root", ".", "--write-report", "reports/report_identity_coverage.json"),
    ("publishing/check_archive_invariants.py", "--root", ".", "--write-report", "reports/archive_invariants.json"),
    ("publishing/check_invariant_catalog_integrity.py", "--root", ".", "--write-report", "reports/invariant_catalog_integrity.json"),
    ("publishing/check_archive_coherence.py", "--root", ".", "--write-report", "reports/archive_surface_coherence.json"),
    ("publishing/update_release_provenance.py", "--root", "."),
    ("publishing/check_research_metadata.py", "--root", ".", "--write-report", "reports/research_metadata_integrity.json"),
]

TAIL_TARGETS = [
    "MANIFEST.json",
    "MANIFEST.sha256",
    "reports/manifest_sha256_verification.json",
    "reports/manifest_coverage_audit.json",
    "reports/manifest_canonicality.json",
    "reports/path_portability.json",
    "reports/archive_packaging_recipe.json",
    "reports/archive_packaging_reproducibility.json",
    "reports/archive_entry_security.json",
    "reports/publication_rehearsal.json",
    "release_queue/PUBLICATION_BLOCKERS.md",
    "release_queue/PUBLICATION_BLOCKERS.json",
    "reports/publication_blockers.json",
    "reports/publication_target_portability.json",
    "reports/freeze_warning_resolution.json",
    "reports/toolchain_fingerprint.json",
    "reports/bundle_identity_consistency.json",
    "reports/control_surface_path_integrity.json",
    "reports/duplicate_content_policy.json",
    "reports/release_guard_negative_controls.json",
    "reports/rebuild_fixed_point_coverage.json",
    "reports/context_pack_contract.json",
    "reports/lifecycle_gate_status.json",
    "reports/content_leakage.json",
    "reports/tex_source_safety.json",
    "reports/secret_material_quarantine.json",
    "reports/makefile_target_integrity.json",
    "reports/surface_schema_validation.json",
    "reports/schema_catalog_integrity.json",
    "reports/report_schema_coverage.json",
    "reports/json_surface_catalog.json",
    "reports/decision_note_integrity.json",
    "reports/json_key_integrity.json",
    "reports/text_surface_normalization.json",
    "reports/unicode_control_hygiene.json",
    "reports/tooling_static_integrity.json",
    "reports/python_entrypoint_smoke.json",
    "reports/report_warning_policy.json",
    "reports/assurance_catalog_integrity.json",
    "release_provenance.intoto.jsonl",
    "reports/research_metadata_integrity.json",
    "reports/archive_invariants.json",
    "reports/invariant_catalog_integrity.json",
    "reports/archive_surface_coherence.json",
    "reports/report_identity_coverage.json",
]


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(root: pathlib.Path, rels: Iterable[str]) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for rel in rels:
        path = root / rel
        out[rel] = sha256_file(path) if path.exists() else None
    return out


def prune_python_bytecode(root: pathlib.Path) -> None:
    for d in sorted(root.rglob("__pycache__"), reverse=True):
        if d.is_dir():
            shutil.rmtree(d, ignore_errors=True)
    for p in root.rglob("*.py[co]"):
        if p.is_file():
            p.unlink(missing_ok=True)


def update_revision_bound_surfaces(root: pathlib.Path) -> None:
    revision = json.loads((root / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))["revision"]
    queue_path = root / "release_queue" / "QUEUE_INDEX.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    queue["generated_for_revision"] = revision
    latest_path = root / "release_queue" / "LATEST_DECISION.json"
    if latest_path.exists():
        latest = json.loads(latest_path.read_text(encoding="utf-8"))
        latest_note = str(latest.get("path", "")).strip()
        if latest_note:
            queue["latest_decision"] = latest_note
    queue_path.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")

    assurance_path = root / "ASSURANCE_ARTIFACTS.json"
    assurance = json.loads(assurance_path.read_text(encoding="utf-8"))
    assurance["generated_for_revision"] = revision
    assurance_path.write_text(json.dumps(assurance, indent=2) + "\n", encoding="utf-8")


def build_manifest_json(root: pathlib.Path) -> None:
    prune_python_bytecode(root)
    files = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
    (root / "MANIFEST.json").write_text(json.dumps({"files": files}, indent=2) + "\n", encoding="utf-8")


def build_manifest_sha256(root: pathlib.Path) -> None:
    prune_python_bytecode(root)
    files = sorted(
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and p.name != "MANIFEST.sha256"
    )
    lines = [f"{sha256_file(root / rel)}  {rel}" for rel in files]
    (root / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_script(root: pathlib.Path, args: tuple[str, ...], timeout_seconds: int) -> SimpleNamespace:
    """Run a publishing helper as an isolated subprocess process group.

    Earlier revisions used runpy to execute helpers inside the rebuild
    controller and monkey-patched subprocess.Popen to catch children.  That was
    fast, but it let imported module state, signal handlers, and helper globals
    survive across dozens of checks.  For a cloudtainer rebuild, isolation is
    more valuable: each helper gets a fresh interpreter, stdlib-only helpers run with site startup disabled, stdout is discarded,
    stderr is captured for diagnostics, bytecode is suppressed, and any timeout
    kills the whole child process group.  The polling heartbeat keeps long but
    legitimate helper checks visible to constrained session wrappers.
    """
    started = time.monotonic()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    py_flags = ["-B"] if args[0] in SITE_REQUIRED_SCRIPTS else ["-S", "-B"]
    cmd = [sys.executable, *py_flags, *args]
    timed_out = False
    stderr = ""
    returncode = 124
    timeout_seconds = max(1, int(timeout_seconds))
    heartbeat_seconds = max(5, min(15, max(1, timeout_seconds // 3)))
    deadline = started + timeout_seconds
    proc = subprocess.Popen(
        cmd,
        cwd=root,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        env=env,
        start_new_session=True,
    )
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            timed_out = True
            break
        try:
            _, tail = proc.communicate(timeout=min(heartbeat_seconds, remaining))
            stderr = (stderr or "") + (tail or "")
            returncode = proc.returncode
            break
        except subprocess.TimeoutExpired:
            elapsed = round(time.monotonic() - started, 1)
            print(json.dumps({"phase": "heartbeat", "script": args[0], "elapsed_seconds": elapsed}), file=sys.stderr, flush=True)

    if timed_out:
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except Exception:
            proc.terminate()
        try:
            _, tail = proc.communicate(timeout=2)
            stderr = (stderr or "") + (tail or "")
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except Exception:
                proc.kill()
            _, tail = proc.communicate()
            stderr = (stderr or "") + (tail or "")
        returncode = 124
        stderr = (stderr or "") + f"\n[rebuild runner] timeout after {timeout_seconds} seconds; killed process group for {' '.join(args)}\n"
    return SimpleNamespace(returncode=returncode, stderr=stderr or "", elapsed_seconds=round(time.monotonic() - started, 3), timed_out=timed_out)

def run_group(root: pathlib.Path, scripts: list[tuple[str, ...]], codes: dict[str, int], timings: dict[str, float], timeout_seconds: int) -> bool:
    ok = True
    for args in scripts:
        if args[0] == "publishing/check_transient_surface.py":
            prune_python_bytecode(root)
        print(json.dumps({"phase": "run", "script": args[0]}), file=sys.stderr, flush=True)
        proc = run_script(root, args, timeout_seconds)
        codes[args[0]] = proc.returncode
        timings[args[0]] = proc.elapsed_seconds
        if proc.returncode != 0:
            ok = False
            print(json.dumps({
                "script": args[0],
                "returncode": proc.returncode,
                "elapsed_seconds": proc.elapsed_seconds,
                "timed_out": proc.timed_out,
                "stderr_tail": (proc.stderr or "")[-2000:],
            }, indent=2), file=sys.stderr)
        else:
            print(json.dumps({"phase": "pass", "script": args[0], "elapsed_seconds": proc.elapsed_seconds}), file=sys.stderr, flush=True)
    return ok


def rebuild_manifest(root: pathlib.Path) -> dict[str, object]:
    prune_python_bytecode(root)
    build_manifest_json(root)
    build_manifest_sha256(root)
    prune_python_bytecode(root)
    return {"status": "pass", "phase": "manifest", "outputs": ["MANIFEST.json", "MANIFEST.sha256"]}


def rebuild_revision_bindings(root: pathlib.Path) -> dict[str, object]:
    prune_python_bytecode(root)
    update_revision_bound_surfaces(root)
    prune_python_bytecode(root)
    return {"status": "pass", "phase": "revision-bindings", "outputs": ["release_queue/QUEUE_INDEX.json", "ASSURANCE_ARTIFACTS.json"]}


def rebuild_first_pass(root: pathlib.Path, timeout_seconds: int, codes: dict[str, int] | None = None, timings: dict[str, float] | None = None) -> dict[str, object]:
    if codes is None:
        codes = {}
    if timings is None:
        timings = {}
    prune_python_bytecode(root)
    update_revision_bound_surfaces(root)
    first_ok = run_group(root, FIRST_PASS_SCRIPTS, codes, timings, timeout_seconds)
    prune_python_bytecode(root)
    if not first_ok:
        return {"status": "fail", "phase": "first_pass", "final_returncodes": codes, "script_timings_seconds": timings}
    return {"status": "pass", "phase": "first_pass", "final_returncodes": codes, "script_timings_seconds": timings}


def rebuild_tail(root: pathlib.Path, max_passes: int, timeout_seconds: int, codes: dict[str, int] | None = None, timings: dict[str, float] | None = None) -> dict[str, object]:
    if codes is None:
        codes = {}
    if timings is None:
        timings = {}
    prune_python_bytecode(root)
    update_revision_bound_surfaces(root)
    settled = False
    passes = 0
    changed_targets: list[str] = []
    pass_summaries: list[dict[str, object]] = []
    for passes in range(1, max_passes + 1):
        before = snapshot(root, TAIL_TARGETS)
        build_manifest_json(root)
        build_manifest_sha256(root)
        tail_ok = run_group(root, TAIL_SCRIPTS, codes, timings, timeout_seconds)
        prune_python_bytecode(root)
        after = snapshot(root, TAIL_TARGETS)
        changed_targets = sorted(rel for rel in TAIL_TARGETS if before.get(rel) != after.get(rel))
        pass_summaries.append({"pass": passes, "changed_target_count": len(changed_targets), "changed_targets": changed_targets[:80]})
        print(json.dumps({"phase": "tail-pass-summary", "pass": passes, "changed_target_count": len(changed_targets), "changed_targets": changed_targets[:20]}), file=sys.stderr, flush=True)
        if before == after:
            settled = True
            break
        if not tail_ok:
            # Manifest-dependent reports can fail during an unsettled pass because
            # they intentionally audit MANIFEST.sha256 while also being listed in
            # it. Continue until either the report/checksum fixed point settles
            # cleanly or the maximum pass budget is exhausted. Persistent failures
            # still fail when convergence does not occur.
            continue

    if not settled:
        return {"status": "fail", "reason": "tail reports did not settle", "tail_passes": passes, "changed_targets": changed_targets, "pass_summaries": pass_summaries, "final_returncodes": codes, "script_timings_seconds": timings}

    if any(code != 0 for code in codes.values()):
        return {"status": "fail", "phase": "tail", "reason": "tail settled with nonzero helper return codes", "tail_passes": passes, "changed_targets": changed_targets, "pass_summaries": pass_summaries, "final_returncodes": codes, "script_timings_seconds": timings}

    return {"status": "pass", "phase": "tail", "tail_passes": passes, "pass_summaries": pass_summaries, "final_returncodes": codes, "script_timings_seconds": timings}


def rebuild(root: pathlib.Path, max_passes: int, timeout_seconds: int) -> dict[str, object]:
    codes: dict[str, int] = {}
    timings: dict[str, float] = {}
    started = time.monotonic()
    first = rebuild_first_pass(root, timeout_seconds, codes, timings)
    if first.get("status") != "pass":
        first["elapsed_seconds"] = round(time.monotonic() - started, 3)
        return first
    tail = rebuild_tail(root, max_passes, timeout_seconds, codes, timings)
    tail["phase"] = "all" if tail.get("status") == "pass" else tail.get("phase", "all")
    tail["elapsed_seconds"] = round(time.monotonic() - started, 3)
    return tail


def dispatch_phase(root: pathlib.Path, phase: str, max_passes: int, timeout_seconds: int) -> dict[str, object]:
    started = time.monotonic()
    if phase == "all":
        report = rebuild(root, max_passes, timeout_seconds)
    elif phase == "revision-bindings":
        report = rebuild_revision_bindings(root)
    elif phase == "manifest":
        report = rebuild_manifest(root)
    elif phase == "first-pass":
        report = rebuild_first_pass(root, timeout_seconds)
    elif phase == "tail":
        report = rebuild_tail(root, max_passes, timeout_seconds)
    elif phase == "tail-pass":
        report = rebuild_tail(root, 1, timeout_seconds)
    else:  # pragma: no cover - argparse prevents this.
        raise ValueError(f"unknown phase: {phase}")
    report.setdefault("phase", phase)
    report["requested_phase"] = phase
    report.setdefault("elapsed_seconds", round(time.monotonic() - started, 3))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--max-passes", type=int, default=6)
    parser.add_argument("--script-timeout-seconds", type=int, default=SCRIPT_TIMEOUT_SECONDS)
    parser.add_argument("--phase", choices=["all", "revision-bindings", "manifest", "first-pass", "tail", "tail-pass"], default="all", help="run a bounded rebuild phase instead of the all-in-one rebuild")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report = dispatch_phase(root, args.phase, args.max_passes, args.script_timeout_seconds)
    print(json.dumps(report, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
