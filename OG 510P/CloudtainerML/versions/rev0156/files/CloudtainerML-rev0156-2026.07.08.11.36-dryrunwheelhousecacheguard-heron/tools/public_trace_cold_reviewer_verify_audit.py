#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(META.get("revision_number") or REV.replace("rev", "") or 0)
OUT = ROOT / "artifacts" / "audit"
FIXROOT = ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_COLD_REVIEWER_VERIFY_FIXTURES"


def load_module(rel: str, name: str) -> Any:
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name + "_" + REVUP, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import " + rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def run(cmd: list[str], cwd: Path | None = None) -> dict[str, Any]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    return {
        "cmd": cmd,
        "cwd": str(cwd) if cwd else None,
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-4000:],
        "stderr_tail": proc.stderr[-4000:],
    }


def copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def run_audit(fixroot: Path, standalone_fixroot: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    case_results: dict[str, bool] = {}
    runs: dict[str, dict[str, Any]] = {}

    # Reuse the standalone fixture builder, but test the cold-reviewer entry
    # points that a moved/extracted handoff archive exposes.
    standalone = load_module("tools/public_trace_standalone_toolpack_audit.py", "_cold_standalone")
    _build, extracted, _tampered = standalone.build_fixture(fixroot=standalone_fixroot)

    if fixroot.exists():
        shutil.rmtree(fixroot)
    fixroot.mkdir(parents=True, exist_ok=True)
    reviewer = fixroot / "reviewer copy with spaces" / "handoff"
    copytree(extracted, reviewer)

    direct_cmd = [sys.executable, str(reviewer / "tools" / "public_trace_handoff_archive_gate.py"), "--strict", "--no-write"]
    wrapper_cmd = [sys.executable, str(reviewer / "VERIFY_HANDOFF.py")]
    runs["direct_no_arg_gate"] = run(direct_cmd, cwd=reviewer)
    runs["verify_handoff_wrapper"] = run(wrapper_cmd, cwd=reviewer)
    case_results["direct_no_arg_gate_passes_after_move"] = runs["direct_no_arg_gate"]["returncode"] == 0
    case_results["verify_handoff_wrapper_passes_after_move"] = runs["verify_handoff_wrapper"]["returncode"] == 0

    # The direct gate must be canonical: it validates the wrapper by digest.
    # This prevents the convenience launcher from becoming an unverified trust root.
    tampered_wrapper = fixroot / "tampered wrapper" / "handoff"
    copytree(reviewer, tampered_wrapper)
    wp = tampered_wrapper / "VERIFY_HANDOFF.py"
    wp.write_text(wp.read_text(encoding="utf-8") + "\n# tampered after manifest\n", encoding="utf-8")
    runs["tampered_wrapper_direct_gate"] = run([sys.executable, str(tampered_wrapper / "tools" / "public_trace_handoff_archive_gate.py"), "--strict", "--no-write"], cwd=tampered_wrapper)
    case_results["direct_gate_rejects_tampered_wrapper"] = runs["tampered_wrapper_direct_gate"]["returncode"] != 0 and (
        "public_trace_cold_reviewer_verify_wrapper" in (runs["tampered_wrapper_direct_gate"]["stdout_tail"] + runs["tampered_wrapper_direct_gate"]["stderr_tail"])
        or "toolpack_subject_set_sha256" in (runs["tampered_wrapper_direct_gate"]["stdout_tail"] + runs["tampered_wrapper_direct_gate"]["stderr_tail"])
    )

    missing_manifest = fixroot / "missing manifest" / "handoff"
    copytree(reviewer, missing_manifest)
    (missing_manifest / "PUBLIC_TRACE_HANDOFF_MANIFEST.json").unlink()
    runs["missing_manifest_direct_gate_strict"] = run([sys.executable, str(missing_manifest / "tools" / "public_trace_handoff_archive_gate.py"), "--strict", "--no-write"], cwd=missing_manifest)
    case_results["no_arg_gate_fails_without_root_manifest"] = runs["missing_manifest_direct_gate_strict"]["returncode"] != 0 and "manifest" in (runs["missing_manifest_direct_gate_strict"]["stdout_tail"] + runs["missing_manifest_direct_gate_strict"]["stderr_tail"]).lower()

    # A reviewer who starts from the full cube root should not get a false green
    # from the convenience launcher because root has no public-trace handoff manifest.
    runs["root_wrapper_blocks_outside_handoff"] = run([sys.executable, str(ROOT / "VERIFY_HANDOFF.py")], cwd=ROOT)
    case_results["root_wrapper_blocks_outside_handoff"] = runs["root_wrapper_blocks_outside_handoff"]["returncode"] != 0

    source = (ROOT / "tools" / "public_trace_handoff_archive_gate.py").read_text(encoding="utf-8")
    source_checks = {
        "portable_manifest_autodiscovery": "PUBLIC_TRACE_HANDOFF_MANIFEST.json" in source and "portable_manifest" in source,
        "wrapper_subject_required": "public_trace_cold_reviewer_verify_wrapper" in source,
        "root_probe_fallback_kept": "artifacts" in source and "probe-results" in source,
        "no_write_gate_supported": "--no-write" in source,
    }
    for key, value in source_checks.items():
        if not value:
            errors.append("cold-reviewer gate source check failed: " + key)

    if not all(case_results.values()):
        errors.append("cold-reviewer verification case failed: " + json.dumps(case_results, sort_keys=True))

    blockers = [
        "real_public_trace_handoff_archive_missing",
        "cold_reviewer_gate_is_integrity_handoff_not_promotion_evidence",
        "named_hardware_timing_still_required_for_promotion",
    ]
    try:
        fixture_dir_value = fixroot.relative_to(ROOT).as_posix()
    except Exception:
        fixture_dir_value = str(fixroot)
    return {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass_with_blockers" if not errors else "fail",
        "verdict": "cold_reviewer_verify_path_hardened_not_promotion" if not errors else "cold_reviewer_verify_path_failed",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Audits a cold-reviewer verification path for portable public-trace handoff archives. Reviewer-facing runs now use --no-write and PYTHONDONTWRITEBYTECODE so verification does not mutate the archive or package being checked.",
        "fixture_dir": fixture_dir_value,
        "no_write_gate_supported": True,
        "case_results": case_results,
        "source_checks": source_checks,
        "runs": runs,
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "online_research_basis": [
            {"url": "https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md", "note": "in-toto Statements bind predicates to named subjects and digests; the cold-reviewer gate validates trace, receipt, and tool subjects by digest."},
            {"url": "https://slsa.dev/spec/v1.2/verifying-source", "note": "SLSA emphasizes that attestations only matter when inspected; rev0115 keeps the portable handoff self-inspecting without mutating it."},
            {"url": "https://huggingface.co/docs/huggingface_hub/en/guides/download", "note": "HF snapshot workflows rely on explicit revisions and local cache behavior; the handoff remains digest/revision-first after extraction."},
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit the cold-reviewer handoff verification path.")
    ap.add_argument("--no-write", action="store_true", help="run in a temporary scratch area and do not update package audit artifacts")
    ap.add_argument("--scratch-dir", type=Path, default=None, help="optional scratch directory for --no-write or fixture construction")
    args = ap.parse_args()
    sys.dont_write_bytecode = bool(args.no_write)

    if args.no_write:
        if args.scratch_dir:
            scratch = args.scratch_dir
            scratch.mkdir(parents=True, exist_ok=True)
            audit = run_audit(scratch / f"{REVUP}_COLD_REVIEWER_VERIFY_FIXTURES", scratch / f"{REVUP}_STANDALONE_TOOLPACK_FIXTURES")
        else:
            with tempfile.TemporaryDirectory(prefix=f"{REVUP.lower()}_cold_reviewer_") as td:
                scratch = Path(td)
                audit = run_audit(scratch / f"{REVUP}_COLD_REVIEWER_VERIFY_FIXTURES", scratch / f"{REVUP}_STANDALONE_TOOLPACK_FIXTURES")
    else:
        OUT.mkdir(parents=True, exist_ok=True)
        FIXROOT.mkdir(parents=True, exist_ok=True)
        audit = run_audit(FIXROOT, ROOT / "artifacts" / "trace-bundles" / f"{REVUP}_STANDALONE_TOOLPACK_FIXTURES")
        (OUT / f"{REVUP}_PUBLIC_TRACE_COLD_REVIEWER_VERIFY_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        md = [
            f"# Public trace cold-reviewer verify audit — {REVUP}",
            "",
            f"Status: `{audit['status']}`  ",
            f"Verdict: `{audit['verdict']}`  ",
            "Promotion allowed: `false`",
            "",
            audit["summary"],
            "",
            "## Cases",
            "",
        ]
        md.extend([f"- `{k}` = `{v}`" for k, v in audit["case_results"].items()])
        md.extend(["", "## Blockers", ""])
        md.extend([f"- `{b}`" for b in audit["blockers"]])
        md.extend(["", "## Errors", ""])
        md.extend([f"- `{e}`" for e in audit["errors"]] if audit["errors"] else ["- none"])
        (OUT / f"{REVUP}_PUBLIC_TRACE_COLD_REVIEWER_VERIFY_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "verdict": audit["verdict"], "case_results": audit["case_results"], "errors": audit["errors"], "no_write": bool(args.no_write)}, indent=2))
    return 0 if not audit["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
