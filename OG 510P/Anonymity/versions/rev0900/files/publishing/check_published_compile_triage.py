#!/usr/bin/env python3
"""Build and verify compile triage for shipped published/ TeX heads.

The published/ layer predates the current release queue and is intentionally not
part of the Candidate/Published-ready/Hold/unqueued series partition.  It still
contains public citation heads and repo-frozen source files, so this checker keeps
that layer source-hash-bound, three-pass TeX-clean, PDF-output-backed, and
explicitly non-authorizing.
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

from live_compile_lock import LiveCompileLockTimeout, live_compile_lock
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


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def published_sources(root: pathlib.Path) -> list[dict[str, str]]:
    classification = load_json(root / "published" / "publication_classification.json")
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    groups = [
        ("legacy_canonical_public_wiki_targets", "legacy_canonical_public_head"),
        ("repo_frozen_noncanonical_entries", "repo_frozen_noncanonical_entry"),
        ("new_post_policy_anonymity_entries", "new_post_policy_anonymity_entry"),
    ]
    for group_name, role in groups:
        for item in classification.get(group_name, []):
            if not isinstance(item, dict):
                continue
            path = str(item.get("path", "")).strip()
            if path and path not in seen:
                seen.add(path)
                rows.append({"path": path, "role": role, "title": str(item.get("wikilink") or item.get("title") or "")})
    return rows


def classification_failures(root: pathlib.Path, rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    listed = [row["path"] for row in rows]
    actual = sorted(path.relative_to(root).as_posix() for path in root.glob("published/**/paper.tex"))
    if sorted(listed) != actual:
        failures.append({
            "category": "published_tex_classification_mismatch",
            "missing_from_classification": sorted(set(actual) - set(listed)),
            "classified_but_missing_tex": sorted(set(listed) - set(actual)),
        })
    duplicates = sorted({path for path in listed if listed.count(path) > 1})
    if duplicates:
        failures.append({"category": "duplicate_published_source_classification", "paths": duplicates})
    for row in rows:
        path = root / row["path"]
        if not path.is_file():
            failures.append({"category": "published_source_missing", "path": row["path"]})
        elif path.name != "paper.tex":
            failures.append({"category": "published_source_not_canonical_paper_tex", "path": row["path"]})
    return failures


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


def run_pdflatex_once(root: pathlib.Path, source: str, outdir: pathlib.Path, log_path: pathlib.Path, timeout_seconds: int, label: str, *, draft_mode: bool = False) -> int:
    source_path = root / source
    source_sha256 = sha256_file(source_path) if source_path.is_file() else ""
    cmd = pdflatex_receipt_command("pdflatex", source, outdir, source_sha256=source_sha256, draft_mode=draft_mode)
    env = deterministic_compile_env(os.environ.copy())
    env["TZ"] = "UTC"
    deadline = time.monotonic() + max(1, timeout_seconds)
    last_heartbeat = time.monotonic()
    heartbeat_seconds = max(5, min(15, timeout_seconds // 2 if timeout_seconds > 1 else 1))
    with log_path.open("w", encoding="utf-8", errors="replace") as handle:
        try:
            proc = subprocess.Popen(cmd, cwd=root, stdout=handle, stderr=subprocess.STDOUT, text=True, env=env, start_new_session=True)
        except FileNotFoundError:
            handle.write("pdflatex not found on PATH\n")
            return 127
        while True:
            rc = proc.poll()
            if rc is not None:
                return rc
            now = time.monotonic()
            if now >= deadline:
                print(f"published-compile-triage timeout: {label}; terminating TeX process group", file=sys.stderr, flush=True)
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
            if now - last_heartbeat >= heartbeat_seconds:
                elapsed = int(now - (deadline - max(1, timeout_seconds)))
                print(f"published-compile-triage heartbeat: {label} running {elapsed}s", file=sys.stderr, flush=True)
                last_heartbeat = now
            time.sleep(0.25)


def compile_source(root: pathlib.Path, source: dict[str, str], index: int, tmp: pathlib.Path, passes: int, timeout_seconds: int) -> dict[str, Any]:
    path = source["path"]
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
        label = f"target {index} pass {pass_no}/{passes} {path}"
        print(f"published-compile-triage start: {label}", file=sys.stderr, flush=True)
        log_path = logs_dir / f"{index}.pass{pass_no}.log"
        rc = run_pdflatex_once(root, path, outdir, log_path, timeout_seconds, label, draft_mode=(pass_no < passes))
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
    pdf_exists = pdf.exists() and pdf.stat().st_size > 0
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
    elif not pdf_exists:
        status = "fail"
        failure_category = "pdf_output_missing"
        error = "paper.pdf was not produced"
    elif final_counts["unresolved_warning_hits"] or final_counts["rerun_warning_hits"]:
        status = "fail"
        failure_category = "final_warning_debt"
        error = f"final unresolved={final_counts['unresolved_warning_hits']} rerun={final_counts['rerun_warning_hits']}"
    row = {
        "index": index,
        "path": path,
        "role": source.get("role", ""),
        "title": source.get("title", ""),
        "status": status,
        "failure_category": failure_category,
        "error": error,
        "returncode": rc,
        "seconds": round(elapsed, 3),
        "passes_completed": completed,
        "passes_requested": passes,
        "source_sha256": sha256_file(root / path) if (root / path).is_file() else "",
        "pdf_output_created": pdf_exists,
        "pdf_output_bytes": pdf.stat().st_size if pdf.exists() else 0,
        "pdf_sha256": "",
        "combined_log_bytes": 0,
        "combined_log_sha256": "",
        "final_log_bytes": 0,
        "final_log_sha256": "",
        "latex_notice_lines": all_counts["latex_notice_lines"],
        "overfull_hbox": all_counts["overfull_hbox"],
        "underfull_hbox": all_counts["underfull_hbox"],
        "unresolved_warning_hits": all_counts["unresolved_warning_hits"],
        "rerun_warning_hits": all_counts["rerun_warning_hits"],
        "fatal_pattern_hits": all_counts["fatal_pattern_hits"],
        "final_latex_notice_lines": final_counts["latex_notice_lines"],
        "final_overfull_hbox": final_counts["overfull_hbox"],
        "final_underfull_hbox": final_counts["underfull_hbox"],
        "final_unresolved_warning_hits": final_counts["unresolved_warning_hits"],
        "final_rerun_warning_hits": final_counts["rerun_warning_hits"],
        "log_excerpt": "\n".join(final_text.splitlines()[-36:]) if status != "pass" else "",
    }
    attach_compile_receipts(row, pdf_path=pdf, combined_log_text=combined, final_log_text=final_text, log_normalization_paths=[tmp, root], source_date_epoch=DEFAULT_SOURCE_DATE_EPOCH, pdf_trailer_id=stable_pdf_trailer_id(path, row.get("source_sha256", "")))
    if row["status"] == "pass" and digest_receipt_failures(row):
        row["status"] = "fail"
        row["failure_category"] = "compile_digest_receipt_missing"
        row["error"] = "PDF/log digest receipt fields are missing or malformed"
    if row["status"] == "pass" and reproducible_receipt_failures(row):
        row["status"] = "fail"
        row["failure_category"] = "compile_reproducible_receipt_missing"
        row["error"] = "deterministic normalized PDF/log receipt fields are missing or malformed"
    print(f"published-compile-triage complete: target {index} {row['status']} {path}", file=sys.stderr, flush=True)
    return row


def scoped_sources(paths: list[dict[str, str]], start_index: int, max_targets: int) -> list[tuple[int, dict[str, str]]]:
    if start_index < 1:
        raise SystemExit("--start-index must be >= 1")
    if max_targets < 0:
        raise SystemExit("--max-targets must be >= 0")
    pairs = list(enumerate(paths, 1))[start_index - 1:]
    if max_targets:
        pairs = pairs[:max_targets]
    return pairs


def _row_int(row: dict[str, Any], key: str) -> int:
    try:
        return int(row.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0


def summary_metrics(rows: list[dict[str, Any]], total_count: int, passes: int) -> dict[str, Any]:
    failed = [row for row in rows if row.get("status") != "pass"]
    return {
        "checks_failed": 0,
        "targets_checked": len(rows),
        "target_count_total": total_count,
        "targets_passed": len(rows) - len(failed),
        "targets_failed": len(failed),
        "passes_requested_per_target": passes,
        "minimum_required_passes": MIN_REQUIRED_PASSES,
        "targets_with_short_pass_count": sum(1 for row in rows if _row_int(row, "passes_completed") < MIN_REQUIRED_PASSES),
        **pdflatex_fingerprint(),
        "latex_notice_lines_total": sum(_row_int(row, "latex_notice_lines") for row in rows),
        "latex_notice_lines_max_per_target": max([_row_int(row, "latex_notice_lines") for row in rows] or [0]),
        "overfull_hbox_total": sum(_row_int(row, "overfull_hbox") for row in rows),
        "overfull_hbox_max_per_target": max([_row_int(row, "overfull_hbox") for row in rows] or [0]),
        "underfull_hbox_total": sum(_row_int(row, "underfull_hbox") for row in rows),
        "underfull_hbox_max_per_target": max([_row_int(row, "underfull_hbox") for row in rows] or [0]),
        "unresolved_warning_hits_total": sum(_row_int(row, "unresolved_warning_hits") for row in rows),
        "unresolved_warning_hits_max_per_target": max([_row_int(row, "unresolved_warning_hits") for row in rows] or [0]),
        "rerun_warning_hits_total": sum(_row_int(row, "rerun_warning_hits") for row in rows),
        "rerun_warning_hits_max_per_target": max([_row_int(row, "rerun_warning_hits") for row in rows] or [0]),
        "fatal_pattern_hits_total": sum(_row_int(row, "fatal_pattern_hits") for row in rows),
        "fatal_pattern_hits_max_per_target": max([_row_int(row, "fatal_pattern_hits") for row in rows] or [0]),
        "final_latex_notice_lines_total": sum(_row_int(row, "final_latex_notice_lines") for row in rows),
        "final_latex_notice_lines_max_per_target": max([_row_int(row, "final_latex_notice_lines") for row in rows] or [0]),
        "final_overfull_hbox_total": sum(_row_int(row, "final_overfull_hbox") for row in rows),
        "final_overfull_hbox_max_per_target": max([_row_int(row, "final_overfull_hbox") for row in rows] or [0]),
        "final_underfull_hbox_total": sum(_row_int(row, "final_underfull_hbox") for row in rows),
        "final_underfull_hbox_max_per_target": max([_row_int(row, "final_underfull_hbox") for row in rows] or [0]),
        "final_unresolved_warning_hits_total": sum(_row_int(row, "final_unresolved_warning_hits") for row in rows),
        "final_unresolved_warning_hits_max_per_target": max([_row_int(row, "final_unresolved_warning_hits") for row in rows] or [0]),
        "final_rerun_warning_hits_total": sum(_row_int(row, "final_rerun_warning_hits") for row in rows),
        "final_rerun_warning_hits_max_per_target": max([_row_int(row, "final_rerun_warning_hits") for row in rows] or [0]),
        "pdf_output_created_count": sum(1 for row in rows if row.get("pdf_output_created") is True and _row_int(row, "pdf_output_bytes") > 0),
        "digest_receipt_count": sum(1 for row in rows if not digest_receipt_failures(row)),
        "digest_receipt_missing_count": digest_receipt_missing_count(rows),
        "reproducible_receipt_count": sum(1 for row in rows if not reproducible_receipt_failures(row)),
        "reproducible_receipt_missing_count": reproducible_receipt_missing_count(rows),
        "digest_receipts_required": True,
        "reproducible_receipts_required": True,
        "compile_receipt_policy": RECEIPT_POLICY_VERSION,
        "source_date_epoch": DEFAULT_SOURCE_DATE_EPOCH,
        "pdf_normalization_policy": PDF_NORMALIZATION_POLICY,
        "log_normalization_policy": LOG_NORMALIZATION_POLICY,
        "publication_authorized": False,
    }


def build_report(root: pathlib.Path, rows: list[dict[str, Any]], *, partial: bool, start_index: int, max_targets: int, passes: int, timeout_seconds: int) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    expected = published_sources(root)
    expected_paths = [row["path"] for row in expected]
    rows_by_path = {str(row.get("path")): row for row in rows}
    ordered_rows = [rows_by_path[path] for path in expected_paths if path in rows_by_path]
    full_coverage = len(ordered_rows) == len(expected_paths) and [row["path"] for row in ordered_rows] == expected_paths
    class_failures = classification_failures(root, expected)
    failed = [row for row in ordered_rows if row.get("status") != "pass"]
    summary = summary_metrics(ordered_rows, len(expected_paths), passes)
    roles: dict[str, int] = {}
    for row in expected:
        roles[row["role"]] = roles.get(row["role"], 0) + 1
    fail_count = len(class_failures) + len(failed)
    if not full_coverage:
        fail_count += 1
    if summary["targets_with_short_pass_count"]:
        fail_count += 1
    if summary["final_unresolved_warning_hits_total"] or summary["final_rerun_warning_hits_total"]:
        fail_count += 1
    if summary["pdf_output_created_count"] != len(ordered_rows):
        fail_count += 1
    if summary["digest_receipt_missing_count"] != 0 or summary["reproducible_receipt_missing_count"] != 0:
        fail_count += 1
    summary["checks_failed"] = fail_count
    status = "pass" if fail_count == 0 else "fail"
    if partial:
        status = "partial"
    return {
        "status": status,
        "generated_for_revision": release["revision"],
        "checked_bundle": release["bundle"],
        "publication_authorized": False,
        "report_kind": "published_tex_compile_triage",
        "partial": partial,
        "scope": {
            "source_rule": "published/publication_classification.json legacy_canonical_public_wiki_targets + repo_frozen_noncanonical_entries + new_post_policy_anonymity_entries",
            "classification_surface": "published/publication_classification.json",
            "target_count_total": len(expected_paths),
            "target_paths_total": expected_paths,
            "role_counts": roles,
            "start_index": start_index,
            "max_targets": max_targets,
        },
        "command_family": r"pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -jobname <basename> -output-directory <tmpdir> \pdftrailerid{<stable><stable>}\input{<published_tex>}",
        "toolchain": {
            "latex_command": "pdflatex",
            **pdflatex_fingerprint(),
            "timeout_seconds_per_pass": timeout_seconds,
            "semantic_limit": "bounded three-pass compile triage for already-shipped published TeX heads; not a new publication authorization",
        },
        "summary": summary,
        "failures": [*class_failures, *[{k: row.get(k, "") for k in ("path", "failure_category", "error", "returncode", "log_excerpt")} for row in failed]],
        "results": ordered_rows,
        "fail_closed_rule": "Published compile triage does not authorize new publication. If a legacy public head or repo-frozen published entry is stale, non-compiling, short-pass, PDF-missing, or final-warning-bearing, repair public-surface build hygiene before trusting published/ TeX heads.",
    }


def _run_live_unlocked(root: pathlib.Path, start_index: int, max_targets: int, passes: int, timeout_seconds: int) -> dict[str, Any]:
    all_sources = published_sources(root)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="anonymity_published_compile_triage."))
    keep = os.environ.get("KEEP_PUBLISHED_COMPILE_TMP", "")
    try:
        rows = [compile_source(root, source, index, tmp, passes, timeout_seconds) for index, source in scoped_sources(all_sources, start_index, max_targets)]
        partial = not (start_index == 1 and (max_targets == 0 or max_targets >= len(all_sources)))
        return build_report(root, rows, partial=partial, start_index=start_index, max_targets=max_targets, passes=passes, timeout_seconds=timeout_seconds)
    finally:
        if keep:
            print(f"published compile triage tmp retained: {tmp}", file=sys.stderr)
        else:
            shutil.rmtree(tmp, ignore_errors=True)



def run_live(root: pathlib.Path, start_index: int, max_targets: int, passes: int, timeout_seconds: int) -> dict[str, Any]:
    try:
        with live_compile_lock(root, "published_compile_triage"):
            return _run_live_unlocked(root, start_index, max_targets, passes, timeout_seconds)
    except LiveCompileLockTimeout as exc:
        release = load_json(root / "RELEASE_MANIFEST.json")
        return {
            "status": "fail",
            "generated_for_revision": release["revision"],
            "checked_bundle": release["bundle"],
            "publication_authorized": False,
            "report_kind": "published_tex_compile_triage",
            "failure_category": "live_compile_lock_busy",
            "summary": {"checks_failed": 1, "publication_authorized": False},
            "failures": [{"category": "live_compile_lock_busy", "detail": str(exc)}],
            "fail_closed_rule": "If another live compile refresh is already running, stop instead of overlapping TeX processes.",
        }


def merge_reports(root: pathlib.Path, part_paths: list[pathlib.Path], passes: int, timeout_seconds: int) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in part_paths:
        report = load_json(path)
        if report.get("report_kind") != "published_tex_compile_triage":
            raise SystemExit(f"not a published compile triage report: {path}")
        for row in report.get("results", []):
            source = str(row.get("path", ""))
            if source in seen:
                raise SystemExit(f"duplicate published compile triage path {source} while merging {path}")
            seen.add(source)
            rows.append(row)
    return build_report(root, rows, partial=False, start_index=1, max_targets=0, passes=passes, timeout_seconds=timeout_seconds)


def summary_consistency_failures(report: dict[str, Any], rows: list[dict[str, Any]], total_count: int) -> list[dict[str, Any]]:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    expected = summary_metrics(rows, total_count, _row_int(summary, "passes_requested_per_target") or MIN_REQUIRED_PASSES)
    failures: list[dict[str, Any]] = []
    for metric, expected_value in expected.items():
        if metric not in summary:
            failures.append({"category": "stored_report_summary_metric_missing", "metric": metric, "expected": expected_value})
        elif summary.get(metric) != expected_value:
            failures.append({"category": "stored_report_summary_metric_mismatch", "metric": metric, "expected": expected_value, "actual": summary.get(metric)})
    return failures


def verify_report(root: pathlib.Path, report_path: pathlib.Path) -> dict[str, Any]:
    release = load_json(root / "RELEASE_MANIFEST.json")
    expected_rows = published_sources(root)
    expected_paths = [row["path"] for row in expected_rows]
    expected_roles = {row["path"]: row["role"] for row in expected_rows}
    report = load_json(report_path)
    failures: list[dict[str, Any]] = classification_failures(root, expected_rows)
    rows = report.get("results", []) if isinstance(report.get("results"), list) else []
    row_paths = [str(row.get("path", "")) for row in rows if isinstance(row, dict)]
    duplicate_paths = sorted({path for path in row_paths if row_paths.count(path) > 1})
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
    if row_paths != expected_paths:
        failures.append({"category": "stored_report_path_scope_mismatch", "expected_count": len(expected_paths), "actual_count": len(row_paths), "missing": sorted(set(expected_paths) - set(row_paths)), "extra": sorted(set(row_paths) - set(expected_paths))})
    stale_hashes: list[dict[str, Any]] = []
    nonpass: list[str] = []
    short_passes: list[str] = []
    short_requested_passes: list[str] = []
    final_warning_debt: list[str] = []
    fatal_debt: list[str] = []
    missing_pdf_evidence: list[str] = []
    role_mismatches: list[dict[str, str]] = []
    row_index_mismatches: list[dict[str, Any]] = []
    digest_gaps: list[str] = []
    reproducible_gaps: list[str] = []
    for idx, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            failures.append({"category": "stored_report_row_not_object", "index": idx})
            continue
        path = str(row.get("path", ""))
        if path not in expected_roles:
            continue
        if row.get("role") != expected_roles[path]:
            role_mismatches.append({"path": path, "expected": expected_roles[path], "actual": str(row.get("role", ""))})
        try:
            actual_index = int(row.get("index", -1))
        except (TypeError, ValueError):
            actual_index = -1
        if actual_index != idx:
            row_index_mismatches.append({"path": path, "expected": idx, "actual": actual_index})
        source = root / path
        if not source.exists():
            stale_hashes.append({"path": path, "expected": "missing", "actual": row.get("source_sha256")})
            continue
        expected_sha = sha256_file(source)
        if row.get("source_sha256") != expected_sha:
            stale_hashes.append({"path": path, "expected": expected_sha, "actual": row.get("source_sha256")})
        if row.get("status") != "pass":
            nonpass.append(path)
        if _row_int(row, "passes_completed") < MIN_REQUIRED_PASSES:
            short_passes.append(path)
        if _row_int(row, "passes_requested") < MIN_REQUIRED_PASSES:
            short_requested_passes.append(path)
        if _row_int(row, "final_unresolved_warning_hits") or _row_int(row, "final_rerun_warning_hits"):
            final_warning_debt.append(path)
        if _row_int(row, "fatal_pattern_hits"):
            fatal_debt.append(path)
        if row.get("pdf_output_created") is not True or _row_int(row, "pdf_output_bytes") <= 0:
            missing_pdf_evidence.append(path)
        if digest_receipt_failures(row):
            digest_gaps.append(path)
        if reproducible_receipt_failures(row):
            reproducible_gaps.append(path)
    failures.extend(summary_consistency_failures(report, [row for row in rows if isinstance(row, dict)], len(expected_paths)))
    if stale_hashes:
        failures.append({"category": "stored_report_source_hash_mismatches", "count": len(stale_hashes), "rows": stale_hashes[:25]})
    if nonpass:
        failures.append({"category": "stored_report_nonpassing_rows", "paths": nonpass})
    if short_passes:
        failures.append({"category": "stored_report_short_pass_rows", "paths": short_passes})
    if short_requested_passes:
        failures.append({"category": "stored_report_short_requested_pass_rows", "paths": short_requested_passes})
    if final_warning_debt:
        failures.append({"category": "stored_report_final_warning_debt", "paths": final_warning_debt})
    if fatal_debt:
        failures.append({"category": "stored_report_fatal_pattern_debt", "paths": fatal_debt})
    if missing_pdf_evidence:
        failures.append({"category": "stored_report_pdf_output_evidence_missing", "paths": missing_pdf_evidence})
    if role_mismatches:
        failures.append({"category": "stored_report_role_mismatches", "rows": role_mismatches})
    if row_index_mismatches:
        failures.append({"category": "stored_report_row_index_mismatches", "rows": row_index_mismatches[:25]})
    if digest_gaps:
        failures.append({"category": "stored_report_digest_receipt_missing", "rows": digest_gaps[:25]})
    if reproducible_gaps:
        failures.append({"category": "stored_report_reproducible_receipt_missing", "rows": reproducible_gaps[:25]})
    summary = {
        "checks_failed": len(failures),
        "target_count": len(expected_paths),
        "stored_result_count": len(rows),
        "duplicate_path_count": len(duplicate_paths),
        "stale_hash_count": len(stale_hashes),
        "nonpassing_row_count": len(nonpass),
        "short_pass_row_count": len(short_passes),
        "short_requested_pass_row_count": len(short_requested_passes),
        "role_mismatch_count": len(role_mismatches),
        "row_index_mismatch_count": len(row_index_mismatches),
        "final_warning_debt_count": len(final_warning_debt),
        "fatal_pattern_debt_count": len(fatal_debt),
        "pdf_output_evidence_missing_count": len(missing_pdf_evidence),
        "digest_receipt_missing_count": len(digest_gaps),
        "reproducible_receipt_missing_count": len(reproducible_gaps),
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
        "fail_closed_rule": "If published compile triage evidence is partial, stale, warning-debt-bearing, summary-inconsistent, PDF-output-missing, digest-missing, role-divergent, or authorizing, treat published/ build hygiene as untrusted until repaired.",
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    lines = [
        "# Published TeX Compile Triage",
        "",
        f"Generated for revision: `{report.get('generated_for_revision')}`",
        f"Checked bundle: `{report.get('checked_bundle')}`",
        "Publication authorized: false",
        "",
        "This is build-rot triage for already-shipped `published/` source files only; it does not authorize a new publication or move queue states.",
        "",
        "## Summary",
        "",
        f"- Status: **{report.get('status')}**",
        f"- Targets checked: {summary.get('targets_checked')} / {summary.get('target_count_total')}",
        f"- Passed: {summary.get('targets_passed')}",
        f"- Failed: {summary.get('targets_failed')}",
        f"- Final unresolved/rerun warning debt: {summary.get('final_unresolved_warning_hits_total')} / {summary.get('final_rerun_warning_hits_total')}",
        f"- Final overfull/underfull hbox telemetry: {summary.get('final_overfull_hbox_total')} / {summary.get('final_underfull_hbox_total')}",
        f"- Aggregate overfull/underfull hbox telemetry: {summary.get('overfull_hbox_total')} / {summary.get('underfull_hbox_total')}",
        f"- PDF outputs recorded: {summary.get('pdf_output_created_count')}",
        f"- Normalized deterministic receipts present: {summary.get('reproducible_receipt_count')}",
        f"- Normalized deterministic receipts missing: {summary.get('reproducible_receipt_missing_count')}",
        "- Publication authorized: false",
        "",
        "## Results",
        "",
        "| # | Role | Source | Status | Passes | Final warnings | Final hbox | PDF SHA-256 |",
        "|---:|---|---|---|---:|---:|---:|---|",
    ]
    for row in report.get("results", []):
        if not isinstance(row, dict):
            continue
        pdf_sha = str(row.get("pdf_sha256", ""))
        pdf_short = f"`{pdf_sha[:16]}…`" if pdf_sha else ""
        lines.append(
            f"| {row.get('index')} | {row.get('role')} | `{row.get('path')}` | {row.get('status')} | "
            f"{row.get('passes_completed')}/{row.get('passes_requested')} | "
            f"{row.get('final_unresolved_warning_hits')}/{row.get('final_rerun_warning_hits')} | "
            f"{row.get('final_overfull_hbox')}/{row.get('final_underfull_hbox')} | {pdf_short} |"
        )
    lines.append("")
    return "\n".join(lines)



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
    parser.add_argument("--report-path", default="published/PUBLISHED_COMPILE_TRIAGE.json")
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
    if args.write_report:
        out = pathlib.Path(args.write_report)
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
