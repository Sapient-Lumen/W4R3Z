#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(META.get("revision_number") or REV.replace("rev", "") or 0)
OUT = ROOT / "artifacts" / "audit"
PROBE = ROOT / "artifacts" / "probe-results"
FIXROOT = ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_STANDALONE_TOOLPACK_FIXTURES"

HANDOFF_CONTRACT = "public_trace_handoff_archive_v1"
TOOLPACK_CONTRACT = "public_trace_handoff_toolpack_v1"
TOOLCHAIN_SUBJECTS = {
    "public_trace_selector_receipt_replay_gate": "tools/public_trace_selector_receipt_replay_gate.py",
    "public_trace_selector_entry_gate": "tools/public_trace_selector_entry_gate.py",
    "public_trace_evaluation_verdict_audit": "tools/public_trace_evaluation_verdict_audit.py",
    "public_trace_gate_surrogate_verifier": "experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py",
    "public_trace_handoff_archive_gate": "tools/public_trace_handoff_archive_gate.py",
    "public_trace_cold_reviewer_verify_wrapper": "VERIFY_HANDOFF.py",
}


def sha256_file(path: Path | None) -> str | None:
    if path is None or not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def stable_sha256(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _normalized_subjects(subjects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"name": s.get("name"), "path": s.get("path"), "digest": s.get("digest", {})} for s in subjects]


def _handoff_subject_set_sha256(subjects: list[dict[str, Any]]) -> str:
    return stable_sha256({"handoff_contract": HANDOFF_CONTRACT, "subjects": _normalized_subjects(subjects)})


def _toolpack_subject_set_sha256(subjects: list[dict[str, Any]]) -> str:
    return stable_sha256({"toolpack_contract": TOOLPACK_CONTRACT, "subjects": _normalized_subjects([s for s in subjects if s.get("name") in TOOLCHAIN_SUBJECTS])})


def _copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _run(cmd: list[str], cwd: Path | None = None) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]}


def _write_deterministic_zip(zip_path: Path, source_dir: Path, archive_parent: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(source_dir.rglob("*")):
            if not path.is_file():
                continue
            arcname = path.relative_to(archive_parent).as_posix()
            info = zipfile.ZipInfo(arcname)
            info.date_time = (2026, 1, 1, 0, 0, 0)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())


def build_fixture(fixroot: Path | None = None) -> tuple[Path, Path, Path]:
    fixroot = fixroot or FIXROOT
    prev = ROOT / "artifacts" / "trace-bundles" / "REV0112_HANDOFF_ARCHIVE_FIXTURES" / "build" / "handoff"
    build = fixroot / "build" / "handoff"
    extracted = fixroot / "extracted" / "handoff"
    tampered = fixroot / "tampered" / "handoff"
    if build.exists():
        shutil.rmtree(build)
    if extracted.exists():
        shutil.rmtree(extracted)
    if tampered.exists():
        shutil.rmtree(tampered)
    build.mkdir(parents=True)
    _copy(prev / "evidence" / "trace.npz", build / "evidence" / "trace.npz")
    _copy(prev / "evidence" / "trace.provenance.json", build / "evidence" / "trace.provenance.json")
    _copy(prev / "receipts" / "evaluation_receipt.json", build / "receipts" / "evaluation_receipt.json")
    _copy(prev / "receipts" / "selector_entry_receipt.json", build / "receipts" / "selector_entry_receipt.json")
    for name, rel in TOOLCHAIN_SUBJECTS.items():
        _copy(ROOT / rel, build / rel)

    subjects = [
        {"name": "public_trace_npz", "path": "evidence/trace.npz", "digest": {"sha256": sha256_file(build / "evidence" / "trace.npz")}},
        {"name": "public_trace_provenance_json", "path": "evidence/trace.provenance.json", "digest": {"sha256": sha256_file(build / "evidence" / "trace.provenance.json")}},
        {"name": "public_trace_evaluation_receipt", "path": "receipts/evaluation_receipt.json", "digest": {"sha256": sha256_file(build / "receipts" / "evaluation_receipt.json")}},
        {"name": "public_trace_selector_entry_receipt", "path": "receipts/selector_entry_receipt.json", "digest": {"sha256": sha256_file(build / "receipts" / "selector_entry_receipt.json")}},
    ]
    for name, rel in TOOLCHAIN_SUBJECTS.items():
        subjects.append({"name": name, "path": rel, "digest": {"sha256": sha256_file(build / rel)}})
    manifest = {
        "handoff_contract": HANDOFF_CONTRACT,
        "toolpack_contract": TOOLPACK_CONTRACT,
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": True,
        "gpu_fused_kernel_measured": False,
        "selector_entry_receipt_contract": "public_trace_selector_entry_receipt_v1",
        "evaluation_receipt_contract": "public_trace_evaluation_receipt_v2",
        "paths_relative_to_manifest_dir": True,
        "subjects": subjects,
        "handoff_subject_set_sha256": _handoff_subject_set_sha256(subjects),
        "toolpack_subject_set_sha256": _toolpack_subject_set_sha256(subjects),
        "standalone_toolpack_selfcheck_required": True,
        "summary": "Portable handoff manifest whose bundled gate, cold-reviewer wrapper, and replay verifier can run without CUBE-META or the source cube checkout. Fixture only; not promotion evidence.",
    }
    (build / "PUBLIC_TRACE_HANDOFF_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")

    # Build and re-extract the archive to force the gate to run from a moved path.
    zip_path = fixroot / f"{REVUP}_portable_handoff_toolpack_fixture.zip"
    _write_deterministic_zip(zip_path, build, build.parent)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(fixroot / "extracted")
    shutil.copytree(extracted, tampered)
    (tampered / "tools" / "public_trace_selector_receipt_replay_gate.py").write_text(
        (tampered / "tools" / "public_trace_selector_receipt_replay_gate.py").read_text(encoding="utf-8") + "\n# tampered after manifest\n",
        encoding="utf-8",
    )
    return build, extracted, tampered


def run_audit(fixroot: Path) -> dict[str, Any]:
    build, extracted, tampered = build_fixture(fixroot=fixroot)
    pass_run = _run([sys.executable, str(extracted / "tools" / "public_trace_handoff_archive_gate.py"), "--strict", "--no-write"], cwd=extracted)
    fail_run = _run([sys.executable, str(tampered / "tools" / "public_trace_handoff_archive_gate.py"), "--strict", "--no-write"], cwd=tampered)
    errors: list[str] = []
    blockers = ["real_public_trace_and_named_hardware_timing_still_required_for_promotion"]
    if pass_run["returncode"] != 0:
        errors.append("extracted standalone toolpack gate did not pass")
    if fail_run["returncode"] == 0:
        errors.append("tampered standalone toolpack replay gate was not rejected")
    try:
        fixture_root_value = fixroot.relative_to(ROOT).as_posix()
    except Exception:
        fixture_root_value = str(fixroot)
    return {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass_with_blockers" if not errors else "fail",
        "verdict": "standalone_toolpack_replay_verified_not_promotion" if not errors else "standalone_toolpack_replay_failed",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "fixture_root": fixture_root_value,
        "no_write_inner_gates": True,
        "extracted_gate_returncode": pass_run["returncode"],
        "tampered_gate_returncode": fail_run["returncode"],
        "extracted_gate_stdout_tail": pass_run["stdout"],
        "extracted_gate_stderr_tail": pass_run["stderr"],
        "tampered_gate_stdout_tail": fail_run["stdout"],
        "tampered_gate_stderr_tail": fail_run["stderr"],
        "research_basis": [
            {"source": "SLSA build provenance v1.2", "url": "https://slsa.dev/spec/v1.2/build-provenance", "note": "provenance consumers verify artifacts against expectations and may rebuild"},
            {"source": "in-toto attestation link predicate", "url": "https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md", "note": "subject records step products and materials record inputs"},
            {"source": "Hugging Face Hub snapshot_download docs", "url": "https://huggingface.co/docs/huggingface_hub/en/guides/download", "note": "specific repository revision must be supplied instead of default latest"},
        ],
        "summary": "Checks a self-contained handoff toolpack from a moved extraction. Inner gate invocations now use --no-write so reviewer verification does not create new audit artifacts inside the archive being verified.",
        "errors": errors,
        "warnings": [],
        "blockers": blockers,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit that the public-trace handoff archive carries a standalone verifier toolpack.")
    ap.add_argument("--no-write", action="store_true", help="run in a temporary scratch area and do not update package audit artifacts")
    ap.add_argument("--scratch-dir", type=Path, default=None, help="optional scratch directory for --no-write or fixture construction")
    args = ap.parse_args()
    sys.dont_write_bytecode = bool(args.no_write)

    if args.no_write:
        if args.scratch_dir:
            scratch = args.scratch_dir
            scratch.mkdir(parents=True, exist_ok=True)
            audit = run_audit(scratch / f"{REVUP}_STANDALONE_TOOLPACK_FIXTURES")
        else:
            with tempfile.TemporaryDirectory(prefix=f"{REVUP.lower()}_standalone_toolpack_") as td:
                audit = run_audit(Path(td) / f"{REVUP}_STANDALONE_TOOLPACK_FIXTURES")
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        PROBE.mkdir(parents=True, exist_ok=True)
        FIXROOT.mkdir(parents=True, exist_ok=True)
        audit = run_audit(FIXROOT)
        (OUT / f"{REVUP}_PUBLIC_TRACE_STANDALONE_TOOLPACK_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        md = [
            f"# Public trace standalone toolpack audit — {REVUP}", "",
            f"Status: `{audit['status']}`  ", f"Verdict: `{audit['verdict']}`  ", "Promotion allowed: `false`", "",
            audit["summary"], "",
            "## Research basis", "",
            "- SLSA build provenance treats provenance as data consumers verify against expected artifact production: https://slsa.dev/spec/v1.2/build-provenance",
            "- in-toto link attestations bind step products in `subject` and inputs in `materials`: https://github.com/in-toto/attestation/blob/main/spec/predicates/link.md",
            "- Hugging Face `snapshot_download()` needs an explicit `revision` for immutable model snapshots: https://huggingface.co/docs/huggingface_hub/en/guides/download",
            "", "## Checks", "",
            f"- extracted standalone gate return code: `{audit['extracted_gate_returncode']}`",
            f"- tampered standalone gate return code: `{audit['tampered_gate_returncode']}`",
            "", "## Blockers", "",
        ]
        md.extend([f"- `{b}`" for b in audit["blockers"]])
        md.extend(["", "## Errors", ""])
        md.extend([f"- `{e}`" for e in audit["errors"]] if audit["errors"] else ["- none"])
        (OUT / f"{REVUP}_PUBLIC_TRACE_STANDALONE_TOOLPACK_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "verdict": audit["verdict"], "errors": audit["errors"], "no_write": bool(args.no_write)}, indent=2))
    return 0 if not audit["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
