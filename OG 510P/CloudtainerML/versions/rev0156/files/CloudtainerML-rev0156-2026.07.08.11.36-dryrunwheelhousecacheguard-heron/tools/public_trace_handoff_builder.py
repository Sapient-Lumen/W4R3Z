#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLCHAIN_SUBJECTS = {
    "public_trace_selector_receipt_replay_gate": "tools/public_trace_selector_receipt_replay_gate.py",
    "public_trace_selector_entry_gate": "tools/public_trace_selector_entry_gate.py",
    "public_trace_evaluation_verdict_audit": "tools/public_trace_evaluation_verdict_audit.py",
    "public_trace_gate_surrogate_verifier": "experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py",
    "public_trace_handoff_archive_gate": "tools/public_trace_handoff_archive_gate.py",
    "public_trace_cold_reviewer_verify_wrapper": "VERIFY_HANDOFF.py",
}
HANDOFF_CONTRACT = "public_trace_handoff_archive_v1"
TOOLPACK_CONTRACT = "public_trace_handoff_toolpack_v1"
SELECTOR_RECEIPT_CONTRACT = "public_trace_selector_entry_receipt_v1"
EVALUATION_RECEIPT_CONTRACT = "public_trace_evaluation_receipt_v2"
TRACE_IDENTITY_RECEIPT_CONTRACT = "public_trace_downstream_identity_receipt_v1"
SELECTOR_ENTRY_CHAIN_CONTRACT = "public_trace_selector_entry_chain_v1"


def load_meta(root: Path = ROOT) -> dict[str, Any]:
    try:
        return json.loads((root / "CUBE-META.json").read_text(encoding="utf-8"))
    except Exception:
        return {
            "revision": "rev0000",
            "revision_number": 0,
            "package_name": root.name,
            "archive_name": None,
        }


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


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


def normalized(subjects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"name": s.get("name"), "path": s.get("path"), "digest": s.get("digest", {})} for s in subjects]


def subject_set_sha256(subjects: list[dict[str, Any]]) -> str:
    return stable_sha256({"handoff_contract": HANDOFF_CONTRACT, "subjects": normalized(subjects)})


def toolpack_subject_set_sha256(subjects: list[dict[str, Any]]) -> str:
    tool_subjects = [s for s in subjects if s.get("name") in TOOLCHAIN_SUBJECTS]
    return stable_sha256({"toolpack_contract": TOOLPACK_CONTRACT, "subjects": normalized(tool_subjects)})


def _copy_preserving_name(src: Path, dst_dir: Path, fallback_name: str) -> Path:
    dst_dir.mkdir(parents=True, exist_ok=True)
    name = src.name or fallback_name
    dst = dst_dir / name
    if src.resolve() != dst.resolve():
        shutil.copy2(src, dst)
    return dst


def _copy_tool(root: Path, handoff_dir: Path, relpath: str) -> Path:
    src = root / relpath
    if not src.exists():
        raise FileNotFoundError(f"required handoff tool subject missing: {relpath}")
    dst = handoff_dir / relpath
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.resolve() != dst.resolve():
        shutil.copy2(src, dst)
    return dst


def _rel(base: Path, path: Path) -> str:
    return path.resolve().relative_to(base.resolve()).as_posix()


def build_handoff_directory(
    *,
    handoff_dir: Path,
    trace_npz: Path,
    provenance_json: Path,
    evaluation_receipt_json: Path,
    selector_entry_receipt_json: Path,
    root: Path = ROOT,
    clean: bool = False,
) -> dict[str, Any]:
    """Create a portable digest-bound handoff directory for an accepted trace.

    This is intentionally a builder, not a promoter: the manifest keeps
    promotion_allowed=false and carries only enough subject identity for a cold
    reviewer to replay the selector-entry receipt and validate the bundled tools.
    """
    meta = load_meta(root)
    rev = str(meta.get("revision", "rev0000"))
    revno = int(meta.get("revision_number") or rev.replace("rev", "") or 0)
    if clean and handoff_dir.exists():
        shutil.rmtree(handoff_dir)
    handoff_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = handoff_dir / "evidence"
    receipts_dir = handoff_dir / "receipts"
    trace = _copy_preserving_name(trace_npz, evidence_dir, "public_trace.npz")
    prov = _copy_preserving_name(provenance_json, evidence_dir, "public_trace.provenance.json")
    eval_receipt = _copy_preserving_name(evaluation_receipt_json, receipts_dir, "evaluation_receipt.json")
    selector_receipt = _copy_preserving_name(selector_entry_receipt_json, receipts_dir, "selector_entry_receipt.json")
    eval_receipt_data = load_json(eval_receipt)
    selector_receipt_data = load_json(selector_receipt)
    trace_identity_sha256 = eval_receipt_data.get("trace_identity_sha256")
    selector_trace_identity_sha256 = selector_receipt_data.get("trace_identity_sha256")
    selector_entry_chain_sha256 = selector_receipt_data.get("selector_entry_chain_sha256")

    subjects: list[dict[str, Any]] = [
        {"name": "public_trace_npz", "path": _rel(handoff_dir, trace), "digest": {"sha256": sha256_file(trace)}},
        {"name": "public_trace_provenance_json", "path": _rel(handoff_dir, prov), "digest": {"sha256": sha256_file(prov)}},
        {"name": "public_trace_evaluation_receipt", "path": _rel(handoff_dir, eval_receipt), "digest": {"sha256": sha256_file(eval_receipt)}},
        {"name": "public_trace_selector_entry_receipt", "path": _rel(handoff_dir, selector_receipt), "digest": {"sha256": sha256_file(selector_receipt)}},
    ]
    for name, relpath in TOOLCHAIN_SUBJECTS.items():
        copied = _copy_tool(root, handoff_dir, relpath)
        subjects.append({"name": name, "path": relpath, "digest": {"sha256": sha256_file(copied)}})

    manifest = {
        "handoff_contract": HANDOFF_CONTRACT,
        "toolpack_contract": TOOLPACK_CONTRACT,
        "revision": rev,
        "revision_number": revno,
        "package_name": meta.get("package_name"),
        "archive_name": meta.get("archive_name"),
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": True,
        "gpu_fused_kernel_measured": False,
        "selector_entry_receipt_contract": SELECTOR_RECEIPT_CONTRACT,
        "evaluation_receipt_contract": EVALUATION_RECEIPT_CONTRACT,
        "trace_identity_receipt_contract": TRACE_IDENTITY_RECEIPT_CONTRACT,
        "trace_identity_sha256": trace_identity_sha256,
        "selector_trace_identity_sha256": selector_trace_identity_sha256,
        "trace_identity_chain_bound": bool(trace_identity_sha256 and trace_identity_sha256 == selector_trace_identity_sha256),
        "selector_entry_chain_contract": SELECTOR_ENTRY_CHAIN_CONTRACT,
        "selector_entry_chain_sha256": selector_entry_chain_sha256,
        "selector_entry_chain_bound": bool(selector_entry_chain_sha256),
        "paths_relative_to_manifest_dir": True,
        "subjects": subjects,
        "handoff_subject_set_sha256": subject_set_sha256(subjects),
        "toolpack_subject_set_sha256": toolpack_subject_set_sha256(subjects),
        "summary": "Portable public-trace handoff manifest for cold reviewers. It binds trace, provenance, evaluation receipt, selector-entry receipt, selector-entry chain digest, trace-identity hash, and verifier toolpack by SHA-256. This is selector-entry evidence, not promotion evidence; named-hardware timing is still required.",
    }
    manifest_path = handoff_dir / "PUBLIC_TRACE_HANDOFF_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return {"handoff_dir": handoff_dir, "manifest_path": manifest_path, "manifest": manifest}


def zip_dir(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        dest.unlink()
    with zipfile.ZipFile(dest, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                z.write(p, arcname=p.relative_to(src).as_posix())


def _load_gate(root: Path) -> Any:
    gate_path = root / "tools" / "public_trace_handoff_archive_gate.py"
    spec = importlib.util.spec_from_file_location("_handoff_builder_gate", gate_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import handoff gate")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a portable digest-bound public-trace handoff archive/directory from a real accepted trace and receipts.")
    ap.add_argument("--trace-npz", type=Path, required=True)
    ap.add_argument("--provenance-json", type=Path, required=True)
    ap.add_argument("--evaluation-receipt-json", type=Path, required=True)
    ap.add_argument("--selector-entry-receipt-json", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--out-zip", type=Path, default=None)
    ap.add_argument("--clean", action="store_true")
    ap.add_argument("--verify-strict", action="store_true", help="run the handoff archive gate after building and fail if replay does not verify")
    args = ap.parse_args()

    missing = [str(p) for p in [args.trace_npz, args.provenance_json, args.evaluation_receipt_json, args.selector_entry_receipt_json] if not p.exists()]
    if missing:
        print(json.dumps({"status": "fail", "errors": ["missing input: " + x for x in missing]}, indent=2))
        return 2

    result = build_handoff_directory(
        handoff_dir=args.out_dir,
        trace_npz=args.trace_npz,
        provenance_json=args.provenance_json,
        evaluation_receipt_json=args.evaluation_receipt_json,
        selector_entry_receipt_json=args.selector_entry_receipt_json,
        clean=args.clean,
    )
    zip_path = None
    if args.out_zip:
        zip_dir(args.out_dir, args.out_zip)
        zip_path = args.out_zip

    gate_summary: dict[str, Any] | None = None
    if args.verify_strict:
        gate = _load_gate(ROOT)
        gate_summary = gate.evaluate_handoff(handoff_dir=args.out_dir, manifest_path=result["manifest_path"], strict=True)
        if gate_summary.get("errors"):
            print(json.dumps({"status": "fail", "manifest": str(result["manifest_path"]), "zip": str(zip_path) if zip_path else None, "gate": gate_summary}, indent=2))
            return 1

    print(json.dumps({
        "status": "pass",
        "manifest": str(result["manifest_path"]),
        "zip": str(zip_path) if zip_path else None,
        "handoff_subject_set_sha256": result["manifest"].get("handoff_subject_set_sha256"),
        "toolpack_subject_set_sha256": result["manifest"].get("toolpack_subject_set_sha256"),
        "gate_verdict": gate_summary.get("verdict") if gate_summary else None,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
