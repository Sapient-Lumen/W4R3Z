#!/usr/bin/env python3
"""Build and verify compile triage for paper sources outside queue states.

Unqueued sources are not Candidate, Published-ready, or Hold queue evidence.  This
checker turns that blind spot into bounded build-hygiene evidence without
promoting any source or authorizing publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from typing import Any

from tex_compile_receipts import (
    DEFAULT_SOURCE_DATE_EPOCH,
    LOG_NORMALIZATION_POLICY,
    PDF_NORMALIZATION_POLICY,
    RECEIPT_POLICY_VERSION,
    attach_compile_receipts,
    deterministic_compile_env,
    digest_receipt_failures,
    digest_receipt_missing_count,
    pdflatex_receipt_command,
    reproducible_receipt_failures,
    reproducible_receipt_missing_count,
    stable_pdf_trailer_id,
)
from live_compile_lock import LiveCompileLockTimeout, live_compile_lock

MIN_REQUIRED_PASSES = 3
NOTICE_RE = re.compile(r"(?:LaTeX|Package|Class|pdfTeX) .*?(?:Warning|Info|warning)", re.I)
OVER_RE = re.compile(r"Overfull \\hbox", re.I)
UNDER_RE = re.compile(r"Underfull \\hbox", re.I)
UNRESOLVED_RE = re.compile(
    r"(?:LaTeX Warning: (?:Citation|Reference).*undefined|"
    r"LaTeX Warning: There were undefined (?:references|citations)|"
    r"No file .*\\.(?:aux|bbl)|Citation .* undefined|Reference .* undefined)",
    re.I,
)
RERUN_RE = re.compile(
    r"(?:Rerun to get cross-references right|Label\(s\) may have changed|"
    r"Package rerunfilecheck Warning: File .* has changed|Rerun to get outlines right)",
    re.I,
)
FATAL = ("! LaTeX Error:", "! Emergency stop.", "Fatal error occurred", " ==> Fatal error occurred")

def pdflatex_fingerprint() -> dict[str, str | bool]:
    path = shutil.which("pdflatex") or ""
    version = ""
    if path:
        try:
            proc = subprocess.run(["pdflatex", "--version"], text=True, capture_output=True, timeout=5)
            version = proc.stdout if proc.stdout else proc.stderr
        except Exception:
            version = ""
    return {
        "pdflatex_path": path,
        "pdflatex_version_line": version.splitlines()[0][:200] if version.splitlines() else "",
        "pdflatex_version_output_sha256": hashlib.sha256(version.encode("utf-8", errors="replace")).hexdigest() if version else "",
        "toolchain_available": bool(path),
    }



def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def unqueued_sources(root: pathlib.Path) -> list[str]:
    queue_index = load_json(root / "release_queue" / "QUEUE_INDEX.json")
    queued: set[str] = set()
    for rows in queue_index.get("states", {}).values():
        for row in rows:
            if isinstance(row, dict) and row.get("source_tex"):
                queued.add(str(row["source_tex"]))
    all_papers = sorted(path.relative_to(root).as_posix() for path in root.glob("series/**/paper.tex"))
    return [path for path in all_papers if path not in queued]


def count_patterns(text: str) -> dict[str, int]:
    lines = text.splitlines()
    return {
        "latex_notice_lines": sum(1 for line in lines if NOTICE_RE.search(line)),
        "overfull_hbox": len(OVER_RE.findall(text)),
        "underfull_hbox": len(UNDER_RE.findall(text)),
        "unresolved_warning_hits": len(UNRESOLVED_RE.findall(text)),
        "rerun_warning_hits": len(RERUN_RE.findall(text)),
        "fatal_pattern_hits": sum(text.count(pattern) for pattern in FATAL),
    }


def scoped_sources(paths: list[str], start_index: int, max_targets: int) -> list[tuple[int, str]]:
    if start_index < 1:
        raise SystemExit("--start-index must be >= 1")
    if max_targets < 0:
        raise SystemExit("--max-targets must be >= 0")
    pairs = list(enumerate(paths, 1))[start_index - 1:]
    if max_targets:
        pairs = pairs[:max_targets]
    return pairs


def run_pdflatex_once(root: pathlib.Path, source: str, outdir: pathlib.Path, log_path: pathlib.Path, timeout_seconds: int, *, draft_mode: bool = False) -> int:
    source_path = root / source
    source_sha256 = sha256_file(source_path) if source_path.is_file() else ""
    cmd = pdflatex_receipt_command("pdflatex", source, outdir, source_sha256=source_sha256, draft_mode=draft_mode)
    env = deterministic_compile_env(os.environ.copy())
    env["TZ"] = "UTC"
    with log_path.open("w", encoding="utf-8", errors="replace") as handle:
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=root,
                stdout=handle,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                start_new_session=True,
            )
        except FileNotFoundError:
            handle.write("pdflatex not found on PATH\n")
            return 127
        try:
            return proc.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except Exception:
                proc.terminate()
            try:
                rc = proc.wait(timeout=5)
                return 124 if rc in {-15, -9, 143} else rc
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except Exception:
                    proc.kill()
                proc.wait(timeout=5)
                return 124


def compile_source(root: pathlib.Path, source: str, index: int, tmp: pathlib.Path, passes: int, timeout_seconds: int) -> dict[str, Any]:
    outdir = tmp / "out" / str(index)
    logs_dir = tmp / "logs"
    outdir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    combined_parts: list[str] = []
    completed = 0
    rc = 0
    final_text = ""
    start = time.monotonic()
    for pass_no in range(1, passes + 1):
        print(f"unqueued-compile-triage start: target {index} pass {pass_no}/{passes} {source}", file=sys.stderr, flush=True)
        log_path = logs_dir / f"{index}.pass{pass_no}.log"
        rc = run_pdflatex_once(root, source, outdir, log_path, timeout_seconds, draft_mode=(pass_no < passes))
        text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
        final_text = text
        combined_parts.append(f"=== pdflatex pass {pass_no}/{passes} rc={rc} ===\n{text}\n")
        if rc != 0:
            break
        completed = pass_no
    elapsed = time.monotonic() - start
    combined = "".join(combined_parts)
    all_counts = count_patterns(combined)
    final_counts = count_patterns(final_text)
    pdf = outdir / "paper.pdf"
    status = "pass"
    failure_category = ""
    error = ""
    if rc != 0:
        status = "fail"
        failure_category = "pdflatex_timeout" if rc == 124 else "pdflatex_failed"
        error = f"pdflatex returned {rc}"
    elif completed < MIN_REQUIRED_PASSES:
        status = "fail"
        failure_category = "pdflatex_pass_count_shortfall"
        error = f"completed {completed} passes"
    elif not (pdf.exists() and pdf.stat().st_size > 0):
        status = "fail"
        failure_category = "pdf_output_missing"
        error = "paper.pdf was not produced"
    elif final_counts["unresolved_warning_hits"] or final_counts["rerun_warning_hits"]:
        status = "fail"
        failure_category = "final_warning_debt"
        error = f"final unresolved={final_counts['unresolved_warning_hits']} rerun={final_counts['rerun_warning_hits']}"
    row = {
        "index": index,
        "path": source,
        "status": status,
        "failure_category": failure_category,
        "error": error,
        "returncode": rc,
        "seconds": round(elapsed, 3),
        "passes_completed": completed,
        "passes_requested": passes,
        "source_sha256": sha256_file(root / source),
        "latex_notice_lines": all_counts["latex_notice_lines"],
        "overfull_hbox": all_counts["overfull_hbox"],
        "underfull_hbox": all_counts["underfull_hbox"],
        "unresolved_warning_hits": all_counts["unresolved_warning_hits"],
        "final_unresolved_warning_hits": final_counts["unresolved_warning_hits"],
        "rerun_warning_hits": all_counts["rerun_warning_hits"],
        "final_rerun_warning_hits": final_counts["rerun_warning_hits"],
        "fatal_pattern_hits": all_counts["fatal_pattern_hits"],
        "pdf_output_created": pdf.exists() and pdf.stat().st_size > 0,
        "pdf_output_bytes": pdf.stat().st_size if pdf.exists() else 0,
        "pdf_sha256": "",
        "combined_log_bytes": 0,
        "combined_log_sha256": "",
        "final_log_bytes": 0,
        "final_log_sha256": "",
        "log_excerpt": "",
    }
    attach_compile_receipts(row, pdf_path=pdf, combined_log_text=combined, final_log_text=final_text, log_normalization_paths=[tmp, root], source_date_epoch=DEFAULT_SOURCE_DATE_EPOCH, pdf_trailer_id=stable_pdf_trailer_id(source, row.get("source_sha256", "")))
    if row["status"] == "pass" and digest_receipt_failures(row):
        row["status"] = "fail"
        row["failure_category"] = "compile_digest_receipt_missing"
        row["error"] = "PDF/log digest receipt fields are missing or malformed"
    if row["status"] == "pass" and reproducible_receipt_failures(row):
        row["status"] = "fail"
        row["failure_category"] = "compile_reproducible_receipt_missing"
        row["error"] = "deterministic normalized PDF/log receipt fields are missing or malformed"
    if row["status"] != "pass":
        row["log_excerpt"] = "\n".join(final_text.splitlines()[-36:])
    print(f"unqueued-compile-triage complete: target {index} {row['status']} {source}", file=sys.stderr, flush=True)
    return row


def build_report(root: pathlib.Path, rows: list[dict[str, Any]], *, partial: bool, start_index: int, max_targets: int, passes: int, timeout_seconds: int) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    all_sources = unqueued_sources(root)
    path_rows = {row["path"]: row for row in rows}
    ordered_rows = []
    for ordinal, path in enumerate(all_sources, 1):
        if path not in path_rows:
            continue
        row = dict(path_rows[path])
        row["index"] = ordinal
        ordered_rows.append(row)
    failed = [row for row in ordered_rows if row["status"] != "pass"]
    full_coverage = len(ordered_rows) == len(all_sources) and [row["path"] for row in ordered_rows] == all_sources
    summary = {
        "target_count_total": len(all_sources),
        "targets_checked": len(ordered_rows),
        "targets_passed": sum(1 for row in ordered_rows if row["status"] == "pass"),
        "targets_failed": len(failed),
        "passes_requested_per_target": passes,
        "short_pass_rows": sum(1 for row in ordered_rows if int(row.get("passes_completed", 0)) < MIN_REQUIRED_PASSES),
        "source_hash_mismatches": 0,
        "final_unresolved_warning_hits_total": sum(int(row.get("final_unresolved_warning_hits", 0)) for row in ordered_rows),
        "final_rerun_warning_hits_total": sum(int(row.get("final_rerun_warning_hits", 0)) for row in ordered_rows),
        "fatal_pattern_hits_total": sum(int(row.get("fatal_pattern_hits", 0)) for row in ordered_rows),
        "overfull_hbox_total": sum(int(row.get("overfull_hbox", 0)) for row in ordered_rows),
        "underfull_hbox_total": sum(int(row.get("underfull_hbox", 0)) for row in ordered_rows),
        "pdf_output_created_count": sum(1 for row in ordered_rows if row.get("pdf_output_created") is True and int(row.get("pdf_output_bytes", 0) or 0) > 0),
        "pdf_digest_present_count": sum(1 for row in ordered_rows if row.get("pdf_sha256")),
        "combined_log_digest_present_count": sum(1 for row in ordered_rows if row.get("combined_log_sha256")),
        "final_log_digest_present_count": sum(1 for row in ordered_rows if row.get("final_log_sha256")),
        "digest_receipt_count": sum(1 for row in ordered_rows if not digest_receipt_failures(row)),
        "digest_receipt_missing_count": digest_receipt_missing_count(ordered_rows),
        "reproducible_receipt_count": sum(1 for row in ordered_rows if not reproducible_receipt_failures(row)),
        "reproducible_receipt_missing_count": reproducible_receipt_missing_count(ordered_rows),
        "digest_receipts_required": True,
        "reproducible_receipts_required": True,
        "compile_receipt_policy": RECEIPT_POLICY_VERSION,
        "source_date_epoch": DEFAULT_SOURCE_DATE_EPOCH,
        "pdf_normalization_policy": PDF_NORMALIZATION_POLICY,
        "log_normalization_policy": LOG_NORMALIZATION_POLICY,
        "publication_authorized": False,
    }
    status = "pass" if full_coverage and not failed and summary["short_pass_rows"] == 0 and summary["final_unresolved_warning_hits_total"] == 0 and summary["final_rerun_warning_hits_total"] == 0 and summary["digest_receipt_missing_count"] == 0 and summary["reproducible_receipt_missing_count"] == 0 else "fail"
    if partial:
        status = "partial"
    return {
        "status": status,
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "report_kind": "unqueued_source_compile_triage",
        "partial": partial,
        "scope": {
            "source_rule": "series/**/paper.tex minus release_queue/QUEUE_INDEX.json states[*].source_tex",
            "start_index": start_index,
            "max_targets": max_targets,
            "target_count_total": len(all_sources),
            "target_paths_total": all_sources,
        },
        "command_family": r"pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -jobname <basename> -output-directory <tmpdir> \pdftrailerid{<stable><stable>}\input{<source_tex>}",
        "toolchain": {
            "latex_command": "pdflatex",
            **pdflatex_fingerprint(),
            "timeout_seconds_per_pass": timeout_seconds,
            "semantic_limit": "bounded three-pass compile triage for unqueued sources; not promotion or publication evidence",
        },
        "summary": summary,
        "failures": [{k: row.get(k, "") for k in ("path", "failure_category", "error", "returncode", "log_excerpt")} for row in failed],
        "results": ordered_rows,
        "fail_closed_rule": "Unqueued compile triage is not release evidence and does not authorize publication; failures mark source rot to repair before a source can enter the queue.",
    }


def _run_live_unlocked(root: pathlib.Path, start_index: int, max_targets: int, passes: int, timeout_seconds: int) -> dict[str, Any]:
    all_sources = unqueued_sources(root)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="anonymity_unqueued_compile_triage."))
    keep = os.environ.get("KEEP_UNQUEUED_COMPILE_TMP", "")
    try:
        rows = [compile_source(root, source, index, tmp, passes, timeout_seconds) for index, source in scoped_sources(all_sources, start_index, max_targets)]
        partial = not (start_index == 1 and (max_targets == 0 or max_targets >= len(all_sources)))
        return build_report(root, rows, partial=partial, start_index=start_index, max_targets=max_targets, passes=passes, timeout_seconds=timeout_seconds)
    finally:
        if keep:
            print(f"unqueued compile triage tmp retained: {tmp}", file=sys.stderr)
        else:
            shutil.rmtree(tmp, ignore_errors=True)



def run_live(root: pathlib.Path, start_index: int, max_targets: int, passes: int, timeout_seconds: int) -> dict[str, Any]:
    try:
        with live_compile_lock(root, "unqueued_compile_triage"):
            return _run_live_unlocked(root, start_index, max_targets, passes, timeout_seconds)
    except LiveCompileLockTimeout as exc:
        release = load_json(root / "RELEASE_MANIFEST.json")
        return {
            "status": "fail",
            "generated_for_revision": release["revision"],
            "checked_bundle": release["bundle"],
            "publication_authorized": False,
            "report_kind": "unqueued_source_compile_triage",
            "failure_category": "live_compile_lock_busy",
            "summary": {"checks_failed": 1, "publication_authorized": False},
            "failures": [{"category": "live_compile_lock_busy", "detail": str(exc)}],
            "fail_closed_rule": "If another live compile refresh is already running, stop instead of overlapping TeX processes.",
        }


def merge_reports(root: pathlib.Path, part_paths: list[pathlib.Path], passes: int, timeout_seconds: int) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    seen: set[int] = set()
    for path in part_paths:
        report = load_json(path)
        if report.get("report_kind") != "unqueued_source_compile_triage":
            raise SystemExit(f"not an unqueued compile triage report: {path}")
        for row in report.get("results", []):
            idx = int(row.get("index", 0))
            if idx in seen:
                raise SystemExit(f"duplicate unqueued compile triage index {idx} while merging {path}")
            seen.add(idx)
            rows.append(row)
    return build_report(root, rows, partial=False, start_index=1, max_targets=0, passes=passes, timeout_seconds=timeout_seconds)


def verify_report(root: pathlib.Path, report_path: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    report = load_json(report_path)
    expected_paths = unqueued_sources(root)
    failures: list[dict[str, Any]] = []
    rows = report.get("results", [])
    row_paths = [str(row.get("path")) for row in rows]
    duplicate_paths = sorted({path for path in row_paths if row_paths.count(path) > 1})
    row_indexes: list[int] = []
    malformed_indexes: list[dict[str, Any]] = []
    for row in rows:
        try:
            idx = int(row.get("index"))
            if idx < 1:
                raise ValueError
            row_indexes.append(idx)
        except (TypeError, ValueError):
            malformed_indexes.append({"path": str(row.get("path", "")), "index": row.get("index")})
    duplicate_indexes = sorted({idx for idx in row_indexes if row_indexes.count(idx) > 1})
    if report.get("status") != "pass":
        failures.append({"category": "stored_report_not_passing", "status": report.get("status")})
    if report.get("partial"):
        failures.append({"category": "stored_report_is_partial"})
    if report.get("generated_for_revision") != release["revision"]:
        failures.append({"category": "stored_report_revision_mismatch", "expected": release["revision"], "actual": report.get("generated_for_revision")})
    if report.get("checked_bundle") != release["bundle"]:
        failures.append({"category": "stored_report_bundle_mismatch", "expected": release["bundle"], "actual": report.get("checked_bundle")})
    if report.get("publication_authorized") is not False or report.get("summary", {}).get("publication_authorized") is not False:
        failures.append({"category": "stored_report_authorizes_publication"})
    if "-no-shell-escape" not in str(report.get("command_family", "")):
        failures.append({"category": "stored_report_missing_no_shell_escape_command_family"})
    if not report.get("toolchain", {}).get("toolchain_available"):
        failures.append({"category": "stored_report_missing_toolchain_availability"})
    if duplicate_paths:
        failures.append({"category": "stored_report_duplicate_paths", "paths": duplicate_paths})
    if duplicate_indexes or malformed_indexes:
        failures.append({"category": "stored_report_index_integrity_failure", "duplicate_indexes": duplicate_indexes[:50], "malformed_indexes": malformed_indexes[:25]})
    if row_paths != expected_paths:
        failures.append({"category": "stored_report_path_scope_mismatch", "expected_count": len(expected_paths), "actual_count": len(row_paths), "missing": sorted(set(expected_paths) - set(row_paths)), "extra": sorted(set(row_paths) - set(expected_paths))})
    stale_hashes = []
    short_passes = []
    nonpass = []
    final_warning_debt = []
    fatal_debt = []
    pdf_missing = []
    digest_missing = []
    reproducible_missing = []
    digest_required = True
    reproducible_required = True
    for row in rows:
        path = str(row.get("path", ""))
        if not path or not (root / path).exists():
            stale_hashes.append({"path": path, "expected": "missing", "actual": row.get("source_sha256")})
            continue
        expected_sha = sha256_file(root / path)
        if row.get("source_sha256") != expected_sha:
            stale_hashes.append({"path": path, "expected": expected_sha, "actual": row.get("source_sha256")})
        if row.get("status") != "pass":
            nonpass.append(path)
        if int(row.get("passes_completed", 0)) < MIN_REQUIRED_PASSES:
            short_passes.append(path)
        if int(row.get("final_unresolved_warning_hits", 0)) or int(row.get("final_rerun_warning_hits", 0)):
            final_warning_debt.append(path)
        if int(row.get("fatal_pattern_hits", 0)):
            fatal_debt.append(path)
        if row.get("pdf_output_created") is not True or int(row.get("pdf_output_bytes", 0) or 0) <= 0:
            pdf_missing.append(path)
        if digest_required and digest_receipt_failures(row):
            digest_missing.append(path)
        if reproducible_required and reproducible_receipt_failures(row):
            reproducible_missing.append(path)
    if stale_hashes:
        failures.append({"category": "stored_report_source_hash_mismatches", "count": len(stale_hashes), "rows": stale_hashes[:25]})
    if nonpass:
        failures.append({"category": "stored_report_nonpassing_rows", "paths": nonpass})
    if short_passes:
        failures.append({"category": "stored_report_short_pass_rows", "paths": short_passes})
    if final_warning_debt:
        failures.append({"category": "stored_report_final_warning_debt", "paths": final_warning_debt})
    if fatal_debt:
        failures.append({"category": "stored_report_fatal_pattern_debt", "paths": fatal_debt})
    if pdf_missing:
        failures.append({"category": "stored_report_pdf_output_evidence_missing", "paths": pdf_missing})
    if digest_missing:
        failures.append({"category": "stored_report_digest_receipts_missing", "paths": digest_missing})
    if reproducible_missing:
        failures.append({"category": "stored_report_reproducible_receipts_missing", "paths": reproducible_missing})
    stored_summary = report.get("summary", {}) if isinstance(report.get("summary", {}), dict) else {}
    if stored_summary.get("reproducible_receipt_count") != len(expected_paths) or int(stored_summary.get("reproducible_receipt_missing_count", -1)) != 0 or stored_summary.get("compile_receipt_policy") != RECEIPT_POLICY_VERSION:
        failures.append({"category": "stored_report_reproducible_receipt_summary_mismatch", "expected": len(expected_paths), "summary": {key: stored_summary.get(key) for key in ("reproducible_receipt_count", "reproducible_receipt_missing_count", "compile_receipt_policy")}})
    summary = {
        "checks_failed": len(failures),
        "target_count": len(expected_paths),
        "stored_result_count": len(rows),
        "duplicate_path_count": len(duplicate_paths),
        "duplicate_index_count": len(duplicate_indexes),
        "malformed_index_count": len(malformed_indexes),
        "stale_hash_count": len(stale_hashes),
        "nonpassing_row_count": len(nonpass),
        "short_pass_row_count": len(short_passes),
        "final_warning_debt_count": len(final_warning_debt),
        "fatal_pattern_debt_count": len(fatal_debt),
        "pdf_output_evidence_missing_count": len(pdf_missing),
        "digest_receipt_missing_count": len(digest_missing),
        "digest_receipts_required": digest_required,
        "reproducible_receipt_missing_count": len(reproducible_missing),
        "reproducible_receipts_required": reproducible_required,
        "publication_authorized": False,
    }
    return {
        "status": "pass" if not failures else "fail",
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "checked_report": report_path.relative_to(root).as_posix() if report_path.is_absolute() and root in report_path.parents else report_path.as_posix(),
        "failures": failures,
        "summary": summary,
        "fail_closed_rule": "If unqueued compile triage evidence is partial, stale, warning-debt-bearing, missing PDF/log digest evidence, or authorizing, default to no promotion and no publication.",
    }



def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    scope = report.get("scope", {}) if isinstance(report.get("scope"), dict) else {}
    lines = [
        "# Unqueued compile triage",
        "",
        f"Generated for revision: `{report.get('generated_for_revision', '')}`",
        f"Checked bundle: `{report.get('checked_bundle', '')}`",
        "Publication authorized: false",
        "",
        "This is build-hygiene evidence for sources outside Candidate, Published-ready, and Hold queue-note coverage. It does not promote any source and does not authorize publication.",
        "",
        "## Summary",
        "",
        f"- Status: **{report.get('status', '')}**",
        f"- Targets checked: {summary.get('targets_checked', 0)} / {summary.get('target_count_total', scope.get('target_count_total', 0))}",
        f"- Passed: {summary.get('targets_passed', 0)}",
        f"- Failed: {summary.get('targets_failed', 0)}",
        f"- Final unresolved/citation warnings: {summary.get('final_unresolved_warning_hits_total', 0)}",
        f"- Final rerun warnings: {summary.get('final_rerun_warning_hits_total', 0)}",
        f"- Fatal pattern hits: {summary.get('fatal_pattern_hits_total', 0)}",
        f"- PDF-output evidence missing: {summary.get('pdf_output_evidence_missing_count', 0)}",
        f"- Digest receipts present: {summary.get('digest_receipt_count', 0)}",
        f"- Digest receipts missing: {summary.get('digest_receipt_missing_count', 0)}",
        f"- Normalized deterministic receipts present: {summary.get('reproducible_receipt_count', 0)}",
        f"- Normalized deterministic receipts missing: {summary.get('reproducible_receipt_missing_count', 0)}",
        "",
        "## Scope",
        "",
        f"- Source rule: `{scope.get('source_rule', '')}`",
        "- Semantic limit: bounded compile triage only; not queue movement and not publication.",
        "",
    ]
    failures = report.get("failures", [])
    if failures:
        lines += ["## Failures", ""]
        for failure in failures[:25]:
            lines.append(f"- `{failure.get('path', '')}`: {failure.get('failure_category', '')} {failure.get('error', '')}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def safe_stdout_write(text: str) -> None:
    try:
        sys.stdout.write(text)
    except (BrokenPipeError, BlockingIOError):
        try:
            sys.stdout.close()
        except Exception:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--report-path", default="release_queue/UNQUEUED_COMPILE_TRIAGE.json")
    parser.add_argument("--write-report", default="")
    parser.add_argument("--write-md", default="")
    parser.add_argument("--run-live", action="store_true")
    parser.add_argument("--merge-parts", nargs="*", default=[])
    parser.add_argument("--start-index", type=int, default=1)
    parser.add_argument("--max-targets", type=int, default=0)
    parser.add_argument("--passes", type=int, default=MIN_REQUIRED_PASSES)
    parser.add_argument("--timeout-seconds", type=int, default=30)
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()
    report_path = root / args.report_path
    if args.run_live and args.merge_parts:
        raise SystemExit("choose either --run-live or --merge-parts, not both")
    if args.run_live:
        report = run_live(root, args.start_index, args.max_targets, args.passes, args.timeout_seconds)
    elif args.merge_parts:
        part_paths = [pathlib.Path(path) if pathlib.Path(path).is_absolute() else root / path for path in args.merge_parts]
        report = merge_reports(root, part_paths, args.passes, args.timeout_seconds)
    else:
        report = verify_report(root, report_path)
    text = json.dumps(report, indent=2) + "\n"
    out_arg = args.write_report
    if out_arg:
        out = pathlib.Path(out_arg)
        if not out.is_absolute():
            out = root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    if args.write_md:
        md_out = pathlib.Path(args.write_md)
        if not md_out.is_absolute():
            md_out = root / md_out
        md_out.parent.mkdir(parents=True, exist_ok=True)
        md_out.write_text(render_markdown(report), encoding="utf-8")
    safe_stdout_write(text)
    return 0 if report["status"] == "pass" else (0 if args.run_live and report["status"] == "partial" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
