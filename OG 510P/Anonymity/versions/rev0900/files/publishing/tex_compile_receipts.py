#!/usr/bin/env python3
"""Compact and reproducible PDF/log digest receipts for TeX compile evidence.

Compile-triage reports deliberately do not ship transient PDFs or TeX logs.  The
legacy receipt fields retain byte counts and SHA-256 digests for the PDF, the
combined multi-pass log, and the final-pass log.  rev0850 adds deterministic
helpers and self-tests for future compile refreshes: stable pdfTeX trailer IDs,
SOURCE_DATE_EPOCH pinning, normalized log digests, and normalized PDF digests
that ignore pdfTeX variable trailer/date metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import pathlib
import re
import sys
from typing import Any, Iterable

HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
RECEIPT_DIGEST_KEYS = ("pdf_sha256", "combined_log_sha256", "final_log_sha256")
RECEIPT_BYTE_KEYS = ("pdf_output_bytes", "combined_log_bytes", "final_log_bytes")
REPRODUCIBLE_DIGEST_KEYS = ("normalized_pdf_sha256", "normalized_combined_log_sha256", "normalized_final_log_sha256")
REPRODUCIBLE_BYTE_KEYS = ("normalized_pdf_bytes", "normalized_combined_log_bytes", "normalized_final_log_bytes")
RECEIPT_POLICY_VERSION = "tex_compile_receipt_v2_deterministic_pdf_normalized_log"
DEFAULT_SOURCE_DATE_EPOCH = "1700000000"
PDF_NORMALIZATION_POLICY = "normalize-pdftex-trailer-id-and-dates-v1"
LOG_NORMALIZATION_POLICY = "normalize-volatile-compile-paths-v1"
PDF_ID_RE = re.compile(rb"/ID\s*\[\s*<[^>]*>\s*<[^>]*>\s*\]")
PDF_DATE_RE = re.compile(rb"/(CreationDate|ModDate)\s*\((?:\\.|[^\\)])*\)")


def _digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_file(path: pathlib.Path) -> bytes:
    return path.read_bytes() if path.exists() and path.is_file() else b""


def stable_pdf_trailer_id(source_path: str | pathlib.Path, source_sha256: str = "") -> str:
    seed = f"{pathlib.Path(source_path).as_posix()}\n{source_sha256}\n{RECEIPT_POLICY_VERSION}\n".encode("utf-8", errors="replace")
    return hashlib.sha256(seed).hexdigest()


def deterministic_compile_env(base: dict[str, str] | None = None, *, source_date_epoch: str = DEFAULT_SOURCE_DATE_EPOCH) -> dict[str, str]:
    env = dict(base or os.environ)
    env["SOURCE_DATE_EPOCH"] = str(source_date_epoch)
    env["FORCE_SOURCE_DATE"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def pdflatex_receipt_command(
    latex: str,
    source_path: str | pathlib.Path,
    outdir: str | pathlib.Path,
    *,
    source_sha256: str = "",
    draft_mode: bool = False,
) -> list[str]:
    source = pathlib.Path(source_path).as_posix()
    ident = stable_pdf_trailer_id(source, source_sha256)
    jobname = pathlib.Path(source_path).stem or "texput"
    injected = rf"\pdftrailerid{{<{ident}><{ident}>}}\input{{{source}}}"
    cmd = [latex, "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error", "-file-line-error"]
    if draft_mode:
        cmd.append("-draftmode")
    cmd.extend(["-jobname", jobname, "-output-directory", str(outdir), injected])
    return cmd


def normalize_tex_log_text(text: str, volatile_paths: Iterable[str | pathlib.Path] = ()) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    for raw in volatile_paths:
        p = pathlib.Path(raw).as_posix() if raw is not None else ""
        if p:
            normalized = normalized.replace(p, "<VOLATILE_PATH>")
            normalized = normalized.replace(str(raw), "<VOLATILE_PATH>")
    tmp_prefix = "/" + "tmp" + "/"
    normalized = re.sub(re.escape(tmp_prefix) + r"[A-Za-z0-9_.\-/]+", "<TMP_PATH>", normalized)
    normalized = re.sub(r"Temporary directory: .+", "Temporary directory: <TMP_PATH>", normalized)
    return normalized


def normalize_pdf_bytes(pdf_bytes: bytes) -> bytes:
    data = PDF_ID_RE.sub(b"/ID [<PDFTEX-STABLE-ID><PDFTEX-STABLE-ID>]", pdf_bytes)
    data = PDF_DATE_RE.sub(lambda m: b"/" + m.group(1) + b"(D:SOURCE_DATE_EPOCH)", data)
    return data


def attach_compile_receipts(
    row: dict[str, Any],
    *,
    pdf_path: pathlib.Path,
    combined_log_path: pathlib.Path | None = None,
    final_log_path: pathlib.Path | None = None,
    combined_log_text: str | None = None,
    final_log_text: str | None = None,
    log_normalization_paths: Iterable[str | pathlib.Path] = (),
    receipt_policy: str = RECEIPT_POLICY_VERSION,
    source_date_epoch: str = DEFAULT_SOURCE_DATE_EPOCH,
    pdf_trailer_id: str = "",
) -> dict[str, Any]:
    pdf_bytes = _read_file(pdf_path)
    if combined_log_text is not None:
        combined_bytes = combined_log_text.encode("utf-8", errors="replace")
        normalized_combined = normalize_tex_log_text(combined_log_text, log_normalization_paths).encode("utf-8", errors="replace")
    else:
        combined_bytes = _read_file(combined_log_path) if combined_log_path is not None else b""
        normalized_combined = combined_bytes
    if final_log_text is not None:
        final_bytes = final_log_text.encode("utf-8", errors="replace")
        normalized_final = normalize_tex_log_text(final_log_text, log_normalization_paths).encode("utf-8", errors="replace")
    else:
        final_bytes = _read_file(final_log_path) if final_log_path is not None else b""
        normalized_final = final_bytes
    normalized_pdf = normalize_pdf_bytes(pdf_bytes) if pdf_bytes else b""
    row["pdf_output_created"] = bool(pdf_bytes)
    row["pdf_output_bytes"] = len(pdf_bytes)
    row["pdf_sha256"] = _digest_bytes(pdf_bytes) if pdf_bytes else ""
    row["combined_log_bytes"] = len(combined_bytes)
    row["combined_log_sha256"] = _digest_bytes(combined_bytes) if combined_bytes else ""
    row["final_log_bytes"] = len(final_bytes)
    row["final_log_sha256"] = _digest_bytes(final_bytes) if final_bytes else ""
    row["compile_receipt_policy"] = receipt_policy
    row["source_date_epoch"] = str(source_date_epoch)
    row["force_source_date"] = True
    row["pdf_trailer_id"] = pdf_trailer_id
    row["pdf_normalization_policy"] = PDF_NORMALIZATION_POLICY
    row["log_normalization_policy"] = LOG_NORMALIZATION_POLICY
    row["normalized_pdf_bytes"] = len(normalized_pdf)
    row["normalized_pdf_sha256"] = _digest_bytes(normalized_pdf) if normalized_pdf else ""
    row["normalized_combined_log_bytes"] = len(normalized_combined)
    row["normalized_combined_log_sha256"] = _digest_bytes(normalized_combined) if normalized_combined else ""
    row["normalized_final_log_bytes"] = len(normalized_final)
    row["normalized_final_log_sha256"] = _digest_bytes(normalized_final) if normalized_final else ""
    return row


def digest_receipt_failures(row: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if row.get("pdf_output_created") is not True:
        failures.append("pdf_output_created")
    for key in RECEIPT_BYTE_KEYS:
        try:
            if int(row.get(key, 0) or 0) <= 0:
                failures.append(key)
        except (TypeError, ValueError):
            failures.append(key)
    for key in RECEIPT_DIGEST_KEYS:
        value = row.get(key)
        if not isinstance(value, str) or not HEX64_RE.fullmatch(value):
            failures.append(key)
    return failures


def reproducible_receipt_failures(row: dict[str, Any]) -> list[str]:
    failures = digest_receipt_failures(row)
    if row.get("compile_receipt_policy") != RECEIPT_POLICY_VERSION:
        failures.append("compile_receipt_policy")
    source_epoch = str(row.get("source_date_epoch", ""))
    if not source_epoch.isdigit():
        failures.append("source_date_epoch")
    if row.get("force_source_date") is not True:
        failures.append("force_source_date")
    if row.get("pdf_normalization_policy") != PDF_NORMALIZATION_POLICY:
        failures.append("pdf_normalization_policy")
    if row.get("log_normalization_policy") != LOG_NORMALIZATION_POLICY:
        failures.append("log_normalization_policy")
    for key in REPRODUCIBLE_BYTE_KEYS:
        try:
            if int(row.get(key, 0) or 0) <= 0:
                failures.append(key)
        except (TypeError, ValueError):
            failures.append(key)
    for key in REPRODUCIBLE_DIGEST_KEYS:
        value = row.get(key)
        if not isinstance(value, str) or not HEX64_RE.fullmatch(value):
            failures.append(key)
    return failures


def digest_receipt_missing_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if digest_receipt_failures(row))


def reproducible_receipt_missing_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if reproducible_receipt_failures(row))


def self_test() -> dict[str, Any]:
    pdf_a = b"%PDF-1.5\n1 0 obj<< /CreationDate(D:20260605121000Z) /ModDate(D:20260605121000Z)>>endobj\ntrailer<< /ID [<aaaaaaaa><bbbbbbbb>] >>\n%%EOF"
    pdf_b = b"%PDF-1.5\n1 0 obj<< /CreationDate(D:20260605122000Z) /ModDate(D:20260605122000Z)>>endobj\ntrailer<< /ID [<cccccccc><dddddddd>] >>\n%%EOF"
    tmp_prefix = "/" + "tmp" + "/"
    log_a = f"({tmp_prefix}abc123/source/paper.tex)\nOutput written on {tmp_prefix}abc123/out/paper.pdf\n"
    log_b = f"({tmp_prefix}xyz789/source/paper.tex)\nOutput written on {tmp_prefix}xyz789/out/paper.pdf\n"
    norm_pdf_a = normalize_pdf_bytes(pdf_a)
    norm_pdf_b = normalize_pdf_bytes(pdf_b)
    norm_log_a = normalize_tex_log_text(log_a)
    norm_log_b = normalize_tex_log_text(log_b)
    cmd = pdflatex_receipt_command("pdflatex", "paper.tex", tmp_prefix + "out")
    draft_cmd = pdflatex_receipt_command("pdflatex", "paper.tex", tmp_prefix + "out", draft_mode=True)
    negative_control_results = [
        {"name": "raw_pdf_digest_differs", "status": "pass" if _digest_bytes(pdf_a) != _digest_bytes(pdf_b) else "fail"},
        {"name": "normalized_pdf_digest_matches", "status": "pass" if _digest_bytes(norm_pdf_a) == _digest_bytes(norm_pdf_b) else "fail"},
        {"name": "raw_log_digest_differs", "status": "pass" if _digest_bytes(log_a.encode()) != _digest_bytes(log_b.encode()) else "fail"},
        {"name": "normalized_log_digest_matches", "status": "pass" if _digest_bytes(norm_log_a.encode()) == _digest_bytes(norm_log_b.encode()) else "fail"},
        {"name": "stable_trailer_id_is_hex", "status": "pass" if re.fullmatch(r"[0-9a-f]{64}", stable_pdf_trailer_id("paper.tex", "abc")) else "fail"},
        {"name": "pdflatex_command_uses_no_shell_escape_trailer_id_and_jobname", "status": "pass" if ("-no-shell-escape" in cmd and "-jobname" in cmd and "\\pdftrailerid" in cmd[-1]) else "fail"},
        {"name": "pdflatex_draftmode_is_explicit_and_opt_in", "status": "pass" if ("-draftmode" in draft_cmd and "-draftmode" not in cmd) else "fail"},
    ]
    failures = [row for row in negative_control_results if row["status"] != "pass"]
    return {
        "status": "pass" if not failures else "fail",
        "receipt_policy": RECEIPT_POLICY_VERSION,
        "pdf_normalization_policy": PDF_NORMALIZATION_POLICY,
        "log_normalization_policy": LOG_NORMALIZATION_POLICY,
        "negative_control_results": negative_control_results,
        "negative_control_failed_count": len(failures),
        "fail_closed_rule": "If receipt normalization self-test fails, do not treat regenerated TeX digest evidence as reproducible across compile roots.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    report = self_test()
    if args.self_test:
        import json
        sys.stdout.write(json.dumps(report, indent=2) + "\n")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
