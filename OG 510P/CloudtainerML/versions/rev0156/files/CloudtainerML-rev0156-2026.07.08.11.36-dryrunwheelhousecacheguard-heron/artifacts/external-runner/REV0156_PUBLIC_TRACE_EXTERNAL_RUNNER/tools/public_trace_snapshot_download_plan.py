#!/usr/bin/env python3
from __future__ import annotations

import argparse
import inspect
import json
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.hf_snapshot_integrity import (  # noqa: E402
    ALLOW_PATTERNS,
    DEFAULT_MODEL_ID,
    DEFAULT_REVISION,
    EXPECTED_MODEL_SAFETENSORS_SHA256,
    REQUIRED_SNAPSHOT_FILES,
    snapshot_path,
)

META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0000"))
REVUP = REV.upper()
REVNO = int(str(META.get("revision_number", REV.replace("rev", "0"))))
OUT_AUDIT = ROOT / "artifacts" / "audit"
OUT_MANIFEST = ROOT / "artifacts" / "run-manifests"
OUT_RUNTIME = ROOT / "artifacts" / "runtime"
for d in (OUT_AUDIT, OUT_MANIFEST, OUT_RUNTIME):
    d.mkdir(parents=True, exist_ok=True)

CONTRACT = "hf_snapshot_download_dry_run_byte_budget_v1"
DEFAULT_CACHE_ROOT = ROOT / "artifacts" / "runtime" / "public-trace-hf-cache"
DEFAULT_HEADROOM_BYTES = 1_073_741_824  # 1 GiB extra beyond planned download bytes.


def env_path(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    if value:
        return Path(value).expanduser()
    return default


def cache_root() -> Path:
    raw = os.environ.get("PUBLIC_TRACE_CACHE_ROOT")
    if raw:
        p = Path(raw).expanduser()
        return p if p.is_absolute() else ROOT / p
    return DEFAULT_CACHE_ROOT


def hub_cache_dir() -> Path:
    if os.environ.get("HF_HUB_CACHE"):
        return Path(os.environ["HF_HUB_CACHE"]).expanduser()
    return cache_root() / "hub"


def simple_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (list, tuple)):
        return [simple_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): simple_value(v) for k, v in value.items()}
    return repr(value)


def dry_info_to_dict(info: Any) -> dict[str, Any]:
    out: dict[str, Any] = {}
    # DryRunFileInfo is a dataclass-like object in current huggingface_hub, but
    # keep this resilient across minor releases because this gate exists to fail early.
    if hasattr(info, "__dict__"):
        for k, v in vars(info).items():
            if not k.startswith("_"):
                out[k] = simple_value(v)
    for attr in [
        "filename", "file_name", "path", "file_path", "repo_file_path", "local_path",
        "file_size", "size", "size_on_disk", "commit_hash", "is_cached", "will_download",
        "should_download", "blob_id", "lfs", "is_lfs",
    ]:
        if attr not in out and hasattr(info, attr):
            try:
                out[attr] = simple_value(getattr(info, attr))
            except Exception as exc:
                out[attr + "_error"] = type(exc).__name__ + ": " + repr(exc)
    return out


def get_name(rec: dict[str, Any]) -> str:
    for key in ["filename", "file_name", "repo_file_path", "file_path", "path"]:
        value = rec.get(key)
        if value:
            return str(value).replace("\\", "/")
    lp = rec.get("local_path")
    if lp:
        return Path(str(lp)).name
    return ""


def get_size(rec: dict[str, Any]) -> int | None:
    for key in ["file_size", "size", "size_on_disk", "bytes"]:
        value = rec.get(key)
        if value is None or value == "":
            continue
        try:
            iv = int(value)
            if iv >= 0:
                return iv
        except Exception:
            pass
    return None


def get_will_download(rec: dict[str, Any]) -> bool | None:
    for key in ["will_download", "should_download"]:
        if key in rec and rec[key] is not None:
            return bool(rec[key])
    if "is_cached" in rec and rec["is_cached"] is not None:
        return not bool(rec["is_cached"])
    return None


def byte_count_text(n: int | None) -> str:
    if n is None:
        return "unknown"
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    x = float(n)
    for unit in units:
        if x < 1024 or unit == units[-1]:
            return f"{x:.1f} {unit}"
        x /= 1024
    return str(n)


def write_outputs(audit: dict[str, Any]) -> None:
    for out in [
        OUT_AUDIT / f"{REVUP}_PUBLIC_TRACE_SNAPSHOT_DOWNLOAD_PLAN.json",
        OUT_MANIFEST / f"{REVUP}_PUBLIC_TRACE_SNAPSHOT_DOWNLOAD_PLAN.json",
        OUT_RUNTIME / "CURRENT_PUBLIC_TRACE_SNAPSHOT_DOWNLOAD_PLAN.json",
    ]:
        out.write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace snapshot download plan — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        "Promotion allowed: `false`",
        "",
        audit.get("summary", ""),
        "",
        "## Plan",
        "",
        f"- model: `{audit.get('model_id')}`",
        f"- revision: `{audit.get('model_revision')}`",
        f"- cache dir: `{audit.get('cache_dir')}`",
        f"- files planned: `{audit.get('planned_file_count')}`",
        f"- bytes to download: `{byte_count_text(audit.get('bytes_to_download'))}`",
        f"- free bytes in cache filesystem: `{byte_count_text(audit.get('cache_filesystem_free_bytes'))}`",
        "",
        "## Blockers",
        "",
    ]
    md.extend([f"- `{b}`" for b in audit.get("blockers", [])] if audit.get("blockers") else ["- none"])
    md.extend(["", "## Warnings", ""])
    md.extend([f"- `{w}`" for w in audit.get("warnings", [])] if audit.get("warnings") else ["- none"])
    md.extend(["", "## Interpretation", "", "This is a snapshot-preparation receipt only. It does not claim a public trace; it prevents wasting network/disk before the evidence-capture runner has a coherent locked-revision file plan."])
    (OUT_AUDIT / f"{REVUP}_PUBLIC_TRACE_SNAPSHOT_DOWNLOAD_PLAN.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def skipped_audit(reason: str) -> dict[str, Any]:
    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "skipped",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Snapshot download-plan gate was explicitly skipped. This is permitted only for unusual operator environments and should not be treated as evidence.",
        "contract": CONTRACT,
        "skip_reason": reason,
        "blockers": [],
        "warnings": ["download_plan_gate_skipped_by_operator"],
    }
    write_outputs(audit)
    return audit


def main() -> int:
    ap = argparse.ArgumentParser(description="Dry-run/byte-budget gate before materializing the locked TinyLlama snapshot.")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--skip-network", action="store_true", help="Write a skipped receipt without importing/calling huggingface_hub.")
    ap.add_argument("--cache-dir", type=Path, default=None)
    ap.add_argument("--min-free-gb", type=float, default=None)
    ap.add_argument("--headroom-bytes", type=int, default=None)
    args = ap.parse_args()

    if args.skip_network:
        audit = skipped_audit("skip_network_argument")
        print(json.dumps({"status": audit["status"], "warnings": audit["warnings"]}, indent=2))
        return 0

    model_id = os.environ.get("MODEL_ID", DEFAULT_MODEL_ID)
    revision = os.environ.get("MODEL_REVISION", DEFAULT_REVISION)
    cache_dir = (args.cache_dir.expanduser() if args.cache_dir else hub_cache_dir())
    if not cache_dir.is_absolute():
        cache_dir = ROOT / cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    expected_snapshot = snapshot_path(cache_dir, model_id, revision)

    blockers: list[str] = []
    warnings: list[str] = []
    dry_run_records: list[dict[str, Any]] = []
    dry_run_error = None
    signature = ""
    hub_version = None

    try:
        import huggingface_hub  # type: ignore
        from huggingface_hub import snapshot_download  # type: ignore
        hub_version = getattr(huggingface_hub, "__version__", None)
        signature = str(inspect.signature(snapshot_download))
        if "dry_run" not in signature:
            blockers.append("huggingface_hub_snapshot_download_has_no_dry_run_parameter")
        else:
            dry_infos = snapshot_download(
                repo_id=model_id,
                revision=revision,
                cache_dir=str(cache_dir),
                allow_patterns=list(ALLOW_PATTERNS),
                dry_run=True,
            )
            if not isinstance(dry_infos, (list, tuple)):
                dry_infos = [dry_infos]
            dry_run_records = [dry_info_to_dict(info) for info in dry_infos]
    except Exception as exc:
        dry_run_error = type(exc).__name__ + ": " + repr(exc)
        blockers.append("snapshot_download_dry_run_failed")

    names = [get_name(r) for r in dry_run_records]
    names = [n for n in names if n]
    missing_required = []
    for req in REQUIRED_SNAPSHOT_FILES:
        if not any(n == req or n.endswith("/" + req) for n in names):
            missing_required.append(req)
    if dry_run_records and missing_required:
        blockers.append("dry_run_missing_required_snapshot_files:" + ",".join(missing_required))

    commit_hashes = sorted({str(r.get("commit_hash")) for r in dry_run_records if r.get("commit_hash")})
    if commit_hashes and revision not in commit_hashes:
        blockers.append("dry_run_commit_hash_does_not_match_locked_revision")
    if len(commit_hashes) > 1:
        warnings.append("dry_run_reported_multiple_commit_hashes")

    bytes_total_known = 0
    bytes_to_download = 0
    unknown_sizes = []
    unknown_download_flags = []
    planned_files = []
    for rec in dry_run_records:
        name = get_name(rec)
        size = get_size(rec)
        will_download = get_will_download(rec)
        if size is None:
            unknown_sizes.append(name or repr(rec)[:120])
        else:
            bytes_total_known += size
        if will_download is None:
            unknown_download_flags.append(name or repr(rec)[:120])
        elif will_download and size is not None:
            bytes_to_download += size
        planned_files.append({
            "name": name,
            "size": size,
            "will_download": will_download,
            "is_cached": rec.get("is_cached"),
            "commit_hash": rec.get("commit_hash"),
            "raw": rec,
        })
    if unknown_sizes:
        blockers.append("dry_run_missing_file_size_for_some_files")
    if unknown_download_flags:
        warnings.append("dry_run_missing_download_flag_for_some_files")

    usage = shutil.disk_usage(cache_dir)
    headroom = args.headroom_bytes if args.headroom_bytes is not None else int(os.environ.get("PUBLIC_TRACE_DOWNLOAD_PLAN_HEADROOM_BYTES", DEFAULT_HEADROOM_BYTES))
    min_free_bytes = None
    if args.min_free_gb is not None:
        min_free_bytes = int(args.min_free_gb * (1024 ** 3))
    elif os.environ.get("PUBLIC_TRACE_DOWNLOAD_PLAN_MIN_FREE_GB"):
        min_free_bytes = int(float(os.environ["PUBLIC_TRACE_DOWNLOAD_PLAN_MIN_FREE_GB"]) * (1024 ** 3))
    elif os.environ.get("PUBLIC_TRACE_DOWNLOAD_PLAN_MIN_FREE_BYTES"):
        min_free_bytes = int(os.environ["PUBLIC_TRACE_DOWNLOAD_PLAN_MIN_FREE_BYTES"])
    needed_free = max(bytes_to_download + headroom, min_free_bytes or 0)
    if dry_run_records and usage.free < needed_free:
        blockers.append("insufficient_free_space_for_planned_snapshot_download_plus_headroom")

    status = "pass" if not blockers else "blocked_here"
    audit: dict[str, Any] = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": status,
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Dry-run and byte-budget receipt for the locked TinyLlama snapshot before any large materialization. This is a waste-control and source-plan gate; evidence capture remains local-only after preparation.",
        "contract": CONTRACT,
        "model_id": model_id,
        "model_revision": revision,
        "expected_model_safetensors_sha256": EXPECTED_MODEL_SAFETENSORS_SHA256,
        "required_snapshot_files": REQUIRED_SNAPSHOT_FILES,
        "allow_patterns": ALLOW_PATTERNS,
        "cache_root": str(cache_root()),
        "cache_dir": str(cache_dir),
        "expected_snapshot_path": str(expected_snapshot),
        "huggingface_hub_version": hub_version,
        "snapshot_download_signature": signature,
        "dry_run_error": dry_run_error,
        "planned_file_count": len(planned_files),
        "planned_files": planned_files,
        "reported_commit_hashes": commit_hashes,
        "missing_required_files": missing_required,
        "bytes_total_known": bytes_total_known,
        "bytes_to_download": bytes_to_download,
        "unknown_sizes": unknown_sizes,
        "unknown_download_flags": unknown_download_flags,
        "cache_filesystem_total_bytes": usage.total,
        "cache_filesystem_used_bytes": usage.used,
        "cache_filesystem_free_bytes": usage.free,
        "headroom_bytes": headroom,
        "min_free_bytes": min_free_bytes,
        "needed_free_bytes": needed_free,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "source_basis": [
            {"url": "https://huggingface.co/docs/huggingface_hub/en/guides/download", "note": "snapshot_download supports programmatic dry_run with file size/cache/download information."},
            {"url": "https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables", "note": "HF_HOME, HF_HUB_CACHE, and HF_XET_CACHE are read at import time, so this script must run after cache env binding and before materialization."},
            {"url": "https://huggingface.co/docs/huggingface_hub/en/guides/manage-cache", "note": "Hub cache roots and snapshot directories are explicit filesystem targets suitable for preflight disk budgeting."},
        ],
        "python": {"version": platform.python_version(), "executable": sys.executable, "platform": platform.platform()},
    }
    write_outputs(audit)
    print(json.dumps({"status": status, "bytes_to_download": bytes_to_download, "blockers": audit["blockers"], "warnings": audit["warnings"]}, indent=2))
    return 0 if (status == "pass" or not args.strict) else 1


if __name__ == "__main__":
    raise SystemExit(main())
