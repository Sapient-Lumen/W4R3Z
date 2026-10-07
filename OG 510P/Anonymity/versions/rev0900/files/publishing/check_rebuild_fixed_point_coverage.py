#!/usr/bin/env python3
"""Audit the archive surface rebuild fixed-point declaration."""

from __future__ import annotations

import argparse
import ast
import json
import pathlib
import sys
from typing import Any

REBUILD_SCRIPT = "publishing/rebuild_archive_surfaces.py"
WORKED_EXAMPLE_REBUILD_HELPER = "series/synthesis/paper17_worked_example_receipt_interlock/tools/rebuild_example.sh"
WORKED_EXAMPLE_REFINE_HELPER = "series/synthesis/paper17_worked_example_receipt_interlock/tools/refine_terminal_witnesses.py"
SUPPORT_MANIFEST_INTEGRITY_SCRIPT = "publishing/check_support_manifest_integrity.py"
QUEUE_COMPILE_SCRIPT = "publishing/check_queue_compile_smoke.py"
QUEUE_COMPILE_RUNNER = "publishing/run_queue_compile_smoke.sh"
UNQUEUED_COMPILE_SCRIPT = "publishing/check_unqueued_compile_triage.py"
PUBLISHED_COMPILE_SCRIPT = "publishing/check_published_compile_triage.py"
AUXILIARY_TEX_COMPILE_SCRIPT = "publishing/check_auxiliary_tex_compile_triage.py"
VERIFY_DRIVER_SCRIPT = "publishing/run_verify_surfaces.py"
LIVE_COMPILE_LOCK_SCRIPT = "publishing/live_compile_lock.py"
TEX_SOURCE_SAFETY_SCRIPT = "publishing/check_tex_source_safety.py"
TEX_COMPILE_RECEIPTS_SCRIPT = "publishing/tex_compile_receipts.py"
REQUIRED_SYNTHETIC_OUTPUTS = ["MANIFEST.json", "MANIFEST.sha256"]
REQUIRED_REBUILD_PHASES = ["all", "revision-bindings", "manifest", "first-pass", "tail", "tail-pass"]
REQUIRED_MAKE_TARGETS = {
    "rebuild-surfaces": "python3 -B publishing/rebuild_archive_surfaces.py --root .",
    "rebuild-revision-bindings": "python3 -B publishing/rebuild_archive_surfaces.py --root . --phase revision-bindings",
    "rebuild-manifest": "python3 -B publishing/rebuild_archive_surfaces.py --root . --phase manifest",
    "rebuild-first-pass": "python3 -B publishing/rebuild_archive_surfaces.py --root . --phase first-pass",
    "rebuild-tail": "python3 -B publishing/rebuild_archive_surfaces.py --root . --phase tail",
    "hold-compile-triage-verify": "python3 -B publishing/check_queue_compile_smoke.py --root . --report-path release_queue/HOLD_COMPILE_TRIAGE.json --states hold --require-digest-receipts --require-reproducible-receipts",
    "unqueued-compile-triage": "python3 -B publishing/check_unqueued_compile_triage.py --root . --run-live --write-report release_queue/UNQUEUED_COMPILE_TRIAGE.json --write-md release_queue/UNQUEUED_COMPILE_TRIAGE.md --timeout-seconds 30 --passes 3",
    "unqueued-compile-triage-verify": "python3 -B publishing/check_unqueued_compile_triage.py --root . --report-path release_queue/UNQUEUED_COMPILE_TRIAGE.json",
    "published-compile-triage": "python3 -B publishing/check_published_compile_triage.py --root . --run-live --write-report published/PUBLISHED_COMPILE_TRIAGE.json --write-md published/PUBLISHED_COMPILE_TRIAGE.md --timeout-seconds 60 --passes 3",
    "published-compile-triage-verify": "python3 -B publishing/check_published_compile_triage.py --root . --report-path published/PUBLISHED_COMPILE_TRIAGE.json",
    "auxiliary-tex-compile-triage": "python3 -B publishing/check_auxiliary_tex_compile_triage.py --root . --run-live --write-report index/AUXILIARY_TEX_COMPILE_TRIAGE.json --write-md index/AUXILIARY_TEX_COMPILE_TRIAGE.md --timeout-seconds 30 --passes 3",
    "auxiliary-tex-compile-triage-verify": "python3 -B publishing/check_auxiliary_tex_compile_triage.py --root . --report-path index/AUXILIARY_TEX_COMPILE_TRIAGE.json",
    "live-compile-lock-self-test": "python3 -B publishing/live_compile_lock.py --root . --self-test",
    "verify-surfaces": "python3 -S -B publishing/run_verify_surfaces.py --root .",
}
SPECIAL_OUTPUTS = {
    "publishing/update_release_provenance.py": ["release_provenance.intoto.jsonl"],
    "publishing/build_publication_blockers.py": ["release_queue/PUBLICATION_BLOCKERS.md", "release_queue/PUBLICATION_BLOCKERS.json"],
}


def literal_assignment(module: ast.Module, name: str) -> Any:
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
    raise KeyError(f"missing assignment {name}")


def output_paths(script_args: tuple[str, ...]) -> list[str]:
    outputs = list(SPECIAL_OUTPUTS.get(script_args[0], []))
    for flag in ("--write-report", "--write-json", "--write-md"):
        if flag in script_args:
            idx = script_args.index(flag)
            if idx + 1 < len(script_args):
                outputs.append(script_args[idx + 1])
    deduped = []
    for out in outputs:
        if out not in deduped:
            deduped.append(out)
    return deduped


def check(root: pathlib.Path) -> dict[str, Any]:
    release = json.loads((root / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
    script_text = (root / REBUILD_SCRIPT).read_text(encoding="utf-8")
    makefile_text = (root / "Makefile").read_text(encoding="utf-8") if (root / "Makefile").exists() else ""
    tree = ast.parse(script_text)
    first_pass = [tuple(row) for row in literal_assignment(tree, "FIRST_PASS_SCRIPTS")]
    tail_scripts = [tuple(row) for row in literal_assignment(tree, "TAIL_SCRIPTS")]
    tail_targets = list(literal_assignment(tree, "TAIL_TARGETS"))
    tail_outputs = list(REQUIRED_SYNTHETIC_OUTPUTS)
    script_output_rows = []
    for args in tail_scripts:
        outs = output_paths(args)
        script_output_rows.append({"script": args[0], "outputs": outs})
        for out in outs:
            if out not in tail_outputs:
                tail_outputs.append(out)
    duplicate_tail_targets = sorted({target for target in tail_targets if tail_targets.count(target) > 1})
    missing_from_tail_targets = sorted(set(tail_outputs) - set(tail_targets))
    extra_tail_targets = sorted(set(tail_targets) - set(tail_outputs))
    self_report = "reports/rebuild_fixed_point_coverage.json"
    missing_tail_target_files = sorted(
        rel for rel in tail_targets
        if rel != self_report and not (root / rel).exists()
    )
    missing_tail_scripts = sorted(args[0] for args in tail_scripts if not (root / args[0]).exists())
    missing_first_pass_scripts = sorted(args[0] for args in first_pass if not (root / args[0]).exists())
    missing_phase_tokens = sorted(phase for phase in REQUIRED_REBUILD_PHASES if f'"{phase}"' not in script_text)
    missing_make_targets = sorted(target for target, command in REQUIRED_MAKE_TARGETS.items() if f"{target}:" not in makefile_text or command not in makefile_text)
    bytecode_cleanup_present = "def prune_python_bytecode" in script_text and "__pycache__" in script_text
    child_cleanup_present = "os.killpg" in script_text and "start_new_session" in script_text
    rebuild_runner_heartbeat_present = all(token in script_text for token in ['"phase": "heartbeat"', "heartbeat_seconds", "proc.communicate(timeout=min(heartbeat_seconds, remaining))"])
    manifest_self_audit_recovery_present = "Manifest-dependent reports can fail during an unsettled pass" in script_text and "tail reports did not settle" in script_text
    worked_helper_path = root / WORKED_EXAMPLE_REBUILD_HELPER
    worked_helper_text = worked_helper_path.read_text(encoding="utf-8") if worked_helper_path.exists() else ""
    worked_helper_exists = worked_helper_path.exists()
    worked_refine_path = root / WORKED_EXAMPLE_REFINE_HELPER
    worked_refine_text = worked_refine_path.read_text(encoding="utf-8") if worked_refine_path.exists() else ""
    support_manifest_integrity_path = root / SUPPORT_MANIFEST_INTEGRITY_SCRIPT
    support_manifest_integrity_text = support_manifest_integrity_path.read_text(encoding="utf-8") if support_manifest_integrity_path.exists() else ""
    queue_compile_path = root / QUEUE_COMPILE_SCRIPT
    queue_runner_path = root / QUEUE_COMPILE_RUNNER
    unqueued_compile_path = root / UNQUEUED_COMPILE_SCRIPT
    published_compile_path = root / PUBLISHED_COMPILE_SCRIPT
    auxiliary_tex_compile_path = root / AUXILIARY_TEX_COMPILE_SCRIPT
    live_compile_lock_path = root / LIVE_COMPILE_LOCK_SCRIPT
    queue_compile_text = queue_compile_path.read_text(encoding="utf-8") if queue_compile_path.exists() else ""
    queue_runner_text = queue_runner_path.read_text(encoding="utf-8") if queue_runner_path.exists() else ""
    unqueued_compile_text = unqueued_compile_path.read_text(encoding="utf-8") if unqueued_compile_path.exists() else ""
    published_compile_text = published_compile_path.read_text(encoding="utf-8") if published_compile_path.exists() else ""
    auxiliary_tex_compile_text = auxiliary_tex_compile_path.read_text(encoding="utf-8") if auxiliary_tex_compile_path.exists() else ""
    live_compile_lock_text = live_compile_lock_path.read_text(encoding="utf-8") if live_compile_lock_path.exists() else ""
    verify_driver_path = root / VERIFY_DRIVER_SCRIPT
    verify_driver_text = verify_driver_path.read_text(encoding="utf-8") if verify_driver_path.exists() else ""
    tex_source_safety_path = root / TEX_SOURCE_SAFETY_SCRIPT
    tex_source_safety_text = tex_source_safety_path.read_text(encoding="utf-8") if tex_source_safety_path.exists() else ""
    tex_compile_receipts_path = root / TEX_COMPILE_RECEIPTS_SCRIPT
    tex_compile_receipts_text = tex_compile_receipts_path.read_text(encoding="utf-8") if tex_compile_receipts_path.exists() else ""
    toolchain_fingerprint_text = (root / "publishing" / "check_toolchain_fingerprint.py").read_text(encoding="utf-8") if (root / "publishing" / "check_toolchain_fingerprint.py").exists() else ""
    check_archive_coherence_text = (root / "publishing" / "check_archive_coherence.py").read_text(encoding="utf-8") if (root / "publishing" / "check_archive_coherence.py").exists() else ""
    worked_helper_fixed_point_present = all(token in worked_helper_text for token in ["MAX_REFINE_PASSES", "artifact_digest", "did not settle", "fixed point after pass"])
    worked_helper_no_ignored_validation_present = "first_validate_status" not in worked_helper_text and "validate_rc=$?" in worked_helper_text
    worked_helper_no_shell_escape_tex_present = "-no-shell-escape" in worked_helper_text and "-halt-on-error" in worked_helper_text
    worked_helper_temp_tex_output_present = "-output-directory" in worked_helper_text and "mktemp -d" in worked_helper_text
    worked_helper_pdf_cleanup_present = "paper.pdf" in worked_helper_text and "cleanup_transients" in worked_helper_text
    worked_helper_bytecode_cleanup_present = "PYTHONDONTWRITEBYTECODE" in worked_helper_text and "*.pyo" in worked_helper_text and "-B" in worked_helper_text
    worked_helper_cloudtainer_heartbeat_present = "run_with_heartbeat" in worked_helper_text and "worked-example" in worked_helper_text
    worked_helper_skip_tex_present = "--skip-tex" in worked_helper_text
    worked_example_compact_json_writer_present = all(token in worked_refine_text for token in [
        "COMPACT_JSON_ARTIFACTS",
        "example_series_spine.json",
        "example_question_routes.json",
        "separators=(',', ':')",
    ])
    support_manifest_compact_json_guard_present = all(token in support_manifest_integrity_text for token in [
        "COMPACT_WORKED_EXAMPLE_JSON",
        "compact-json-canonicality-mismatch",
        "compact_json_savings_bytes",
        "example_series_spine.json",
        "example_question_routes.json",
    ])
    queue_compile_scope_controls_present = all(token in queue_compile_text for token in ["--states", "--start-index", "--max-targets", "--include-path", "apply_target_scope"])
    queue_compile_resume_ingest_present = all(token in queue_compile_text + queue_runner_text for token in ["--run-dir", "--ingest-run-dir", "result_*.tsv", "refresh_results_tsv", "Outer cloudtainer timeouts"])
    queue_compile_root_missing_diagnostic_present = all(token in queue_compile_text for token in ["compile root missing before pdflatex launch", "compile root missing during pdflatex launch", "return 126"])
    queue_compile_merge_index_guard_present = all(token in queue_compile_text for token in ["for ordinal, t in enumerate(ts, 1)", "stored_report_duplicate_row_indexes", "duplicate_stored_index_count"])
    queue_compile_hold_digest_required_present = all(token in queue_compile_text for token in ["selected_states_for_digest", "(\"hold\",)", "digest_receipt_failures"])
    unqueued_compile_index_guard_present = all(token in unqueued_compile_text for token in ["for ordinal, path in enumerate(all_sources, 1)", "stored_report_index_integrity_failure", "duplicate_index_count"])
    unqueued_compile_digest_required_present = "digest_required = True" in unqueued_compile_text and "digest_receipt_failures" in unqueued_compile_text and "reproducible_required = True" in unqueued_compile_text and "reproducible_receipt_failures" in unqueued_compile_text
    queue_compile_hold_scope_present = '"hold": "release_queue/hold"' in queue_compile_text
    queue_compile_reindexed_scope_present = "queue_order_index" in queue_compile_text and '"queue_order_index": t.get("queue_order_index", t["index"])' in queue_compile_text
    queue_compile_heartbeat_present = all(token in queue_compile_text for token in ["heartbeat_label", "queue-compile-smoke heartbeat", "queue-compile-smoke target-complete", "proc.poll()"])
    queue_runner_scope_passthrough_present = all(token in queue_runner_text for token in ["--states", "--start-index", "--max-targets", "--include-path", "INCLUDE_PATHS"])
    hold_triage_stored_verify_present = (
        "hold-compile-triage-verify:" in makefile_text
        and "release_queue/HOLD_COMPILE_TRIAGE.json" in makefile_text
        and "--states hold" in makefile_text
    )
    queue_compile_stored_verifier_order_guard_present = all(token in queue_compile_text for token in [
        "stored_report_queue_order_mismatches",
        "stored_report_queue_note_mismatches",
        "stored_report_missing_no_shell_escape_command_family",
        "stored_summary_consistency_failures",
        "stored_report_summary_metric_mismatch",
    ])
    unqueued_compile_triage_present = all(token in unqueued_compile_text for token in [
        "def unqueued_sources",
        "--merge-parts",
        "release_queue/UNQUEUED_COMPILE_TRIAGE.json",
        "pdflatex",
        "-no-shell-escape",
        "stored_report_path_scope_mismatch",
        "stored_report_source_hash_mismatches",
    ])
    unqueued_compile_make_verify_present = (
        "unqueued-compile-triage-verify:" in makefile_text
        and "publishing/check_unqueued_compile_triage.py --root . --report-path release_queue/UNQUEUED_COMPILE_TRIAGE.json" in makefile_text
    )
    published_compile_triage_present = all(token in published_compile_text for token in [
        "def published_sources",
        "publication_classification.json",
        "published/PUBLISHED_COMPILE_TRIAGE.json",
        "pdflatex",
        "-no-shell-escape",
        "pdf_sha256",
        "stored_report_pdf_output_evidence_missing",
        "render_markdown",
    ])
    published_compile_make_verify_present = (
        "published-compile-triage-verify:" in makefile_text
        and "publishing/check_published_compile_triage.py --root . --report-path published/PUBLISHED_COMPILE_TRIAGE.json" in makefile_text
    )
    auxiliary_tex_compile_triage_present = all(token in auxiliary_tex_compile_text for token in [
        "all *.tex minus series/**/paper.tex and published/**/paper.tex",
        "stored_report_path_scope_mismatch",
        "stored_report_source_hash_mismatches",
        "-no-shell-escape",
        "pdflatex",
        "def sources",
    ])
    auxiliary_tex_compile_make_verify_present = (
        "auxiliary-tex-compile-triage-verify:" in makefile_text
        and "publishing/check_auxiliary_tex_compile_triage.py --root . --report-path index/AUXILIARY_TEX_COMPILE_TRIAGE.json" in makefile_text
    )
    verify_surface_driver_present = (
        "verify-surfaces:" in makefile_text
        and "python3 -S -B publishing/run_verify_surfaces.py --root ." in makefile_text
        and all(token in verify_driver_text for token in ["VERIFY_COMMANDS", "start_new_session", "os.killpg", "publishing/check_toolchain_fingerprint.py", "publishing/live_compile_lock.py", "publishing/check_unqueued_compile_triage.py", "publishing/check_published_compile_triage.py", "publishing/check_auxiliary_tex_compile_triage.py", "release_queue/HOLD_COMPILE_TRIAGE.json", "--require-digest-receipts", "--require-reproducible-receipts", "published/PUBLISHED_COMPILE_TRIAGE.json", "index/AUXILIARY_TEX_COMPILE_TRIAGE.json"])
    )
    live_compile_lock_script_present = all(token in live_compile_lock_text for token in ["LiveCompileLockTimeout", "fcntl.flock", "LOCK_EX", "LOCK_NB", "self_test", "child_blocked_while_parent_holds_lock", "child_acquires_after_parent_release"])
    live_compile_project_scope_present = all(token in live_compile_lock_text for token in ["lock_scope_token", "ANONYMITY_LIVE_COMPILE_LOCK_SCOPE", "project_scope_lock_path_shared_across_clone", "project_scope_blocks_clone_worktree", "lock_scope"])
    live_compile_lock_runner_coverage_present = all("live_compile_lock" in text and "LiveCompileLockTimeout" in text for text in [queue_compile_text, unqueued_compile_text, published_compile_text, auxiliary_tex_compile_text])
    live_compile_lock_verify_present = "live-compile-lock-self-test:" in makefile_text and "publishing/live_compile_lock.py --root . --self-test" in makefile_text and "publishing/live_compile_lock.py" in verify_driver_text
    live_compile_lock_failfast_present = all(token in live_compile_lock_text for token in ["ANONYMITY_LIVE_COMPILE_LOCK_WAIT_SECONDS", "LiveCompileLockTimeout", "live_compile_lock_busy"]) and all("live_compile_lock_busy" in text for text in [queue_compile_text, unqueued_compile_text, published_compile_text, auxiliary_tex_compile_text])
    toolchain_fingerprint_negative_controls_present = all(token in toolchain_fingerprint_text for token in ["negative_control_results", "compile_surface_fingerprint_mismatch", "COMPILE_EVIDENCE_SURFACES"])
    tex_source_safety_doubled_command_guard_present = all(token in tex_source_safety_text for token in [
        "SUSPICIOUS_DOUBLED_COMMAND_RE",
        "suspicious_doubled_command_escape",
        "doubled_command_escape_allowed",
        "ALLOWED_DOUBLED_COMMANDS_AFTER_LINEBREAK",
    ])
    tex_source_safety_negative_controls_present = all(token in tex_source_safety_text for token in [
        "NEGATIVE_CONTROL_CASES",
        "negative_control_results",
        "doubled_latex_command",
        "doubled_texttt_command",
        "doubled_math_relation",
        "negative_control_failed_count",
    ])
    tex_compile_receipts_deterministic_selftest_present = all(token in tex_compile_receipts_text for token in [
        "RECEIPT_POLICY_VERSION",
        "stable_pdf_trailer_id",
        "pdflatex_receipt_command",
        "deterministic_compile_env",
        "normalize_tex_log_text",
        "normalize_pdf_bytes",
        "reproducible_receipt_failures",
        "negative_control_results",
        "normalized_pdf_digest_matches",
    ])
    queue_compile_release_reproducible_receipts_present = all(token in queue_compile_text for token in [
        "deterministic_compile_env",
        "pdflatex_receipt_command",
        "stable_pdf_trailer_id",
        "reproducible_receipt_failures",
        "--require-reproducible-receipts",
        "reproducible_receipt_missing_count",
    ]) and "--require-reproducible-receipts" in makefile_text and "--require-reproducible-receipts" in verify_driver_text
    full_tex_partition_reproducible_receipts_present = all(token in check_archive_coherence_text for token in [
        "all_tex_compile_reproducible_receipts_are_complete",
        "compile_reproducible_receipt_missing",
        "published_reproducible_missing",
        "auxiliary_reproducible_missing",
        "unqueued_reproducible_missing_paths",
        "hold_reproducible_missing_paths",
    ]) and all("reproducible_receipt_failures" in text and "reproducible_receipt_missing_count" in text for text in [queue_compile_text, unqueued_compile_text, published_compile_text, auxiliary_tex_compile_text])
    failures = []
    if duplicate_tail_targets:
        failures.append({"category": "duplicate_tail_targets", "paths": duplicate_tail_targets})
    if missing_from_tail_targets:
        failures.append({"category": "tail_outputs_missing_from_tail_targets", "paths": missing_from_tail_targets})
    if missing_tail_target_files:
        failures.append({"category": "tail_target_files_missing", "paths": missing_tail_target_files})
    if missing_tail_scripts or missing_first_pass_scripts:
        failures.append({"category": "rebuild_scripts_missing", "first_pass": missing_first_pass_scripts, "tail": missing_tail_scripts})
    if missing_phase_tokens:
        failures.append({"category": "rebuild_phase_entry_points_missing", "phases": missing_phase_tokens})
    if missing_make_targets:
        failures.append({"category": "make_phase_targets_missing", "targets": missing_make_targets})
    if not bytecode_cleanup_present:
        failures.append({"category": "bytecode_cleanup_missing"})
    if not child_cleanup_present:
        failures.append({"category": "child_cleanup_missing"})
    if not rebuild_runner_heartbeat_present:
        failures.append({"category": "rebuild_runner_heartbeat_missing", "path": REBUILD_SCRIPT})
    if not manifest_self_audit_recovery_present:
        failures.append({"category": "manifest_self_audit_recovery_missing"})
    if not worked_helper_exists:
        failures.append({"category": "worked_example_rebuild_helper_missing", "path": WORKED_EXAMPLE_REBUILD_HELPER})
    if not worked_helper_fixed_point_present:
        failures.append({"category": "worked_example_rebuild_helper_fixed_point_missing", "path": WORKED_EXAMPLE_REBUILD_HELPER})
    if not worked_helper_no_ignored_validation_present:
        failures.append({"category": "worked_example_rebuild_helper_ignored_validation_guard_missing", "path": WORKED_EXAMPLE_REBUILD_HELPER})
    if not worked_helper_no_shell_escape_tex_present:
        failures.append({"category": "worked_example_rebuild_helper_safe_tex_missing", "path": WORKED_EXAMPLE_REBUILD_HELPER})
    if not worked_helper_temp_tex_output_present:
        failures.append({"category": "worked_example_rebuild_helper_temp_tex_output_missing", "path": WORKED_EXAMPLE_REBUILD_HELPER})
    if not worked_helper_pdf_cleanup_present:
        failures.append({"category": "worked_example_rebuild_helper_pdf_cleanup_missing", "path": WORKED_EXAMPLE_REBUILD_HELPER})
    if not worked_helper_bytecode_cleanup_present:
        failures.append({"category": "worked_example_rebuild_helper_bytecode_cleanup_missing", "path": WORKED_EXAMPLE_REBUILD_HELPER})
    if not worked_helper_cloudtainer_heartbeat_present:
        failures.append({"category": "worked_example_rebuild_helper_heartbeat_missing", "path": WORKED_EXAMPLE_REBUILD_HELPER})
    if not worked_helper_skip_tex_present:
        failures.append({"category": "worked_example_rebuild_helper_skip_tex_missing", "path": WORKED_EXAMPLE_REBUILD_HELPER})
    if not worked_example_compact_json_writer_present:
        failures.append({"category": "worked_example_compact_json_writer_missing", "path": WORKED_EXAMPLE_REFINE_HELPER})
    if not support_manifest_compact_json_guard_present:
        failures.append({"category": "support_manifest_compact_json_guard_missing", "path": SUPPORT_MANIFEST_INTEGRITY_SCRIPT})
    if not queue_compile_scope_controls_present:
        failures.append({"category": "queue_compile_scope_controls_missing", "path": QUEUE_COMPILE_SCRIPT})
    if not queue_compile_resume_ingest_present:
        failures.append({"category": "queue_compile_resume_ingest_missing", "path": QUEUE_COMPILE_SCRIPT})
    if not queue_compile_root_missing_diagnostic_present:
        failures.append({"category": "queue_compile_root_missing_diagnostic_missing", "path": QUEUE_COMPILE_SCRIPT})
    if not queue_compile_merge_index_guard_present:
        failures.append({"category": "queue_compile_merge_index_guard_missing", "path": QUEUE_COMPILE_SCRIPT})
    if not queue_compile_hold_digest_required_present:
        failures.append({"category": "queue_compile_hold_digest_requirement_missing", "path": QUEUE_COMPILE_SCRIPT})
    if not unqueued_compile_index_guard_present:
        failures.append({"category": "unqueued_compile_index_guard_missing", "path": UNQUEUED_COMPILE_SCRIPT})
    if not unqueued_compile_digest_required_present:
        failures.append({"category": "unqueued_compile_digest_requirement_missing", "path": UNQUEUED_COMPILE_SCRIPT})
    if not queue_compile_hold_scope_present:
        failures.append({"category": "queue_compile_hold_scope_missing", "path": QUEUE_COMPILE_SCRIPT})
    if not queue_compile_reindexed_scope_present:
        failures.append({"category": "queue_compile_reindexed_scope_missing", "path": QUEUE_COMPILE_SCRIPT})
    if not queue_compile_heartbeat_present:
        failures.append({"category": "queue_compile_heartbeat_missing", "path": QUEUE_COMPILE_SCRIPT})
    if not queue_runner_scope_passthrough_present:
        failures.append({"category": "queue_compile_runner_scope_passthrough_missing", "path": QUEUE_COMPILE_RUNNER})
    if not hold_triage_stored_verify_present:
        failures.append({"category": "hold_compile_triage_stored_verifier_missing", "path": "Makefile"})
    if not queue_compile_stored_verifier_order_guard_present:
        failures.append({"category": "queue_compile_stored_verifier_order_guard_missing", "path": QUEUE_COMPILE_SCRIPT})
    if not unqueued_compile_triage_present:
        failures.append({"category": "unqueued_compile_triage_missing", "path": UNQUEUED_COMPILE_SCRIPT})
    if not unqueued_compile_make_verify_present:
        failures.append({"category": "unqueued_compile_make_verify_missing", "path": "Makefile"})
    if not published_compile_triage_present:
        failures.append({"category": "published_compile_triage_missing", "path": PUBLISHED_COMPILE_SCRIPT})
    if not published_compile_make_verify_present:
        failures.append({"category": "published_compile_make_verify_missing", "path": "Makefile"})
    if not auxiliary_tex_compile_triage_present:
        failures.append({"category": "auxiliary_tex_compile_triage_missing", "path": AUXILIARY_TEX_COMPILE_SCRIPT})
    if not auxiliary_tex_compile_make_verify_present:
        failures.append({"category": "auxiliary_tex_compile_make_verify_missing", "path": "Makefile"})
    if not verify_surface_driver_present:
        failures.append({"category": "verify_surface_driver_missing", "path": VERIFY_DRIVER_SCRIPT})
    if not live_compile_lock_script_present:
        failures.append({"category": "live_compile_lock_script_missing", "path": LIVE_COMPILE_LOCK_SCRIPT})
    if not live_compile_lock_runner_coverage_present:
        failures.append({"category": "live_compile_lock_runner_coverage_missing", "paths": [QUEUE_COMPILE_SCRIPT, UNQUEUED_COMPILE_SCRIPT, PUBLISHED_COMPILE_SCRIPT, AUXILIARY_TEX_COMPILE_SCRIPT]})
    if not live_compile_lock_verify_present:
        failures.append({"category": "live_compile_lock_verify_missing", "path": "Makefile"})
    if not live_compile_lock_failfast_present:
        failures.append({"category": "live_compile_lock_failfast_missing", "path": LIVE_COMPILE_LOCK_SCRIPT})
    if not live_compile_project_scope_present:
        failures.append({"category": "live_compile_lock_project_scope_missing", "path": LIVE_COMPILE_LOCK_SCRIPT})
    if not toolchain_fingerprint_negative_controls_present:
        failures.append({"category": "toolchain_fingerprint_negative_controls_missing", "path": "publishing/check_toolchain_fingerprint.py"})
    if not tex_source_safety_doubled_command_guard_present:
        failures.append({"category": "tex_source_safety_doubled_command_guard_missing", "path": TEX_SOURCE_SAFETY_SCRIPT})
    if not tex_source_safety_negative_controls_present:
        failures.append({"category": "tex_source_safety_negative_controls_missing", "path": TEX_SOURCE_SAFETY_SCRIPT})
    if not tex_compile_receipts_deterministic_selftest_present:
        failures.append({"category": "tex_compile_receipts_deterministic_selftest_missing", "path": TEX_COMPILE_RECEIPTS_SCRIPT})
    if not queue_compile_release_reproducible_receipts_present:
        failures.append({"category": "queue_compile_release_reproducible_receipts_missing", "path": QUEUE_COMPILE_SCRIPT})
    if not full_tex_partition_reproducible_receipts_present:
        failures.append({"category": "full_tex_partition_reproducible_receipts_missing", "paths": [QUEUE_COMPILE_SCRIPT, UNQUEUED_COMPILE_SCRIPT, PUBLISHED_COMPILE_SCRIPT, AUXILIARY_TEX_COMPILE_SCRIPT, "publishing/check_archive_coherence.py"]})
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "rebuild_script": REBUILD_SCRIPT,
        "worked_example_rebuild_helper": WORKED_EXAMPLE_REBUILD_HELPER,
        "queue_compile_script": QUEUE_COMPILE_SCRIPT,
        "queue_compile_runner": QUEUE_COMPILE_RUNNER,
        "unqueued_compile_script": UNQUEUED_COMPILE_SCRIPT,
        "published_compile_script": PUBLISHED_COMPILE_SCRIPT,
        "auxiliary_tex_compile_script": AUXILIARY_TEX_COMPILE_SCRIPT,
        "verify_driver_script": VERIFY_DRIVER_SCRIPT,
        "live_compile_lock_script": LIVE_COMPILE_LOCK_SCRIPT,
        "first_pass_scripts": [args[0] for args in first_pass],
        "tail_scripts": [args[0] for args in tail_scripts],
        "script_outputs": script_output_rows,
        "required_rebuild_phases": REQUIRED_REBUILD_PHASES,
        "makefile_phase_targets": REQUIRED_MAKE_TARGETS,
        "required_tail_outputs": tail_outputs,
        "tail_targets": tail_targets,
        "extra_tail_targets": extra_tail_targets,
        "failures": failures,
        "summary": {
            "checks_failed": len(failures),
            "first_pass_script_count": len(first_pass),
            "tail_script_count": len(tail_scripts),
            "tail_output_count": len(tail_outputs),
            "tail_target_count": len(tail_targets),
            "missing_tail_target_count": len(missing_from_tail_targets),
            "missing_tail_target_file_count": len(missing_tail_target_files),
            "duplicate_tail_target_count": len(duplicate_tail_targets),
            "extra_tail_target_count": len(extra_tail_targets),
            "required_rebuild_phase_count": len(REQUIRED_REBUILD_PHASES),
            "missing_rebuild_phase_count": len(missing_phase_tokens),
            "make_phase_target_count": len(REQUIRED_MAKE_TARGETS),
            "missing_make_phase_target_count": len(missing_make_targets),
            "bytecode_cleanup_present": bytecode_cleanup_present,
            "child_cleanup_present": child_cleanup_present,
            "rebuild_runner_heartbeat_present": rebuild_runner_heartbeat_present,
            "manifest_self_audit_recovery_present": manifest_self_audit_recovery_present,
            "toolchain_fingerprint_negative_controls_present": toolchain_fingerprint_negative_controls_present,
            "worked_example_helper_exists": worked_helper_exists,
            "worked_example_helper_fixed_point_present": worked_helper_fixed_point_present,
            "worked_example_helper_no_ignored_validation_present": worked_helper_no_ignored_validation_present,
            "worked_example_helper_no_shell_escape_tex_present": worked_helper_no_shell_escape_tex_present,
            "worked_example_helper_temp_tex_output_present": worked_helper_temp_tex_output_present,
            "worked_example_helper_pdf_cleanup_present": worked_helper_pdf_cleanup_present,
            "worked_example_helper_bytecode_cleanup_present": worked_helper_bytecode_cleanup_present,
            "worked_example_helper_cloudtainer_heartbeat_present": worked_helper_cloudtainer_heartbeat_present,
            "worked_example_helper_skip_tex_present": worked_helper_skip_tex_present,
            "worked_example_compact_json_writer_present": worked_example_compact_json_writer_present,
            "support_manifest_compact_json_guard_present": support_manifest_compact_json_guard_present,
            "queue_compile_scope_controls_present": queue_compile_scope_controls_present,
            "queue_compile_resume_ingest_present": queue_compile_resume_ingest_present,
            "queue_compile_root_missing_diagnostic_present": queue_compile_root_missing_diagnostic_present,
            "queue_compile_merge_index_guard_present": queue_compile_merge_index_guard_present,
            "queue_compile_hold_digest_required_present": queue_compile_hold_digest_required_present,
            "unqueued_compile_index_guard_present": unqueued_compile_index_guard_present,
            "unqueued_compile_digest_required_present": unqueued_compile_digest_required_present,
            "queue_compile_hold_scope_present": queue_compile_hold_scope_present,
            "queue_compile_reindexed_scope_present": queue_compile_reindexed_scope_present,
            "queue_compile_heartbeat_present": queue_compile_heartbeat_present,
            "queue_compile_runner_scope_passthrough_present": queue_runner_scope_passthrough_present,
            "hold_triage_stored_verify_present": hold_triage_stored_verify_present,
            "queue_compile_stored_verifier_order_guard_present": queue_compile_stored_verifier_order_guard_present,
            "unqueued_compile_triage_present": unqueued_compile_triage_present,
            "unqueued_compile_make_verify_present": unqueued_compile_make_verify_present,
            "published_compile_triage_present": published_compile_triage_present,
            "published_compile_make_verify_present": published_compile_make_verify_present,
            "auxiliary_tex_compile_triage_present": auxiliary_tex_compile_triage_present,
            "auxiliary_tex_compile_make_verify_present": auxiliary_tex_compile_make_verify_present,
            "verify_surface_driver_present": verify_surface_driver_present,
            "live_compile_lock_script_present": live_compile_lock_script_present,
            "live_compile_lock_runner_coverage_present": live_compile_lock_runner_coverage_present,
            "live_compile_lock_verify_present": live_compile_lock_verify_present,
            "live_compile_lock_failfast_present": live_compile_lock_failfast_present,
            "live_compile_lock_project_scope_present": live_compile_project_scope_present,
            "tex_source_safety_doubled_command_guard_present": tex_source_safety_doubled_command_guard_present,
            "tex_source_safety_negative_controls_present": tex_source_safety_negative_controls_present,
            "tex_compile_receipts_deterministic_selftest_present": tex_compile_receipts_deterministic_selftest_present,
            "queue_compile_release_reproducible_receipts_present": queue_compile_release_reproducible_receipts_present,
            "full_tex_partition_reproducible_receipts_present": full_tex_partition_reproducible_receipts_present,
        },
        "fail_closed_rule": "If a tail-mutated output, rebuild phase entry point, cleanup hook, rebuild-runner heartbeat, manifest self-audit recovery path, worked-example support-bundle fixed-point helper, worked-example compact artifact writer/guard, bounded queue compile triage scope, resumable queue compile ingest, live-root-loss diagnostics, scoped-result order preservation, row-index integrity, stored Hold-triage verification, unqueued/published/auxiliary compile-triage verification, no-shell-escape evidence, queue compile heartbeat, live compile mutual-exclusion lock/self-test, suspicious doubled TeX command-escape guard, TeX source-safety negative controls, deterministic TeX receipt self-tests, or full-TeX-partition reproducible receipt enforcement is missing, default to no publication and repair the executable rebuild declaration before trusting regenerated surfaces.",
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
