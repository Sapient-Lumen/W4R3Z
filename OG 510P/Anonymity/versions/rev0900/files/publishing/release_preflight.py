#!/usr/bin/env python3
"""Conservative preflight checks for a prospective new Anonymity release.

This does not publish anything. It validates naming, queue readiness, source
closure, and optional clean compilation before a source is frozen into published/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib

MIN_PDFLATEX_COMPILE_PASSES = 3

import re
import shutil
import subprocess
import sys
import tempfile
from typing import Iterable

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import publication_target as pt  # noqa: E402
import tex_compile_receipts as tcr  # noqa: E402

DATE_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
PREFIX = "Anonymity: "
CITE_COMMAND_RE = re.compile(
    r"\\(?:cite|citep|citet|citealp|citeauthor|citeyear|autocite|parencite|textcite|footcite|supercite|Cite)[A-Za-z*]*"
    r"(?:\s*\[[^\]]*\])*\s*\{([^{}]+)\}"
)
LABEL_RE = re.compile(r"\\label\{([^{}]+)\}")
REF_RE = re.compile(r"\\(?:ref|eqref|autoref|cref|Cref|pageref)\{([^{}]+)\}")
BIBITEM_RE = re.compile(r"\\bibitem(?:\[[^\]]*\])?\{([^{}]+)\}")
BIB_RESOURCE_RE = re.compile(r"\\(?:bibliography|addbibresource)\{([^{}]+)\}")
BIB_ENTRY_RE = re.compile(r"@[A-Za-z]+\s*\{\s*([^,\s]+)\s*,")
PLACEHOLDER_RE = re.compile(r"\b(TODO|FIXME|TBD|XXX)\b", re.IGNORECASE)
QUEUE_BOUND_SOURCE_HASH_RE = re.compile(r"sha256:([0-9a-f]{64})")
ARTIFACT_NEEDLES = re.compile(
    r"\b(artifact|receipt|manifest|provenance|evidence|validator|verification|verifier|notary|certificate|ledger|audit|support bundle|digest|hash|trace|budget|DHT)\b",
    re.IGNORECASE,
)
MALFORMED_BIB_COMMAND_RE = re.compile(r"(?m)^\s*(ibitem|ewblock)\b")


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def strip_tex_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        escaped = False
        keep = []
        for ch in line:
            if ch == "%" and not escaped:
                break
            keep.append(ch)
            escaped = (ch == "\\" and not escaped)
            if ch != "\\":
                escaped = False
        out.append("".join(keep))
    return "\n".join(out)


def split_keys(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def discover_bib_paths(src: pathlib.Path, text: str) -> list[pathlib.Path]:
    paths: list[pathlib.Path] = []
    for raw in BIB_RESOURCE_RE.findall(text):
        for name in split_keys(raw):
            candidate = name.strip()
            if candidate.startswith("["):
                continue
            if not candidate.endswith(".bib"):
                candidate += ".bib"
            paths.append((src.parent / candidate).resolve())
    # Conservative fallback: local .bib files beside the source.
    paths.extend(sorted(src.parent.glob("*.bib")))
    unique: list[pathlib.Path] = []
    seen = set()
    for path in paths:
        if path not in seen:
            unique.append(path)
            seen.add(path)
    return unique


def collect_bib_keys(src: pathlib.Path, text: str) -> tuple[set[str], list[str]]:
    keys = set(BIBITEM_RE.findall(text))
    missing_bibs: list[str] = []
    for bib in discover_bib_paths(src, text):
        if not bib.exists():
            missing_bibs.append(bib.relative_to(src.parent).as_posix() if bib.is_relative_to(src.parent) else bib.as_posix())
            continue
        try:
            keys.update(BIB_ENTRY_RE.findall(bib.read_text(encoding="utf-8")))
        except UnicodeDecodeError:
            keys.update(BIB_ENTRY_RE.findall(bib.read_text(encoding="latin-1")))
    return keys, missing_bibs


def citation_and_reference_closure(src: pathlib.Path, text: str) -> dict:
    clean = strip_tex_comments(text)
    citation_keys = sorted({key for raw in CITE_COMMAND_RE.findall(clean) for key in split_keys(raw)})
    bib_keys, missing_bibs = collect_bib_keys(src, clean)
    labels = set(LABEL_RE.findall(clean))
    ref_keys = sorted({key for raw in REF_RE.findall(clean) for key in split_keys(raw)})
    undefined_citations = sorted(key for key in citation_keys if key not in bib_keys)
    undefined_refs = sorted(key for key in ref_keys if key not in labels)
    return {
        "citation_key_count": len(citation_keys),
        "bibliography_key_count": len(bib_keys),
        "undefined_citations": undefined_citations,
        "missing_bibliography_files": missing_bibs,
        "reference_key_count": len(ref_keys),
        "label_count": len(labels),
        "undefined_references": undefined_refs,
    }


def placeholder_findings(text: str) -> list[dict[str, str | int]]:
    findings = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if PLACEHOLDER_RE.search(line):
            findings.append({"line": line_no, "text": line.strip()[:180]})
    return findings[:50]


def source_needs_evidence_review(text: str) -> bool:
    """Conservatively detect artifact-governance evidence-pack needs."""
    return bool(ARTIFACT_NEEDLES.search(text))


def malformed_bibliography_commands(text: str) -> list[dict[str, str | int]]:
    findings: list[dict[str, str | int]] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        match = MALFORMED_BIB_COMMAND_RE.match(line)
        if match:
            findings.append({"line": line_no, "command_fragment": match.group(1), "text": line.strip()[:180]})
    return findings[:50]


def repo_relative_existing_paths(root: pathlib.Path, paths: Iterable[str]) -> tuple[list[str], list[str]]:
    existing: list[str] = []
    missing: list[str] = []
    for raw in paths:
        rel = raw.strip()
        if not rel:
            continue
        candidate = (root / rel).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            missing.append(rel)
            continue
        if candidate.exists():
            existing.append(rel)
        else:
            missing.append(rel)
    return existing, missing


def load_queue_index(root: pathlib.Path) -> dict:
    queue_path = root / "release_queue" / "QUEUE_INDEX.json"
    if not queue_path.exists():
        return {}
    try:
        return json.loads(queue_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def queue_records_for_source(root: pathlib.Path, rel_source: str) -> list[dict]:
    """Return exact QUEUE_INDEX records for a source path.

    Earlier rev0805 preflight used broad note-text substring matching and included
    ``paper`` as a fallback needle, which made almost every source look queued.
    Release preflight must instead bind the candidate to an exact source_tex row.
    """
    queue = load_queue_index(root)
    records: list[dict] = []
    for state, items in queue.get("states", {}).items():
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict) and item.get("source_tex") == rel_source:
                enriched = dict(item)
                enriched["queue_state"] = state
                records.append(enriched)
    return records


def source_in_published_ready(root: pathlib.Path, rel_source: str) -> bool:
    return any(item.get("queue_state") == "published_ready" for item in queue_records_for_source(root, rel_source))


def decision_note_source_hashes(root: pathlib.Path, note_rel: str) -> list[str]:
    if not note_rel:
        return []
    path = root / note_rel
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    return sorted(set(QUEUE_BOUND_SOURCE_HASH_RE.findall(text)))


def artifact_governance_likely(text: str) -> bool:
    return bool(ARTIFACT_NEEDLES.search(text))


def run_compile_check(src: pathlib.Path, latex_command: str, source_date_epoch: str = "", source_sha256: str = "") -> dict:
    if shutil.which(latex_command) is None:
        return {"status": "fail", "detail": f"{latex_command} not found on PATH"}
    with tempfile.TemporaryDirectory(prefix="anonymity_release_preflight_") as tmp:
        tmp_path = pathlib.Path(tmp)
        # Copy the source directory so compile products cannot mutate the archive.
        work_dir = tmp_path / src.parent.name
        shutil.copytree(src.parent, work_dir)
        work_src = work_dir / src.name
        source_epoch = str(source_date_epoch or tcr.DEFAULT_SOURCE_DATE_EPOCH)
        if source_epoch and not source_epoch.isdigit():
            return {"status": "fail", "detail": f"SOURCE_DATE_EPOCH must be an integer, got {source_date_epoch!r}"}
        if latex_command == "latexmk":
            cmd = ["latexmk", "-pdf", "-halt-on-error", "-interaction=nonstopmode", work_src.name]
            runs = [cmd]
            minimum_required_passes = 1
            pdf_trailer_id = ""
        else:
            pdf_trailer_id = tcr.stable_pdf_trailer_id(src.as_posix(), source_sha256)
            runs = []
            for pass_index in range(MIN_PDFLATEX_COMPILE_PASSES):
                draft_mode = pass_index < MIN_PDFLATEX_COMPILE_PASSES - 1
                cmd = tcr.pdflatex_receipt_command(
                    latex_command,
                    work_src.name,
                    work_dir,
                    source_sha256=source_sha256 or src.as_posix(),
                    draft_mode=draft_mode,
                )
                cmd[-1] = rf"\pdftrailerid{{<{pdf_trailer_id}><{pdf_trailer_id}>}}\input{{{work_src.name}}}"
                runs.append(cmd)
            minimum_required_passes = MIN_PDFLATEX_COMPILE_PASSES
        env = tcr.deterministic_compile_env(os.environ.copy(), source_date_epoch=source_epoch)
        env["TZ"] = "UTC"
        logs = []
        for cmd in runs:
            proc = subprocess.run(cmd, cwd=work_dir, text=True, capture_output=True, env=env)
            logs.append(proc.stdout + "\n" + proc.stderr)
            if proc.returncode != 0:
                return {"status": "fail", "detail": f"compile command failed: {' '.join(cmd)}", "tail": logs[-1][-2000:]}
        # Only the final pass decides unresolved citation/reference cleanliness.
        # Earlier citation/reference/rerun warnings are expected while LaTeX is
        # still constructing its aux state.  The gate records aggregate warning
        # telemetry, but blocks only on final-pass debt.
        unresolved_needles = ["Citation", "undefined", "Undefined references"]
        rerun_needles = ["Rerun to get cross-references right", "Rerun to get citations correct", "Label(s) may have changed"]
        all_needles = unresolved_needles + rerun_needles
        aggregate_warnings = sorted({line.strip() for log in logs for line in log.splitlines() if any(needle in line for needle in all_needles)})[:60]
        final_log = logs[-1] if logs else ""
        final_unresolved_warnings = sorted({line.strip() for line in final_log.splitlines() if any(needle in line for needle in unresolved_needles)})[:30]
        final_rerun_warnings = sorted({line.strip() for line in final_log.splitlines() if any(needle in line for needle in rerun_needles)})[:30]
        final_warnings = sorted(set(final_unresolved_warnings) | set(final_rerun_warnings))[:40]
        pdf_path = work_src.with_suffix(".pdf")
        final_clean = not final_unresolved_warnings and not final_rerun_warnings
        report = {
            "status": "pass" if final_clean else "fail",
            "detail": "clean final compile pass" if final_clean else "final compile pass emitted unresolved citation/reference or rerun warnings",
            "command": latex_command,
            "run_count": len(runs),
            "minimum_required_passes": minimum_required_passes,
            "final_warning_count": len(final_warnings),
            "final_unresolved_warning_count": len(final_unresolved_warnings),
            "final_rerun_warning_count": len(final_rerun_warnings),
            "aggregate_warning_count": len(aggregate_warnings),
            "warnings": final_warnings,
            "final_unresolved_warnings": final_unresolved_warnings,
            "final_rerun_warnings": final_rerun_warnings,
            "nonfinal_warnings_ignored_count": max(0, len(aggregate_warnings) - len(final_warnings)),
            "first_pass_warnings_ignored_count": max(0, len(aggregate_warnings) - len(final_warnings)),
            "source_date_epoch": source_epoch,
            "deterministic_pdf_environment": bool(source_epoch),
            "deterministic_receipt_policy": tcr.RECEIPT_POLICY_VERSION if latex_command == "pdflatex" else "latexmk_legacy",
            "pdf_trailer_id": pdf_trailer_id,
        }
        if pdf_path.exists():
            report["output_pdf_sha256"] = sha256_file(pdf_path)
            report["output_pdf_bytes"] = pdf_path.stat().st_size
            if latex_command == "pdflatex":
                tcr.attach_compile_receipts(
                    report,
                    pdf_path=pdf_path,
                    combined_log_text="\n".join(logs),
                    final_log_text=final_log,
                    log_normalization_paths=[tmp_path, work_dir],
                    source_date_epoch=source_epoch,
                    pdf_trailer_id=pdf_trailer_id,
                )
        return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--title", required=True, help="Title without the 'Anonymity: ' prefix")
    parser.add_argument("--source", required=True, help="Source .tex path to freeze")
    parser.add_argument("--root", default=".")
    parser.add_argument("--allow-unqueued-source", action="store_true", help="Do not fail if the source is not found in release_queue/published_ready notes.")
    parser.add_argument("--allow-placeholders", action="store_true", help="Warn rather than fail on TODO/FIXME/TBD/XXX markers.")
    parser.add_argument("--expected-source-sha256", default="", help="Fail unless the selected source matches this exact SHA-256 digest.")
    parser.add_argument("--skip-citation-closure", action="store_true", help="Skip static citation/reference closure checks.")
    parser.add_argument("--compile", action="store_true", help="Run a clean LaTeX build in a temporary directory.")
    parser.add_argument("--latex-command", default="latexmk", choices=["latexmk", "pdflatex"], help="Command used when --compile is set.")
    parser.add_argument("--source-date-epoch", default="", help="Optional integer SOURCE_DATE_EPOCH used for deterministic PDF compile witnesses.")
    parser.add_argument("--evidence-mode", default="warn", choices=["warn", "require", "waive", "ignore"], help="How to handle likely artifact-governance evidence-pack needs.")
    parser.add_argument("--evidence-pack", action="append", default=[], help="Repo-relative evidence pack file or directory to attach; may be repeated.")
    parser.add_argument("--evidence-waiver-id", default="", help="Recorded waiver identifier when --evidence-mode=waive is used.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable report JSON.")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    src = (root / args.source).resolve()

    problems: list[str] = []
    warnings: list[str] = []
    details: dict[str, object] = {}

    if not DATE_RE.match(args.date):
        problems.append("date must match YYYY.MM.DD")
    if args.title.startswith(PREFIX):
        problems.append("title should omit the 'Anonymity: ' prefix")
    if not src.exists():
        problems.append(f"source does not exist: {args.source}")
        text = ""
    elif src.suffix != ".tex":
        problems.append("source must be a .tex file")
        text = src.read_text(encoding="utf-8", errors="replace")
    else:
        text = src.read_text(encoding="utf-8", errors="replace")
        details["source_sha256"] = sha256_file(src)
        if args.expected_source_sha256:
            details["expected_source_sha256"] = args.expected_source_sha256
            if details["source_sha256"] != args.expected_source_sha256:
                problems.append(f"source SHA-256 mismatch: expected {args.expected_source_sha256}, got {details['source_sha256']}")

    if src.exists():
        rel = src.relative_to(root).as_posix()
        if rel.startswith("published/"):
            problems.append("source is already under published/")
        if rel.startswith("series/synthesis/"):
            m = re.match(r"series/synthesis/paper(\d+)_", rel)
            if m and int(m.group(1)) >= 31:
                warnings.append("late synthesis paper: default posture is defer unless a recorded stabilization reason exists")
            if rel.startswith("series/synthesis/paper17_"):
                warnings.append("worked example has been repeatedly revised; verify it is truly a freeze target")
        queue_records = queue_records_for_source(root, rel)
        details["queue_records"] = queue_records
        current_source_hash = details.get("source_sha256", "")
        note_hash_bindings = []
        for record in queue_records:
            note_rel = str(record.get("path", ""))
            values = decision_note_source_hashes(root, note_rel)
            note_hash_bindings.append({"decision_note": note_rel, "source_sha256_values": values, "current_match": current_source_hash in values})
        details["decision_note_source_hash_bindings"] = note_hash_bindings
        if not args.allow_unqueued_source and not source_in_published_ready(root, rel):
            found_states = sorted({item.get("queue_state", "unknown") for item in queue_records})
            if found_states:
                problems.append(f"source is queued but not in published_ready: states={found_states}; pass --allow-unqueued-source only with a recorded exception")
            else:
                problems.append("source was not found as an exact source_tex row in release_queue/QUEUE_INDEX.json; pass --allow-unqueued-source only with a recorded exception")
        elif not args.allow_unqueued_source and not any(binding.get("current_match") for binding in note_hash_bindings):
            problems.append("Published-ready decision note does not carry the current source SHA-256; refresh or record an explicit exception before freeze")

    try:
        dirname = pt.portable_published_dirname(args.date, args.title.strip())
        target_rel = pt.portable_published_path(args.date, args.title.strip())
    except ValueError as exc:
        dirname = ""
        target_rel = "published/__invalid_publication_target__"
        problems.append(str(exc))
    target = root / target_rel
    if target.exists():
        problems.append(f"target already exists: {target.relative_to(root)}")

    if not list((root / "release_queue" / "decisions").glob("*.md")):
        warnings.append("no decision notes found; repo should usually record one before release")

    if text and not args.skip_citation_closure:
        closure = citation_and_reference_closure(src, text)
        details["citation_reference_closure"] = closure
        if closure["missing_bibliography_files"]:
            problems.append(f"missing bibliography files: {closure['missing_bibliography_files']}")
        if closure["undefined_citations"]:
            problems.append(f"undefined citation keys: {closure['undefined_citations'][:30]}")
        if closure["undefined_references"]:
            problems.append(f"undefined reference keys: {closure['undefined_references'][:30]}")

    if text:
        placeholders = placeholder_findings(text)
        details["placeholder_findings"] = placeholders
        if placeholders and not args.allow_placeholders:
            problems.append(f"placeholder markers present: {len(placeholders)} shown")
        elif placeholders:
            warnings.append(f"placeholder markers present but allowed: {len(placeholders)} shown")

        malformed_bib = malformed_bibliography_commands(text)
        details["malformed_bibliography_commands"] = malformed_bib
        if malformed_bib:
            problems.append(f"malformed bibliography command fragments present: {len(malformed_bib)} shown")

        likely_evidence = source_needs_evidence_review(text)
        details["artifact_governance_likely"] = likely_evidence
        existing_evidence, missing_evidence = repo_relative_existing_paths(root, args.evidence_pack)
        details["evidence_pack"] = {
            "mode": args.evidence_mode,
            "declared_paths": args.evidence_pack,
            "existing_paths": existing_evidence,
            "missing_paths": missing_evidence,
            "waiver_id": args.evidence_waiver_id,
        }
        if missing_evidence:
            problems.append(f"declared evidence-pack paths do not exist or escape the archive: {missing_evidence}")
        if likely_evidence and args.evidence_mode == "warn":
            warnings.append("artifact-governance language detected; freeze should attach a minimal evidence pack or record an explicit waiver")
        elif likely_evidence and args.evidence_mode == "require" and not existing_evidence:
            problems.append("artifact-governance language detected and --evidence-mode=require was used without an existing --evidence-pack path")
        elif likely_evidence and args.evidence_mode == "waive" and not args.evidence_waiver_id:
            problems.append("artifact-governance language detected and --evidence-mode=waive requires --evidence-waiver-id")

    if args.compile and src.exists():
        compile_report = run_compile_check(src, args.latex_command, args.source_date_epoch, args.expected_source_sha256)
        details["compile"] = compile_report
        if compile_report["status"] != "pass":
            problems.append(f"compile check failed: {compile_report['detail']}")

    report = {
        "status": "pass" if not problems else "fail",
        "prospective_published_name": dirname,
        "source": args.source,
        "target": target_rel,
        "warnings": warnings,
        "problems": problems,
        "details": details,
        "fail_closed_rule": "A failed preflight means no publication; repair closure, source-hash/evidence binding, record an explicit exception, or keep the source in the queue.",
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"prospective published name: [[{dirname}]]")
        print(f"prospective published path: {target_rel}")
        print(f"source: {args.source}")
        if "source_sha256" in details:
            print(f"source sha256: {details['source_sha256']}")
        if warnings:
            print("warnings:")
            for item in warnings:
                print(f" - {item}")
        if problems:
            print("problems:", file=sys.stderr)
            for item in problems:
                print(f" - {item}", file=sys.stderr)
            print("preflight: FAIL", file=sys.stderr)
        else:
            print("preflight: PASS")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
