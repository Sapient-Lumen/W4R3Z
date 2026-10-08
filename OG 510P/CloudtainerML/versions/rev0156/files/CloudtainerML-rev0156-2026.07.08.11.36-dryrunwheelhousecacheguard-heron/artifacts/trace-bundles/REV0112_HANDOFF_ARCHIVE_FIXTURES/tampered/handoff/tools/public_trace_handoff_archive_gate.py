#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(REV.replace("rev", ""))
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)
HANDOFF_CONTRACT = "public_trace_handoff_archive_v1"
TOOLPACK_CONTRACT = "public_trace_handoff_toolpack_v1"
REPLAY_TOOL_REL = "tools/public_trace_selector_receipt_replay_gate.py"
SELECTOR_RECEIPT_CONTRACT = "public_trace_selector_entry_receipt_v1"
EVALUATION_RECEIPT_CONTRACT = "public_trace_evaluation_receipt_v2"
TOOLCHAIN_SUBJECTS = {
    "public_trace_selector_receipt_replay_gate": "tools/public_trace_selector_receipt_replay_gate.py",
    "public_trace_selector_entry_gate": "tools/public_trace_selector_entry_gate.py",
    "public_trace_evaluation_verdict_audit": "tools/public_trace_evaluation_verdict_audit.py",
    "public_trace_gate_surrogate_verifier": "experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py",
    "public_trace_handoff_archive_gate": "tools/public_trace_handoff_archive_gate.py",
}
REQUIRED_SUBJECTS = {
    "public_trace_npz",
    "public_trace_provenance_json",
    "public_trace_evaluation_receipt",
    "public_trace_selector_entry_receipt",
    *TOOLCHAIN_SUBJECTS.keys(),
}


def _load_replay_module() -> Any:
    path = ROOT / REPLAY_TOOL_REL
    spec = importlib.util.spec_from_file_location("_handoff_replay_" + REVUP, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import " + REPLAY_TOOL_REL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


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


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_load_error": repr(exc)}


def rel(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def _resolve_under(base: Path, value: Any, errors: list[str], *, field: str) -> Path | None:
    if not value:
        errors.append(f"handoff manifest missing {field}")
        return None
    p = Path(str(value))
    if p.is_absolute():
        errors.append(f"handoff manifest {field} must be relative, not absolute")
        return None
    target = (base / p).resolve()
    try:
        target.relative_to(base.resolve())
    except Exception:
        errors.append(f"handoff manifest {field} escapes handoff directory")
        return None
    return target


def _subject_map(subjects: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(subjects, list):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for item in subjects:
        if isinstance(item, dict) and item.get("name"):
            out[str(item["name"])] = item
    return out


def _normalized_subjects(subjects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"name": s.get("name"), "path": s.get("path"), "digest": s.get("digest", {})} for s in subjects]


def _handoff_subject_set_sha256(subjects: list[dict[str, Any]]) -> str:
    return stable_sha256({"handoff_contract": HANDOFF_CONTRACT, "subjects": _normalized_subjects(subjects)})


def _toolpack_subject_set_sha256(subjects: list[dict[str, Any]]) -> str:
    tool_subjects = [s for s in subjects if s.get("name") in TOOLCHAIN_SUBJECTS]
    return stable_sha256({"toolpack_contract": TOOLPACK_CONTRACT, "subjects": _normalized_subjects(tool_subjects)})


def default_manifest() -> Path:
    return ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_HANDOFF_MANIFEST.json"


def evaluate_handoff(*, handoff_dir: Path | None = None, manifest_path: Path | None = None, strict: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    blockers: list[str] = []
    if manifest_path is None:
        manifest_path = default_manifest()
    if not manifest_path.exists():
        audit = {
            "revision": REV,
            "revision_number": REVNO,
            "package_name": META.get("package_name"),
            "archive_name": META.get("archive_name"),
            "status": "pass_with_blockers",
            "verdict": "handoff_archive_blocked_no_manifest",
            "promotion_allowed": False,
            "public_pretrained_trace_loaded": False,
            "gpu_fused_kernel_measured": False,
            "handoff_manifest": rel(manifest_path),
            "summary": "No public-trace handoff manifest exists yet. This is expected before a real accepted evaluation receipt and selector-entry receipt are produced.",
            "errors": [],
            "warnings": [],
            "blockers": ["real_public_trace_handoff_manifest_missing"],
        }
        if strict:
            audit["status"] = "fail"
            audit["errors"] = ["strict handoff archive gate requested but manifest is missing"]
        return audit

    base = (handoff_dir or manifest_path.parent).resolve()
    manifest = load_json(manifest_path)
    if manifest.get("_load_error"):
        return {
            "revision": REV,
            "revision_number": REVNO,
            "package_name": META.get("package_name"),
            "archive_name": META.get("archive_name"),
            "status": "fail",
            "verdict": "handoff_archive_blocked_malformed_manifest",
            "promotion_allowed": False,
            "public_pretrained_trace_loaded": False,
            "gpu_fused_kernel_measured": False,
            "handoff_manifest": rel(manifest_path),
            "summary": "Handoff manifest could not be parsed.",
            "errors": [str(manifest.get("_load_error"))],
            "warnings": [],
            "blockers": [],
        }
    if manifest.get("handoff_contract") != HANDOFF_CONTRACT:
        errors.append("handoff_contract must be " + HANDOFF_CONTRACT)
    if manifest.get("toolpack_contract") != TOOLPACK_CONTRACT:
        errors.append("toolpack_contract must be " + TOOLPACK_CONTRACT)
    if manifest.get("paths_relative_to_manifest_dir") is not True:
        errors.append("paths_relative_to_manifest_dir must be true")
    if manifest.get("promotion_allowed") is not False:
        errors.append("handoff manifest must not allow promotion")
    if manifest.get("selector_entry_receipt_contract") not in (None, SELECTOR_RECEIPT_CONTRACT):
        errors.append("selector_entry_receipt_contract must be " + SELECTOR_RECEIPT_CONTRACT)
    if manifest.get("evaluation_receipt_contract") not in (None, EVALUATION_RECEIPT_CONTRACT):
        errors.append("evaluation_receipt_contract must be " + EVALUATION_RECEIPT_CONTRACT)
    if manifest.get("revision") != REV:
        warnings.append("handoff manifest revision differs from current cube revision; digest replay continues")

    subjects = manifest.get("subjects")
    if not isinstance(subjects, list):
        errors.append("handoff manifest missing subjects list")
        subjects = []
    subject_by_name = _subject_map(subjects)
    missing_subjects = sorted(REQUIRED_SUBJECTS - set(subject_by_name))
    for name in missing_subjects:
        errors.append("handoff manifest missing required subject: " + name)
    duplicate_names = [name for name in {str(s.get('name')) for s in subjects if isinstance(s, dict)} if sum(1 for s in subjects if isinstance(s, dict) and str(s.get('name')) == name) > 1]
    for name in sorted(duplicate_names):
        errors.append("handoff manifest duplicate subject: " + name)

    paths: dict[str, Path | None] = {}
    actual_subjects: list[dict[str, Any]] = []
    for item in subjects:
        if not isinstance(item, dict):
            errors.append("handoff manifest subjects contains non-object entry")
            continue
        name = str(item.get("name"))
        path = _resolve_under(base, item.get("path"), errors, field=f"subject[{name}].path")
        paths[name] = path
        expected_sha = None
        if isinstance(item.get("digest"), dict):
            expected_sha = item["digest"].get("sha256")
        actual_sha = sha256_file(path)
        if actual_sha is None:
            errors.append("handoff subject missing file: " + name)
        elif expected_sha != actual_sha:
            errors.append("handoff subject digest mismatch: " + name)
        actual_subjects.append({"name": name, "path": item.get("path"), "digest": {"sha256": actual_sha}})

    actual_subject_set = _handoff_subject_set_sha256(actual_subjects)
    if manifest.get("handoff_subject_set_sha256") != actual_subject_set:
        errors.append("handoff_subject_set_sha256 does not match actual extracted files/tools")

    actual_toolpack_subject_set = _toolpack_subject_set_sha256(actual_subjects)
    if manifest.get("toolpack_subject_set_sha256") != actual_toolpack_subject_set:
        errors.append("toolpack_subject_set_sha256 does not match actual extracted tool files")

    current_tool_hashes: dict[str, str | None] = {name: sha256_file(ROOT / relpath) for name, relpath in TOOLCHAIN_SUBJECTS.items()}
    for name, relpath in TOOLCHAIN_SUBJECTS.items():
        sub = subject_by_name.get(name)
        if not sub:
            continue
        if sub.get("path") != relpath:
            errors.append(f"handoff tool subject {name} path must be {relpath}")
        subject_sha = sub.get("digest", {}).get("sha256") if isinstance(sub.get("digest"), dict) else None
        if subject_sha != current_tool_hashes.get(name):
            errors.append(f"handoff tool subject {name} hash does not match current cube tool")

    replay_result: dict[str, Any] = {}
    if not errors:
        replay_mod = _load_replay_module()
        replay_result = replay_mod.evaluate_chain(
            selector_receipt_path=paths.get("public_trace_selector_entry_receipt") or Path("missing"),
            evaluation_receipt_path=paths.get("public_trace_evaluation_receipt"),
            trace_npz=paths.get("public_trace_npz"),
            provenance_json=paths.get("public_trace_provenance_json"),
            strict=True,
        )
        if replay_result.get("verdict") != "selector_receipt_replay_verified_selector_entry_not_promotion":
            errors.append("selector receipt replay did not verify handoff archive subjects")
        for e in replay_result.get("errors", []):
            errors.append("replay: " + str(e))
    else:
        blockers.append("replay_skipped_due_to_manifest_or_digest_errors")

    if errors:
        status = "fail"
        verdict = "handoff_archive_blocked_manifest_or_replay_mismatch"
    else:
        status = "pass_with_blockers"
        verdict = "handoff_archive_replay_verified_not_promotion"
        blockers.append("named_hardware_timing_still_required_for_promotion")

    if strict and verdict != "handoff_archive_replay_verified_not_promotion":
        status = "fail"
        if "strict handoff archive gate requested but verified handoff is absent" not in errors:
            errors.append("strict handoff archive gate requested but verified handoff is absent")

    return {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": status,
        "verdict": verdict,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": verdict == "handoff_archive_replay_verified_not_promotion",
        "gpu_fused_kernel_measured": False,
        "handoff_manifest": rel(manifest_path),
        "handoff_dir": rel(base),
        "handoff_contract": manifest.get("handoff_contract"),
        "toolpack_contract": manifest.get("toolpack_contract"),
        "handoff_subject_set_sha256": manifest.get("handoff_subject_set_sha256"),
        "actual_handoff_subject_set_sha256": actual_subject_set if subjects else None,
        "toolpack_subject_set_sha256": manifest.get("toolpack_subject_set_sha256"),
        "actual_toolpack_subject_set_sha256": actual_toolpack_subject_set if subjects else None,
        "actual_subjects": actual_subjects,
        "current_tool_hashes": current_tool_hashes,
        "replay_result_verdict": replay_result.get("verdict"),
        "replay_result_status": replay_result.get("status"),
        "summary": "Validates a portable public-trace handoff directory/archive by checking relative subject paths, SHA-256 digests, the handoff subject-set hash, a self-contained verifier toolpack, current tool identity, and a full selector-entry receipt replay. It is an archive-portability gate, not promotion evidence.",
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a portable public-trace handoff archive/directory by digest, verifier toolpack, and selector-entry receipt replay.")
    ap.add_argument("--handoff-dir", type=Path, default=None)
    ap.add_argument("--manifest", type=Path, default=None)
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    audit = evaluate_handoff(handoff_dir=args.handoff_dir, manifest_path=args.manifest, strict=args.strict)
    (OUT / f"{REVUP}_PUBLIC_TRACE_HANDOFF_ARCHIVE_GATE_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace handoff archive gate — {REVUP}", "",
        f"Status: `{audit['status']}`  ", f"Verdict: `{audit.get('verdict')}`  ", "Promotion allowed: `false`", "",
        audit.get("summary", "No summary."), "", "## Manifest", "",
        f"- handoff manifest: `{audit.get('handoff_manifest') or 'missing'}`",
        f"- handoff dir: `{audit.get('handoff_dir') or 'missing'}`",
        f"- toolpack contract: `{audit.get('toolpack_contract') or 'missing'}`",
        "", "## Blockers", "",
    ]
    md.extend([f"- `{b}`" for b in audit.get("blockers", [])] if audit.get("blockers") else ["- none"])
    md.extend(["", "## Errors", ""])
    md.extend([f"- `{e}`" for e in audit.get("errors", [])] if audit.get("errors") else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_HANDOFF_ARCHIVE_GATE_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "verdict": audit.get("verdict"), "errors": audit.get("errors", []), "blockers": audit.get("blockers", [])}, indent=2))
    return 0 if not audit.get("errors") else 1


if __name__ == "__main__":
    raise SystemExit(main())
