#!/usr/bin/env python3
"""Plan, ingest, run, and verify queue-scoped TeX compile-smoke evidence.

The shell runner delegates to this bounded Python runner so review containers can
compile in scoped windows with heartbeat output and process-group cleanup.  The
stored-report verifier is fail-closed for release-lane and Hold triage evidence:
it requires source-hash freshness, queue-note/order agreement, at least three
completed passes, no final unresolved/rerun warning debt, and explicit
``-no-shell-escape`` command evidence.
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

DEFAULT_STATES = ("published_ready", "candidate")
STATES = DEFAULT_STATES
STATE_DIRS = {"published_ready": "release_queue/published_ready", "candidate": "release_queue/candidates", "hold": "release_queue/hold"}
MIN_REQUIRED_PASSES = 3
NOTICE_RE = re.compile(r"(?:LaTeX|Package|Class|pdfTeX) .*?(?:Warning|Info|warning)", re.I)
OVER_RE = re.compile(r"Overfull \\hbox", re.I)
UNDER_RE = re.compile(r"Underfull \\hbox", re.I)
UNRESOLVED_RE = re.compile(
    r"(?:LaTeX Warning: (?:Citation|Reference).*undefined|"
    r"LaTeX Warning: There were undefined (?:references|citations)|"
    r"No file .*\\.(?:aux|bbl)|"
    r"Citation .* undefined|Reference .* undefined)",
    re.I,
)
RERUN_RE = re.compile(
    r"(?:Rerun to get cross-references right|Label\(s\) may have changed|"
    r"Package rerunfilecheck Warning: File .* has changed|Rerun to get outlines right)",
    re.I,
)
FATAL = ("! LaTeX Error:", "! Emergency stop.", "Fatal error occurred", " ==> Fatal error occurred")


def write_toolchain_fingerprint(tmp: pathlib.Path, latex: str) -> None:
    tool_path = shutil.which(latex) or ""
    (tmp / "toolchain.path").write_text(tool_path + ("\n" if tool_path else ""), encoding="utf-8")
    if tool_path:
        try:
            proc = subprocess.run([latex, "--version"], text=True, capture_output=True, timeout=5)
            version = proc.stdout if proc.stdout else proc.stderr
        except Exception as exc:  # pragma: no cover - defensive toolchain path
            version = f"{latex} --version failed: {exc}\n"
    else:
        version = ""
    (tmp / "toolchain.version").write_text(version, encoding="utf-8")


def append_file(dst: pathlib.Path, src: pathlib.Path) -> None:
    with dst.open("a", encoding="utf-8", errors="replace") as out:
        if src.exists():
            out.write(src.read_text(encoding="utf-8", errors="replace"))


def run_pdflatex_once(
    root: pathlib.Path,
    latex: str,
    source: str,
    outdir: pathlib.Path,
    pass_log: pathlib.Path,
    timeout_seconds: int,
    heartbeat_label: str = "",
    draft_mode: bool = False,
) -> int:
    """Run one pdflatex pass with timeout, process-group cleanup, and stderr heartbeat.

    The heartbeat is intentionally outside the TeX log file: it keeps short-lived
    cloudtainers from treating a legitimate long TeX pass as a dead silent job,
    while preserving the pass log as compiler output only.
    """
    source_path = root / source
    source_sha256 = sha(source_path) if source_path.is_file() else ""
    cmd = pdflatex_receipt_command(latex, source, outdir, source_sha256=source_sha256, draft_mode=draft_mode)
    env = deterministic_compile_env(os.environ.copy())
    env["TZ"] = "UTC"
    deadline = time.monotonic() + max(1, int(timeout_seconds))
    heartbeat_every = max(3, min(10, max(1, int(timeout_seconds) // 3)))
    last_heartbeat = time.monotonic()
    with pass_log.open("w", encoding="utf-8", errors="replace") as log_handle:
        if not root.is_dir():
            log_handle.write(f"compile root missing before pdflatex launch: {root}\n")
            return 126
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=root,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                start_new_session=True,
            )
        except FileNotFoundError as exc:
            if not root.is_dir():
                log_handle.write(f"compile root missing during pdflatex launch: {root}; {exc}\n")
                return 126
            log_handle.write(f"{latex} not found on PATH: {exc}\n")
            return 127
        while True:
            rc = proc.poll()
            if rc is not None:
                return rc
            now = time.monotonic()
            if now >= deadline:
                if heartbeat_label:
                    print(f"queue-compile-smoke timeout: {heartbeat_label}; terminating TeX process group", file=sys.stderr, flush=True)
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
            if heartbeat_label and now - last_heartbeat >= heartbeat_every:
                elapsed = int(round(now - (deadline - max(1, int(timeout_seconds)))))
                print(f"queue-compile-smoke heartbeat: {heartbeat_label} running {elapsed}s", file=sys.stderr, flush=True)
                last_heartbeat = now
            time.sleep(0.25)


def _run_live_unlocked(
    root: pathlib.Path,
    latex: str,
    timeout_seconds: int,
    passes: int,
    states: tuple[str, ...] | None = None,
    start_index: int = 1,
    max_targets: int = 0,
    include_paths: set[str] | None = None,
    run_dir: pathlib.Path | None = None,
) -> dict[str, Any]:
    tmp = run_dir.resolve() if run_dir is not None else pathlib.Path(tempfile.mkdtemp(prefix="anonymity_queue_compile_smoke."))
    keep_tmp = os.environ.get("KEEP_QUEUE_COMPILE_TMP", "") or run_dir is not None
    try:
        (tmp / "logs").mkdir(parents=True, exist_ok=True)
        (tmp / "out").mkdir(parents=True, exist_ok=True)
        write_plan(root, tmp / "plan.tsv", states=states, start_index=start_index, max_targets=max_targets, include_paths=include_paths)
        write_toolchain_fingerprint(tmp, latex)
        rows, _ = targets(root, states=states, start_index=start_index, max_targets=max_targets, include_paths=include_paths)
        total_targets = len(rows)
        for target_ordinal, item in enumerate(rows, 1):
            idx = int(item["index"])
            source = str(item["path"])
            print(f"queue-compile-smoke start: target {target_ordinal}/{total_targets} {source}", file=sys.stderr, flush=True)
            outdir_rel = f"out/{idx}"
            outdir = tmp / outdir_rel
            outdir.mkdir(parents=True, exist_ok=True)
            log_rel = f"logs/{idx}.log"
            log_path = tmp / log_rel
            log_path.write_text("", encoding="utf-8")
            pdf_rel = f"{outdir_rel}/{pathlib.Path(source).stem}.pdf"
            final_log_rel = f"logs/{idx}.pass0.log"
            rc = 0
            completed = 0
            start = time.monotonic()
            if not (tmp / "toolchain.path").read_text(encoding="utf-8", errors="replace").strip():
                log_path.write_text(f"{latex} not found on PATH\n", encoding="utf-8")
                (tmp / final_log_rel).write_text(f"{latex} not found on PATH\n", encoding="utf-8")
                rc = 127
            else:
                for pass_no in range(1, passes + 1):
                    pass_log_rel = f"logs/{idx}.pass{pass_no}.log"
                    pass_log = tmp / pass_log_rel
                    final_log_rel = pass_log_rel
                    with log_path.open("a", encoding="utf-8", errors="replace") as combined:
                        combined.write(f"=== pdflatex pass {pass_no}/{passes} for {source} ===\n")
                    heartbeat_label = f"target {target_ordinal}/{total_targets} pass {pass_no}/{passes} {source}"
                    rc = run_pdflatex_once(root, latex, source, outdir, pass_log, timeout_seconds, heartbeat_label, draft_mode=(pass_no < passes))
                    append_file(log_path, pass_log)
                    with log_path.open("a", encoding="utf-8", errors="replace") as combined:
                        combined.write(f"\n=== pdflatex pass {pass_no}/{passes} rc={rc} ===\n")
                    if rc != 0:
                        print(f"queue-compile-smoke stop: target {target_ordinal}/{total_targets} pass {pass_no}/{passes} rc={rc} {source}", file=sys.stderr, flush=True)
                        break
                    completed = pass_no
                    print(f"queue-compile-smoke pass-complete: target {target_ordinal}/{total_targets} pass {pass_no}/{passes} {source}", file=sys.stderr, flush=True)
            elapsed_ms = int(round((time.monotonic() - start) * 1000))
            print(f"queue-compile-smoke target-complete: target {target_ordinal}/{total_targets} rc={rc} completed={completed}/{passes} {source}", file=sys.stderr, flush=True)
            (tmp / f"result_{idx}.tsv").write_text(
                "\t".join([str(idx), source, str(rc), str(elapsed_ms), log_rel, pdf_rel, outdir_rel, str(completed), str(passes), final_log_rel]) + "\n",
                encoding="utf-8",
            )
            refresh_results_tsv(tmp)
        refresh_results_tsv(tmp)
        return build(root, tmp, latex, timeout_seconds, passes, states=states, start_index=start_index, max_targets=max_targets, include_paths=include_paths)
    finally:
        if keep_tmp:
            print(f"queue compile smoke tmp retained: {tmp}", file=sys.stderr)
        else:
            shutil.rmtree(tmp, ignore_errors=True)



def run_live(
    root: pathlib.Path,
    latex: str,
    timeout_seconds: int,
    passes: int,
    states: tuple[str, ...] | None = None,
    start_index: int = 1,
    max_targets: int = 0,
    include_paths: set[str] | None = None,
    run_dir: pathlib.Path | None = None,
) -> dict[str, Any]:
    try:
        with live_compile_lock(root, "queue_compile_smoke"):
            return _run_live_unlocked(root, latex, timeout_seconds, passes, states=states, start_index=start_index, max_targets=max_targets, include_paths=include_paths, run_dir=run_dir)
    except LiveCompileLockTimeout as exc:
        release = json.loads((root / "RELEASE_MANIFEST.json").read_text(encoding="utf-8"))
        return {
            "status": "fail",
            "generated_for_revision": release["revision"],
            "checked_bundle": release["bundle"],
            "publication_authorized": False,
            "report_kind": "queue_compile_smoke",
            "failure_category": "live_compile_lock_busy",
            "summary": {"checks_failed": 1, "publication_authorized": False},
            "failures": [{"category": "live_compile_lock_busy", "detail": str(exc)}],
            "fail_closed_rule": "If another live compile refresh is already running, stop instead of overlapping TeX processes.",
        }


def load(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def clean(x: Any) -> str:
    return str(x).replace("\t", " ").replace("\n", " ").replace("\r", " ").strip()


def parse_state_csv(raw: str) -> tuple[str, ...]:
    states = tuple(x.strip() for x in str(raw).split(",") if x.strip())
    if not states:
        raise SystemExit("--states must name at least one queue state")
    unknown = sorted(set(states) - set(STATE_DIRS))
    if unknown:
        raise SystemExit(f"unknown queue states: {', '.join(unknown)}")
    return states


def apply_target_scope(
    rows: list[dict[str, Any]],
    start_index: int = 1,
    max_targets: int = 0,
    include_paths: set[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    failures: list[dict[str, Any]] = []
    if start_index < 1:
        failures.append({"category": "invalid_start_index", "value": start_index})
        start_index = 1
    if max_targets < 0:
        failures.append({"category": "invalid_max_targets", "value": max_targets})
        max_targets = 0
    if include_paths:
        by_path = {str(r["path"]): r for r in rows}
        missing = sorted(include_paths - set(by_path))
        if missing:
            failures.append({"category": "include_path_not_in_selected_states", "paths": missing})
        scoped = [by_path[p] for p in sorted(include_paths & set(by_path), key=lambda p: int(by_path[p]["index"]))]
    else:
        start0 = start_index - 1
        scoped = rows[start0:]
        if max_targets:
            scoped = scoped[:max_targets]
    out=[]
    for i, row in enumerate(scoped, 1):
        clone = dict(row)
        clone["queue_order_index"] = clone["index"]
        clone["index"] = i
        out.append(clone)
    return out, failures


def targets(
    root: pathlib.Path,
    states: tuple[str, ...] | None = None,
    start_index: int = 1,
    max_targets: int = 0,
    include_paths: set[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected_states = states or DEFAULT_STATES
    q = load(root / "release_queue/QUEUE_INDEX.json")
    rows: list[dict[str, Any]] = []
    fails: list[dict[str, Any]] = []
    seen: set[str] = set()
    idx = 0
    for state in selected_states:
        arr = q.get("states", {}).get(state, [])
        if not isinstance(arr, list):
            fails.append({"category": "queue_state_not_list", "state": state})
            continue
        for item in arr:
            if not isinstance(item, dict):
                fails.append({"category": "queue_item_not_object", "state": state})
                continue
            src = str(item.get("source_tex", "")).strip()
            note = str(item.get("path", "")).strip()
            if not src:
                fails.append({"category": "missing_source_tex", "state": state, "queue_note": note})
                continue
            if src in seen:
                fails.append({"category": "duplicate_scoped_queue_source", "path": src, "queue_note": note})
                continue
            seen.add(src)
            idx += 1
            rows.append({
                "index": idx,
                "state": state,
                "path": src,
                "queue_note": note,
                "item_id": str(item.get("item_id", "")),
                "title": str(item.get("title", "")),
            })
    scoped, scope_failures = apply_target_scope(rows, start_index=start_index, max_targets=max_targets, include_paths=include_paths)
    return scoped, fails + scope_failures

def write_plan(
    root: pathlib.Path,
    out: pathlib.Path,
    states: tuple[str, ...] | None = None,
    start_index: int = 1,
    max_targets: int = 0,
    include_paths: set[str] | None = None,
) -> dict[str, Any]:
    rows, fails = targets(root, states=states, start_index=start_index, max_targets=max_targets, include_paths=include_paths)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        "".join("\t".join(clean(r[k]) for k in ("index", "path", "state", "queue_note", "item_id", "title")) + "\n" for r in rows),
        encoding="utf-8",
    )
    rel = load(root / "RELEASE_MANIFEST.json")
    return {
        "status": "pass" if not fails else "fail",
        "generated_for_revision": rel["revision"],
        "checked_bundle": rel["bundle"],
        "publication_authorized": False,
        "summary": {"checks_failed": len(fails), "target_count": len(rows)},
        "failures": fails,
    }

def refresh_results_tsv(tmp: pathlib.Path) -> None:
    """Rewrite results.tsv from durable per-target result_*.tsv rows.

    Outer cloudtainer timeouts can interrupt a long TeX chunk after some
    targets have already finished.  Each target result is written immediately,
    and --ingest-run-dir can later recover the completed rows instead of wasting
    the whole chunk.
    """
    result_lines: list[str] = []
    result_paths = sorted(
        tmp.glob("result_*.tsv"),
        key=lambda p: int(p.stem.split("_", 1)[1]) if p.stem.split("_", 1)[1].isdigit() else -1,
    )
    for result_path in result_paths:
        result_lines.append(result_path.read_text(encoding="utf-8"))
    (tmp / "results.tsv").write_text("".join(result_lines), encoding="utf-8")


def read_results(path: pathlib.Path) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    if not path.exists():
        refresh_results_tsv(path.parent)
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        p = line.split("\t")
        if len(p) < 7:
            continue
        try:
            idx = int(p[0])
            rc = int(p[2])
            ms = int(p[3])
            passes_completed = int(p[7]) if len(p) > 7 and p[7] else 0
            passes_requested = int(p[8]) if len(p) > 8 and p[8] else 1
        except ValueError:
            continue
        out[idx] = {
            "path": p[1],
            "returncode": rc,
            "elapsed_ms": ms,
            "log": p[4],
            "pdf": p[5],
            "outdir": p[6],
            "passes_completed": passes_completed,
            "passes_requested": passes_requested,
            "final_log": p[9] if len(p) > 9 else p[4],
        }
    return out


def counts(text: str) -> dict[str, int]:
    lines = text.splitlines()
    return {
        "latex_notice_lines": sum(1 for x in lines if NOTICE_RE.search(x)),
        "overfull_hbox": len(OVER_RE.findall(text)),
        "underfull_hbox": len(UNDER_RE.findall(text)),
        "unresolved_warning_hits": len(UNRESOLVED_RE.findall(text)),
        "rerun_warning_hits": len(RERUN_RE.findall(text)),
        "fatal_pattern_hits": sum(text.count(x) for x in FATAL),
    }


def row_from(root: pathlib.Path, tmp: pathlib.Path, t: dict[str, Any], rr: dict[str, Any] | None) -> dict[str, Any]:
    src = root / str(t["path"])
    row: dict[str, Any] = {
        "index": t["index"],
        "queue_order_index": t.get("queue_order_index", t["index"]),
        "state": t["state"],
        "queue_note": t["queue_note"],
        "path": t["path"],
        "title": t["title"],
        "item_id": t["item_id"],
        "status": "fail",
        "failure_category": "",
        "returncode": None,
        "seconds": 0.0,
        "passes_requested": 0,
        "passes_completed": 0,
        "source_sha256": sha(src) if src.is_file() else "",
        "latex_notice_lines": 0,
        "overfull_hbox": 0,
        "underfull_hbox": 0,
        "unresolved_warning_hits": 0,
        "final_unresolved_warning_hits": 0,
        "rerun_warning_hits": 0,
        "final_rerun_warning_hits": 0,
        "fatal_pattern_hits": 0,
        "pdf_output_created": False,
        "pdf_output_bytes": 0,
        "pdf_sha256": "",
        "combined_log_bytes": 0,
        "combined_log_sha256": "",
        "final_log_bytes": 0,
        "final_log_sha256": "",
        "error": "",
        "log_excerpt": "",
    }
    if not src.exists():
        row.update(failure_category="source_missing", error="source path does not exist")
        return row
    if src.name != "paper.tex":
        row.update(failure_category="source_not_canonical_paper_tex", error="source must be paper.tex")
        return row
    if rr is None:
        row.update(failure_category="missing_run_result", error="no shell result for source")
        return row

    logp = tmp / str(rr["log"])
    final_logp = tmp / str(rr.get("final_log") or rr["log"])
    pdfp = tmp / str(rr["pdf"])
    log = logp.read_text(encoding="utf-8", errors="replace") if logp.exists() else ""
    final_log = final_logp.read_text(encoding="utf-8", errors="replace") if final_logp.exists() else ""
    aggregate = counts(log)
    final = counts(final_log)
    row.update({k: aggregate[k] for k in ("latex_notice_lines", "overfull_hbox", "underfull_hbox", "unresolved_warning_hits", "rerun_warning_hits", "fatal_pattern_hits")})
    row["final_unresolved_warning_hits"] = final["unresolved_warning_hits"]
    row["final_rerun_warning_hits"] = final["rerun_warning_hits"]
    row["returncode"] = rr["returncode"]
    row["seconds"] = round(rr["elapsed_ms"] / 1000, 3)
    row["passes_requested"] = rr.get("passes_requested", 1)
    row["passes_completed"] = rr.get("passes_completed", 0)
    row["pdf_output_created"] = pdfp.is_file() and pdfp.stat().st_size > 0
    row["pdf_output_bytes"] = pdfp.stat().st_size if row["pdf_output_created"] else 0
    attach_compile_receipts(
        row,
        pdf_path=pdfp,
        combined_log_text=log,
        final_log_text=final_log,
        log_normalization_paths=[tmp, root],
        source_date_epoch=DEFAULT_SOURCE_DATE_EPOCH,
        pdf_trailer_id=stable_pdf_trailer_id(t["path"], row.get("source_sha256", "")),
    )

    if row["returncode"] != 0:
        row["failure_category"] = "pdflatex_timeout" if row["returncode"] in {124, 137, -15, -9} else "pdflatex_failed"
        row["error"] = f"pdflatex returned {row['returncode']}"
    elif row["passes_completed"] < min(MIN_REQUIRED_PASSES, row["passes_requested"]):
        row["failure_category"] = "pdflatex_pass_count_shortfall"
        row["error"] = f"completed {row['passes_completed']} of {row['passes_requested']} requested passes"
    elif not row["pdf_output_created"]:
        row["failure_category"] = "pdf_output_missing"
        row["error"] = "pdflatex returned zero but did not create a PDF"
    elif reproducible_receipt_failures(row):
        row["failure_category"] = "compile_reproducible_receipt_missing"
        row["error"] = "deterministic PDF/log receipt fields are missing or malformed: " + ", ".join(reproducible_receipt_failures(row)[:8])
    elif row["final_unresolved_warning_hits"]:
        row["failure_category"] = "final_unresolved_reference_or_citation_warning"
        row["error"] = f"final pass unresolved warnings: {row['final_unresolved_warning_hits']}"
    elif row["final_rerun_warning_hits"]:
        row["failure_category"] = "final_rerun_warning"
        row["error"] = f"final pass rerun warnings: {row['final_rerun_warning_hits']}"
    else:
        row["status"] = "pass"

    if row["status"] != "pass":
        excerpt_source = final_log if final_log else log
        row["log_excerpt"] = "\n".join(excerpt_source.splitlines()[-36:])
    return row



def _row_int(row: dict[str, Any], key: str) -> int:
    try:
        return int(row.get(key, 0) or 0)
    except (TypeError, ValueError):
        return 0


def stored_summary_consistency_failures(stored: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return fail-closed findings when stored summary telemetry disagrees with rows.

    Row-level hashes/pass/final-warning checks are the authority, but summary
    telemetry is what operators skim first.  A manually merged or partially
    refreshed compile report must not be allowed to keep stale totals or maxima.
    """
    summary = stored.get("summary", {}) if isinstance(stored.get("summary"), dict) else {}
    failures: list[dict[str, Any]] = []
    expected_metrics: dict[str, int] = {
        "targets_checked": len(rows),
        "targets_passed": sum(1 for row in rows if row.get("status") == "pass"),
        "targets_failed": sum(1 for row in rows if row.get("status") != "pass"),
        "targets_with_short_pass_count": sum(1 for row in rows if _row_int(row, "passes_completed") < MIN_REQUIRED_PASSES),
        "final_unresolved_warning_hits_total": sum(_row_int(row, "final_unresolved_warning_hits") for row in rows),
        "final_rerun_warning_hits_total": sum(_row_int(row, "final_rerun_warning_hits") for row in rows),
        "fatal_pattern_hits_total": sum(_row_int(row, "fatal_pattern_hits") for row in rows),
        "overfull_hbox_total": sum(_row_int(row, "overfull_hbox") for row in rows),
        "underfull_hbox_total": sum(_row_int(row, "underfull_hbox") for row in rows),
        "latex_notice_lines_total": sum(_row_int(row, "latex_notice_lines") for row in rows),
        "unresolved_warning_hits_total": sum(_row_int(row, "unresolved_warning_hits") for row in rows),
        "rerun_warning_hits_total": sum(_row_int(row, "rerun_warning_hits") for row in rows),
        "overfull_hbox_max_per_target": max([_row_int(row, "overfull_hbox") for row in rows] or [0]),
        "underfull_hbox_max_per_target": max([_row_int(row, "underfull_hbox") for row in rows] or [0]),
        "latex_notice_lines_max_per_target": max([_row_int(row, "latex_notice_lines") for row in rows] or [0]),
        "pdf_output_created_count": sum(1 for row in rows if row.get("pdf_output_created") is True and _row_int(row, "pdf_output_bytes") > 0),
        "digest_receipt_count": sum(1 for row in rows if not digest_receipt_failures(row)),
        "digest_receipt_missing_count": digest_receipt_missing_count(rows),
        "reproducible_receipt_count": sum(1 for row in rows if not reproducible_receipt_failures(row)),
        "reproducible_receipt_missing_count": reproducible_receipt_missing_count(rows),
    }
    for metric, expected in expected_metrics.items():
        if metric in summary and summary.get(metric) != expected:
            failures.append({"category": "stored_report_summary_metric_mismatch", "metric": metric, "expected": expected, "actual": summary.get(metric)})
    if summary.get("publication_authorized") is not False:
        failures.append({"category": "stored_report_summary_authorization_not_false", "actual": summary.get("publication_authorized")})
    if "minimum_required_passes" in summary and int(summary.get("minimum_required_passes", 0) or 0) != MIN_REQUIRED_PASSES:
        failures.append({"category": "stored_report_minimum_required_passes_mismatch", "expected": MIN_REQUIRED_PASSES, "actual": summary.get("minimum_required_passes")})
    if isinstance(summary.get("state_counts"), dict):
        expected_states: dict[str, dict[str, int]] = {}
        for row in rows:
            state = str(row.get("state", ""))
            bucket = expected_states.setdefault(state, {"expected": 0, "passed": 0, "failed": 0})
            bucket["expected"] += 1
            bucket["passed" if row.get("status") == "pass" else "failed"] += 1
        if summary.get("state_counts") != expected_states:
            failures.append({"category": "stored_report_state_counts_summary_mismatch", "expected": expected_states, "actual": summary.get("state_counts")})
    return failures

def tool(tmp: pathlib.Path) -> dict[str, Any]:
    p = (tmp / "toolchain.path").read_text(encoding="utf-8", errors="replace").strip() if (tmp / "toolchain.path").exists() else ""
    v = (tmp / "toolchain.version").read_text(encoding="utf-8", errors="replace") if (tmp / "toolchain.version").exists() else ""
    return {
        "pdflatex_path": p,
        "pdflatex_version_line": v.splitlines()[0][:200] if v.splitlines() else "",
        "pdflatex_version_output_sha256": hashlib.sha256(v.encode()).hexdigest() if v else "",
        "toolchain_available": bool(p),
    }


def build(
    root: pathlib.Path,
    tmp: pathlib.Path,
    latex: str,
    timeout: int,
    passes: int,
    states: tuple[str, ...] | None = None,
    start_index: int = 1,
    max_targets: int = 0,
    include_paths: set[str] | None = None,
) -> dict[str, Any]:
    rel = load(root / "RELEASE_MANIFEST.json")
    q = load(root / "release_queue/QUEUE_INDEX.json")
    ts, disc = targets(root, states=states, start_index=start_index, max_targets=max_targets, include_paths=include_paths)
    rr = read_results(tmp / "results.tsv")
    rows = [row_from(root, tmp, t, rr.get(int(t["index"]))) for t in ts]
    failed = [r for r in rows if r["status"] != "pass"]
    tc = tool(tmp)
    fails = list(disc)
    if not tc["toolchain_available"]:
        fails.append({"category": "pdflatex_missing", "detail": f"{latex} not found on PATH"})
    if passes < MIN_REQUIRED_PASSES:
        fails.append({"category": "insufficient_requested_passes", "requested": passes, "minimum": MIN_REQUIRED_PASSES})
    fails += [
        {
            "category": r["failure_category"],
            "state": r["state"],
            "path": r["path"],
            "queue_note": r["queue_note"],
            "error": r["error"],
            "returncode": r["returncode"],
            "log_excerpt": r["log_excerpt"],
        }
        for r in failed
    ]
    state_counts = {s: {"expected": 0, "passed": 0, "failed": 0} for s in (states or DEFAULT_STATES)}
    for t in ts:
        state_counts.setdefault(t["state"], {"expected": 0, "passed": 0, "failed": 0})["expected"] += 1
    for r in rows:
        state_counts.setdefault(r["state"], {"expected": 0, "passed": 0, "failed": 0})["passed" if r["status"] == "pass" else "failed"] += 1
    return {
        "status": "pass" if not fails and len(rows) == len(ts) else "fail",
        "generated_for_revision": rel["revision"],
        "checked_bundle": rel["bundle"],
        "publication_authorized": False,
        "report_kind": "generated_queue_compile_smoke_gate",
        "scope": {
            "checked_states": list(states or DEFAULT_STATES),
            "queue_dirs": [STATE_DIRS.get(s, f"release_queue/{s}") for s in (states or DEFAULT_STATES)],
            "target_window": {"start_index": start_index, "max_targets": max_targets, "include_paths": sorted(include_paths or [])},
            "source_index": "release_queue/QUEUE_INDEX.json",
            "unique_source_targets_expected": len(ts),
            "published_ready_targets": sum(1 for t in ts if t["state"] == "published_ready"),
            "candidate_targets": sum(1 for t in ts if t["state"] == "candidate"),
            "hold_targets": sum(1 for t in ts if t["state"] == "hold"),
        },
        "command_family": "pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -jobname <basename> -output-directory <tmpdir> \\pdftrailerid{<stable><stable>}\\input{<source_tex>}",
        "toolchain": {
            "latex_command": latex,
            **tc,
            "timeout_seconds_per_pass": timeout,
            "runner": "publishing/run_queue_compile_smoke.sh",
            "semantic_limit": "bounded three-pass compile smoke with final-pass unresolved-reference/rerun-warning rejection; not a full latexmk/bibliography publication build",
            "resumable_run_dir_ingest": "per-target result_*.tsv rows can be recovered with --ingest-run-dir after an outer cloudtainer timeout",
        },
        "summary": {
            "checks_failed": len(fails),
            "targets_expected": len(ts),
            "targets_checked": len(rows),
            "targets_passed": len(rows) - len(failed),
            "targets_failed": len(failed),
            "passes_requested_per_target": passes,
            "minimum_required_passes": MIN_REQUIRED_PASSES,
            "targets_with_short_pass_count": sum(1 for r in rows if int(r.get("passes_completed", 0)) < MIN_REQUIRED_PASSES),
            "state_counts": state_counts,
            "toolchain_available": tc["toolchain_available"],
            "latex_notice_lines_total": sum(int(r["latex_notice_lines"]) for r in rows),
            "latex_notice_lines_max_per_target": max([int(r["latex_notice_lines"]) for r in rows] or [0]),
            "overfull_hbox_total": sum(int(r["overfull_hbox"]) for r in rows),
            "overfull_hbox_max_per_target": max([int(r["overfull_hbox"]) for r in rows] or [0]),
            "underfull_hbox_total": sum(int(r["underfull_hbox"]) for r in rows),
            "unresolved_warning_hits_total": sum(int(r["unresolved_warning_hits"]) for r in rows),
            "final_unresolved_warning_hits_total": sum(int(r["final_unresolved_warning_hits"]) for r in rows),
            "rerun_warning_hits_total": sum(int(r["rerun_warning_hits"]) for r in rows),
            "final_rerun_warning_hits_total": sum(int(r["final_rerun_warning_hits"]) for r in rows),
            "fatal_pattern_hits_total": sum(int(r["fatal_pattern_hits"]) for r in rows),
            "pdf_output_created_count": sum(1 for r in rows if r.get("pdf_output_created") is True and int(r.get("pdf_output_bytes", 0) or 0) > 0),
            "pdf_digest_present_count": sum(1 for r in rows if r.get("pdf_sha256")),
            "combined_log_digest_present_count": sum(1 for r in rows if r.get("combined_log_sha256")),
            "final_log_digest_present_count": sum(1 for r in rows if r.get("final_log_sha256")),
            "digest_receipt_count": sum(1 for r in rows if not digest_receipt_failures(r)),
            "digest_receipt_missing_count": digest_receipt_missing_count(rows),
            "reproducible_receipt_count": sum(1 for r in rows if not reproducible_receipt_failures(r)),
            "reproducible_receipt_missing_count": reproducible_receipt_missing_count(rows),
            "digest_receipts_required": True,
            "reproducible_receipts_required": tuple(states or DEFAULT_STATES) in {DEFAULT_STATES, ("hold",)},
            "compile_receipt_policy": RECEIPT_POLICY_VERSION,
            "source_date_epoch": DEFAULT_SOURCE_DATE_EPOCH,
            "pdf_normalization_policy": PDF_NORMALIZATION_POLICY,
            "log_normalization_policy": LOG_NORMALIZATION_POLICY,
            "queue_posture_preserved": {
                "candidate": q.get("summary", {}).get("candidate"),
                "published_ready": q.get("summary", {}).get("published_ready"),
                "hold": q.get("summary", {}).get("hold"),
                "published": q.get("summary", {}).get("published", 0),
            },
            "publication_authorized": False,
        },
        "failures": fails[:50],
        "results": rows,
        "fail_closed_rule": "For the default release-lane scope, if any Candidate or Published-ready source fails this shell-run bounded three-pass compile smoke, default to no publication until repaired; for Hold-scoped triage, treat failures as rot to repair before any future promotion.",
    }


def merge_reports(
    root: pathlib.Path,
    part_paths: list[pathlib.Path],
    latex: str,
    timeout: int,
    passes: int,
    states: tuple[str, ...] | None = None,
    start_index: int = 1,
    max_targets: int = 0,
    include_paths: set[str] | None = None,
) -> dict[str, Any]:
    rel = load(root / "RELEASE_MANIFEST.json")
    q = load(root / "release_queue/QUEUE_INDEX.json")
    ts, disc = targets(root, states=states, start_index=start_index, max_targets=max_targets, include_paths=include_paths)
    expected_by_path = {str(t["path"]): t for t in ts}
    rows_by_path: dict[str, dict[str, Any]] = {}
    duplicate_paths: list[str] = []
    failures: list[dict[str, Any]] = list(disc)
    first_toolchain: dict[str, Any] = {}
    for part_path in part_paths:
        report = load(part_path)
        if report.get("report_kind") != "generated_queue_compile_smoke_gate":
            raise SystemExit(f"not a queue compile-smoke report: {part_path}")
        if report.get("publication_authorized") is not False:
            failures.append({"category": "merged_part_authorizes_publication", "path": str(part_path)})
        if report.get("toolchain") and not first_toolchain:
            first_toolchain = dict(report.get("toolchain", {}))
        for row in report.get("results", []):
            if not isinstance(row, dict):
                continue
            path = str(row.get("path", ""))
            if path in rows_by_path:
                duplicate_paths.append(path)
            rows_by_path[path] = row
    for path in duplicate_paths:
        failures.append({"category": "merged_part_duplicate_path", "path": path})
    missing = sorted(set(expected_by_path) - set(rows_by_path))
    extra = sorted(set(rows_by_path) - set(expected_by_path))
    if missing or extra:
        failures.append({"category": "merged_part_scope_mismatch", "missing": missing[:50], "extra": extra[:50]})
    rows = []
    for ordinal, t in enumerate(ts, 1):
        path = str(t["path"])
        if path not in rows_by_path:
            continue
        row = dict(rows_by_path[path])
        row["index"] = ordinal
        row["queue_order_index"] = int(t.get("queue_order_index", t["index"]))
        row["state"] = t.get("state")
        row["queue_note"] = t.get("queue_note")
        rows.append(row)
    failed = [r for r in rows if r.get("status") != "pass"]
    state_counts = {s: {"expected": 0, "passed": 0, "failed": 0} for s in (states or DEFAULT_STATES)}
    for t in ts:
        state_counts.setdefault(t["state"], {"expected": 0, "passed": 0, "failed": 0})["expected"] += 1
    for r in rows:
        state_counts.setdefault(str(r.get("state", "")), {"expected": 0, "passed": 0, "failed": 0})["passed" if r.get("status") == "pass" else "failed"] += 1
    if not first_toolchain:
        first_toolchain = {"latex_command": latex, "toolchain_available": bool(shutil.which(latex)), "timeout_seconds_per_pass": timeout, "runner": "publishing/run_queue_compile_smoke.sh"}
    summary = {
        "checks_failed": len(failures) + len(failed),
        "targets_expected": len(ts),
        "targets_checked": len(rows),
        "targets_passed": len(rows) - len(failed),
        "targets_failed": len(failed),
        "passes_requested_per_target": passes,
        "minimum_required_passes": MIN_REQUIRED_PASSES,
        "targets_with_short_pass_count": sum(1 for r in rows if int(r.get("passes_completed", 0) or 0) < MIN_REQUIRED_PASSES),
        "state_counts": state_counts,
        "toolchain_available": bool(first_toolchain.get("toolchain_available")),
        "latex_notice_lines_total": sum(int(r.get("latex_notice_lines", 0) or 0) for r in rows),
        "latex_notice_lines_max_per_target": max([int(r.get("latex_notice_lines", 0) or 0) for r in rows] or [0]),
        "overfull_hbox_total": sum(int(r.get("overfull_hbox", 0) or 0) for r in rows),
        "overfull_hbox_max_per_target": max([int(r.get("overfull_hbox", 0) or 0) for r in rows] or [0]),
        "underfull_hbox_total": sum(int(r.get("underfull_hbox", 0) or 0) for r in rows),
        "underfull_hbox_max_per_target": max([int(r.get("underfull_hbox", 0) or 0) for r in rows] or [0]),
        "unresolved_warning_hits_total": sum(int(r.get("unresolved_warning_hits", 0) or 0) for r in rows),
        "final_unresolved_warning_hits_total": sum(int(r.get("final_unresolved_warning_hits", 0) or 0) for r in rows),
        "rerun_warning_hits_total": sum(int(r.get("rerun_warning_hits", 0) or 0) for r in rows),
        "final_rerun_warning_hits_total": sum(int(r.get("final_rerun_warning_hits", 0) or 0) for r in rows),
        "fatal_pattern_hits_total": sum(int(r.get("fatal_pattern_hits", 0) or 0) for r in rows),
        "pdf_output_created_count": sum(1 for r in rows if r.get("pdf_output_created") is True and int(r.get("pdf_output_bytes", 0) or 0) > 0),
        "pdf_digest_present_count": sum(1 for r in rows if r.get("pdf_sha256")),
        "combined_log_digest_present_count": sum(1 for r in rows if r.get("combined_log_sha256")),
        "final_log_digest_present_count": sum(1 for r in rows if r.get("final_log_sha256")),
        "digest_receipt_count": sum(1 for r in rows if not digest_receipt_failures(r)),
        "digest_receipt_missing_count": digest_receipt_missing_count(rows),
        "reproducible_receipt_count": sum(1 for r in rows if not reproducible_receipt_failures(r)),
        "reproducible_receipt_missing_count": reproducible_receipt_missing_count(rows),
        "digest_receipts_required": True,
        "reproducible_receipts_required": tuple(states or DEFAULT_STATES) in {DEFAULT_STATES, ("hold",)},
        "compile_receipt_policy": RECEIPT_POLICY_VERSION,
        "source_date_epoch": DEFAULT_SOURCE_DATE_EPOCH,
        "pdf_normalization_policy": PDF_NORMALIZATION_POLICY,
        "log_normalization_policy": LOG_NORMALIZATION_POLICY,
        "queue_posture_preserved": {"candidate": q.get("summary", {}).get("candidate"), "published_ready": q.get("summary", {}).get("published_ready"), "hold": q.get("summary", {}).get("hold"), "published": q.get("summary", {}).get("published", 0)},
        "publication_authorized": False,
    }
    merge_failures = failures + [{"category": r.get("failure_category", "compile_failure"), "path": r.get("path"), "error": r.get("error", "")} for r in failed]
    if summary["digest_receipt_missing_count"]:
        merge_failures.append({"category": "merged_digest_receipts_missing", "count": summary["digest_receipt_missing_count"]})
    if tuple(states or DEFAULT_STATES) == DEFAULT_STATES and summary.get("reproducible_receipt_missing_count"):
        merge_failures.append({"category": "merged_reproducible_receipts_missing", "count": summary["reproducible_receipt_missing_count"]})
    return {
        "status": "pass" if not merge_failures and len(rows) == len(ts) else "fail",
        "generated_for_revision": rel["revision"],
        "checked_bundle": rel["bundle"],
        "publication_authorized": False,
        "report_kind": "generated_queue_compile_smoke_gate",
        "scope": {"checked_states": list(states or DEFAULT_STATES), "queue_dirs": [STATE_DIRS.get(s, f"release_queue/{s}") for s in (states or DEFAULT_STATES)], "target_window": {"start_index": start_index, "max_targets": max_targets, "include_paths": sorted(include_paths or [])}, "source_index": "release_queue/QUEUE_INDEX.json", "unique_source_targets_expected": len(ts), "published_ready_targets": sum(1 for t in ts if t["state"] == "published_ready"), "candidate_targets": sum(1 for t in ts if t["state"] == "candidate"), "hold_targets": sum(1 for t in ts if t["state"] == "hold"), "merged_part_count": len(part_paths)},
        "command_family": "pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -jobname <basename> -output-directory <tmpdir> \\pdftrailerid{<stable><stable>}\\input{<source_tex>}",
        "toolchain": {"latex_command": latex, **first_toolchain, "timeout_seconds_per_pass": timeout, "runner": "publishing/run_queue_compile_smoke.sh", "semantic_limit": "bounded three-pass compile smoke with final-pass unresolved-reference/rerun-warning rejection; not a full latexmk/bibliography publication build"},
        "summary": summary,
        "failures": merge_failures[:50],
        "results": rows,
        "fail_closed_rule": "Merged queue compile-smoke evidence must be complete, source-current, three-pass, no-shell-escape, final-warning-clean, PDF-output-backed, and PDF/log digest-receipt-backed; it remains non-authorizing.",
    }


def verify(
    root: pathlib.Path,
    report_rel: str,
    states: tuple[str, ...] | None = None,
    start_index: int = 1,
    max_targets: int = 0,
    include_paths: set[str] | None = None,
    require_digest_receipts: bool = False,
    require_reproducible_receipts: bool = False,
) -> dict[str, Any]:
    rel = load(root / "RELEASE_MANIFEST.json")
    ts, disc = targets(root, states=states, start_index=start_index, max_targets=max_targets, include_paths=include_paths)
    path = root / report_rel
    fails = list(disc)
    stored = load(path) if path.exists() else {}
    raw_results = stored.get("results", []) if isinstance(stored.get("results", []), list) else []
    by: dict[str, dict[str, Any]] = {}
    duplicate_paths: list[str] = []
    duplicate_indexes: list[int] = []
    malformed_indexes: list[dict[str, Any]] = []
    seen_indexes: dict[int, str] = {}
    for row in raw_results:
        if not isinstance(row, dict):
            continue
        row_path = str(row.get("path", ""))
        if not row_path:
            continue
        if row_path in by:
            duplicate_paths.append(row_path)
        by[row_path] = row
        try:
            row_index = int(row.get("index"))
            if row_index < 1:
                raise ValueError
        except (TypeError, ValueError):
            malformed_indexes.append({"path": row_path, "index": row.get("index")})
            continue
        if row_index in seen_indexes:
            duplicate_indexes.append(row_index)
        else:
            seen_indexes[row_index] = row_path
    summary_rows = [row for row in raw_results if isinstance(row, dict) and str(row.get("path", ""))]
    exp = {str(t["path"]) for t in ts}
    selected_states_for_digest = tuple(states or DEFAULT_STATES)
    digest_required = bool(
        require_digest_receipts
        or (
            start_index == 1
            and max_targets == 0
            and not include_paths
            and selected_states_for_digest in {DEFAULT_STATES, ("hold",)}
        )
        or (stored.get("summary", {}) if isinstance(stored.get("summary", {}), dict) else {}).get("digest_receipts_required") is True
    )
    reproducible_required = bool(
        require_reproducible_receipts
        or (str(report_rel).endswith("reports/queue_compile_smoke.json") and tuple(states or DEFAULT_STATES) == DEFAULT_STATES)
        or (stored.get("summary", {}) if isinstance(stored.get("summary", {}), dict) else {}).get("reproducible_receipts_required") is True
    )
    if stored:
        fails.extend(stored_summary_consistency_failures(stored, summary_rows))
    if not stored:
        fails.append({"category": "stored_report_missing", "path": report_rel})
    if duplicate_paths:
        fails.append({"category": "stored_report_duplicate_paths", "paths": sorted(set(duplicate_paths))[:50]})
    if duplicate_indexes:
        fails.append({"category": "stored_report_duplicate_row_indexes", "indexes": sorted(set(duplicate_indexes))[:50]})
    if malformed_indexes:
        fails.append({"category": "stored_report_malformed_row_indexes", "items": malformed_indexes[:50]})
    if stored.get("status") != "pass":
        fails.append({"category": "stored_report_status_not_pass", "value": stored.get("status")})
    if stored.get("generated_for_revision") != rel["revision"]:
        fails.append({"category": "stored_report_revision_mismatch", "value": stored.get("generated_for_revision"), "expected": rel["revision"]})
    if stored.get("checked_bundle") != rel["bundle"]:
        fails.append({"category": "stored_report_bundle_mismatch", "value": stored.get("checked_bundle"), "expected": rel["bundle"]})
    if stored.get("publication_authorized") is not False:
        fails.append({"category": "stored_report_authorization_not_false"})
    if set(by) != exp:
        fails.append({"category": "stored_report_target_set_mismatch", "missing": sorted(exp - set(by)), "extra": sorted(set(by) - exp)})
    command_family = str(stored.get("command_family", ""))
    if "-no-shell-escape" not in command_family:
        fails.append({"category": "stored_report_missing_no_shell_escape_command_family", "command_family": command_family[:200]})
    stale: list[str] = []
    nonpass: list[str] = []
    short_pass_count: list[str] = []
    final_warning_paths: list[str] = []
    pdf_missing_paths: list[str] = []
    digest_missing_paths: list[str] = []
    reproducible_missing_paths: list[str] = []
    state_mismatches: list[dict[str, Any]] = []
    queue_note_mismatches: list[dict[str, Any]] = []
    queue_order_mismatches: list[dict[str, Any]] = []
    for t in ts:
        r = by.get(t["path"])
        src = root / t["path"]
        if not r:
            continue
        if r.get("status") != "pass":
            nonpass.append(t["path"])
        if not src.is_file() or r.get("source_sha256") != sha(src):
            stale.append(t["path"])
        if int(r.get("passes_completed", 0)) < MIN_REQUIRED_PASSES:
            short_pass_count.append(t["path"])
        if int(r.get("final_unresolved_warning_hits", 0)) or int(r.get("final_rerun_warning_hits", 0)):
            final_warning_paths.append(t["path"])
        if r.get("pdf_output_created") is not True or int(r.get("pdf_output_bytes", 0) or 0) <= 0:
            pdf_missing_paths.append(t["path"])
        if digest_required and digest_receipt_failures(r):
            digest_missing_paths.append(t["path"])
        if reproducible_required and reproducible_receipt_failures(r):
            reproducible_missing_paths.append(t["path"])
        if r.get("state") != t.get("state"):
            state_mismatches.append({"path": t["path"], "expected": t.get("state"), "actual": r.get("state")})
        if r.get("queue_note") != t.get("queue_note"):
            queue_note_mismatches.append({"path": t["path"], "expected": t.get("queue_note"), "actual": r.get("queue_note")})
        expected_queue_order = int(t.get("queue_order_index", t["index"]))
        actual_queue_order = r.get("queue_order_index", r.get("index"))
        try:
            actual_queue_order_int = int(actual_queue_order)
        except (TypeError, ValueError):
            actual_queue_order_int = -1
        if actual_queue_order_int != expected_queue_order:
            queue_order_mismatches.append({"path": t["path"], "expected": expected_queue_order, "actual": actual_queue_order})
    if stale:
        fails.append({"category": "stored_report_source_hash_mismatch", "paths": stale[:50]})
    if nonpass:
        fails.append({"category": "stored_report_nonpassing_results", "paths": nonpass[:50]})
    if short_pass_count:
        fails.append({"category": "stored_report_insufficient_completed_passes", "paths": short_pass_count[:50], "minimum": MIN_REQUIRED_PASSES})
    if final_warning_paths:
        fails.append({"category": "stored_report_final_warnings_present", "paths": final_warning_paths[:50]})
    if pdf_missing_paths:
        fails.append({"category": "stored_report_pdf_output_evidence_missing", "paths": pdf_missing_paths[:50]})
    if digest_missing_paths:
        fails.append({"category": "stored_report_digest_receipts_missing", "paths": digest_missing_paths[:50], "count": len(digest_missing_paths)})
    if reproducible_missing_paths:
        fails.append({"category": "stored_report_reproducible_receipts_missing", "paths": reproducible_missing_paths[:50], "count": len(reproducible_missing_paths)})
    if state_mismatches:
        fails.append({"category": "stored_report_state_mismatches", "items": state_mismatches[:50]})
    if queue_note_mismatches:
        fails.append({"category": "stored_report_queue_note_mismatches", "items": queue_note_mismatches[:50]})
    if queue_order_mismatches:
        fails.append({"category": "stored_report_queue_order_mismatches", "items": queue_order_mismatches[:50]})
    s = stored.get("summary", {}) if isinstance(stored.get("summary"), dict) else {}
    tc = stored.get("toolchain", {}) if isinstance(stored.get("toolchain"), dict) else {}
    toolchain_available = s.get("toolchain_available", tc.get("toolchain_available"))
    if s.get("targets_checked") != len(ts) or s.get("targets_failed") != 0 or s.get("targets_passed") != len(ts):
        fails.append({"category": "stored_report_summary_counts_mismatch", "summary": s, "expected_targets": len(ts)})
    if toolchain_available is not True:
        fails.append({"category": "stored_report_toolchain_not_available", "summary_value": s.get("toolchain_available"), "toolchain_value": tc.get("toolchain_available")})
    if int(s.get("passes_requested_per_target", 0)) < MIN_REQUIRED_PASSES:
        fails.append({"category": "stored_report_insufficient_requested_passes", "value": s.get("passes_requested_per_target"), "minimum": MIN_REQUIRED_PASSES})
    if int(s.get("final_unresolved_warning_hits_total", 0)) or int(s.get("final_rerun_warning_hits_total", 0)):
        fails.append({"category": "stored_report_final_warning_totals_nonzero", "final_unresolved": s.get("final_unresolved_warning_hits_total"), "final_rerun": s.get("final_rerun_warning_hits_total")})
    if digest_required and (s.get("pdf_output_created_count") != len(ts) or s.get("digest_receipt_count") != len(ts) or int(s.get("digest_receipt_missing_count", -1)) != 0):
        fails.append({"category": "stored_report_digest_receipt_summary_mismatch", "expected": len(ts), "summary": {k: s.get(k) for k in ("pdf_output_created_count", "digest_receipt_count", "digest_receipt_missing_count")}})
    if reproducible_required and (s.get("reproducible_receipt_count") != len(ts) or int(s.get("reproducible_receipt_missing_count", -1)) != 0 or s.get("compile_receipt_policy") != RECEIPT_POLICY_VERSION):
        fails.append({"category": "stored_report_reproducible_receipt_summary_mismatch", "expected": len(ts), "summary": {k: s.get(k) for k in ("reproducible_receipt_count", "reproducible_receipt_missing_count", "compile_receipt_policy")}})
    return {
        "status": "pass" if not fails else "fail",
        "generated_for_revision": rel["revision"],
        "checked_bundle": rel["bundle"],
        "publication_authorized": False,
        "report_kind": "queue_compile_smoke_stored_report_verifier",
        "stored_report": report_rel,
        "verified_states": list(states or DEFAULT_STATES),
        "summary": {
            "checks_failed": len(fails),
            "expected_targets": len(ts),
            "stored_result_count": len(by),
            "duplicate_stored_path_count": len(set(duplicate_paths)),
            "duplicate_stored_index_count": len(set(duplicate_indexes)),
            "malformed_stored_index_count": len(malformed_indexes),
            "source_hash_mismatch_count": len(stale),
            "nonpassing_result_count": len(nonpass),
            "short_pass_count": len(short_pass_count),
            "final_warning_path_count": len(final_warning_paths),
            "pdf_output_evidence_missing_count": len(pdf_missing_paths),
            "digest_receipt_missing_count": len(digest_missing_paths),
            "digest_receipts_required": digest_required,
            "reproducible_receipt_missing_count": len(reproducible_missing_paths),
            "reproducible_receipts_required": reproducible_required,
            "state_mismatch_count": len(state_mismatches),
            "queue_note_mismatch_count": len(queue_note_mismatches),
            "queue_order_mismatch_count": len(queue_order_mismatches),
            "toolchain_available": toolchain_available is True,
        },
        "failures": fails[:50],
        "fail_closed_rule": "If the stored queue compile-smoke report is stale, incomplete, not three-pass, missing no-shell-escape/PDF-output evidence, duplicate-indexed, queue-order divergent, or nonpassing, rerun publishing/run_queue_compile_smoke.sh before trusting buildability evidence.",
    }



def safe_stdout_write(text: str) -> None:
    try:
        sys.stdout.write(text)
    except (BrokenPipeError, BlockingIOError):
        try:
            sys.stdout.close()
        except Exception:
            pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--write-report", default="")
    ap.add_argument("--report-path", default="reports/queue_compile_smoke.json")
    ap.add_argument("--emit-plan-tsv", default="")
    ap.add_argument("--ingest-run-dir", default="")
    ap.add_argument("--latex-command", default="pdflatex")
    ap.add_argument("--timeout-seconds", type=int, default=30)
    ap.add_argument("--passes", type=int, default=MIN_REQUIRED_PASSES)
    ap.add_argument("--states", default=",".join(DEFAULT_STATES), help="comma-separated queue states to compile or verify; default is release lane")
    ap.add_argument("--start-index", type=int, default=1, help="1-based start within the selected state order for bounded triage")
    ap.add_argument("--max-targets", type=int, default=0, help="maximum targets to include; 0 means no limit")
    ap.add_argument("--include-path", action="append", default=[], help="exact source_tex path to include; may be repeated and overrides start/max window")
    ap.add_argument("--run-live", action="store_true", help="run the compile gate directly, writing tmp logs/results and ingesting them")
    ap.add_argument("--run-dir", default="", help="optional durable run directory for live compile logs/results; enables later --ingest-run-dir recovery")
    ap.add_argument("--merge-parts", nargs="*", default=[], help="merge bounded live queue compile-smoke part reports into one scoped report")
    ap.add_argument("--require-digest-receipts", action="store_true", help="stored-report verification must require PDF/log digest receipts even for scoped evidence")
    ap.add_argument("--require-reproducible-receipts", action="store_true", help="stored-report verification must require deterministic normalized PDF/log receipt fields")
    a = ap.parse_args()
    root = pathlib.Path(a.root).resolve()
    selected_states = parse_state_csv(a.states)
    include_paths = set(a.include_path or []) or None
    if a.run_live and a.merge_parts:
        raise SystemExit("choose either --run-live or --merge-parts, not both")
    if a.run_live:
        run_dir = pathlib.Path(a.run_dir) if a.run_dir else None
        rep = run_live(root, a.latex_command, a.timeout_seconds, a.passes, states=selected_states, start_index=a.start_index, max_targets=a.max_targets, include_paths=include_paths, run_dir=run_dir)
    elif a.merge_parts:
        part_paths = [pathlib.Path(path) if pathlib.Path(path).is_absolute() else root / path for path in a.merge_parts]
        rep = merge_reports(root, part_paths, a.latex_command, a.timeout_seconds, a.passes, states=selected_states, start_index=a.start_index, max_targets=a.max_targets, include_paths=include_paths)
    elif a.emit_plan_tsv:
        rep = write_plan(root, pathlib.Path(a.emit_plan_tsv), states=selected_states, start_index=a.start_index, max_targets=a.max_targets, include_paths=include_paths)
    elif a.ingest_run_dir:
        rep = build(root, pathlib.Path(a.ingest_run_dir).resolve(), a.latex_command, a.timeout_seconds, a.passes, states=selected_states, start_index=a.start_index, max_targets=a.max_targets, include_paths=include_paths)
    else:
        rep = verify(root, a.report_path, states=selected_states, start_index=a.start_index, max_targets=a.max_targets, include_paths=include_paths, require_digest_receipts=a.require_digest_receipts, require_reproducible_receipts=a.require_reproducible_receipts)
    text = json.dumps(rep, indent=2) + "\n"
    if a.write_report:
        out = root / a.write_report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    safe_stdout_write(text)
    return 0 if rep.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
