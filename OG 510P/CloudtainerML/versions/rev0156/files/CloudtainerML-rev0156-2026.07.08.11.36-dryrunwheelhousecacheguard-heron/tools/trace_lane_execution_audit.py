#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0093"))
REVUP = REV.upper()
OUT_AUDIT = ROOT / "artifacts" / "audit"
OUT_RUN = ROOT / "artifacts" / "run-manifests"
OUT_AUDIT.mkdir(parents=True, exist_ok=True)
OUT_RUN.mkdir(parents=True, exist_ok=True)


def optional_dep(name: str) -> dict[str, Any]:
    spec = importlib.util.find_spec(name)
    out: dict[str, Any] = {"available": bool(spec), "origin": getattr(spec, "origin", None) if spec else None}
    if not spec:
        return out
    try:
        module = importlib.import_module(name)
        out["version"] = getattr(module, "__version__", "unknown")
    except Exception as exc:
        out["available"] = False
        out["import_error"] = repr(exc)
    return out


def torch_runtime() -> dict[str, Any]:
    info = optional_dep("torch")
    if not info.get("available"):
        return info
    try:
        import torch  # type: ignore
        info.update({
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
            "cuda_device_names": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] if torch.cuda.is_available() else [],
            "torch_cuda_version": getattr(torch.version, "cuda", None),
        })
    except Exception as exc:
        info["runtime_error"] = repr(exc)
    return info


def cache_roots() -> list[Path]:
    roots: list[Path] = []
    for env_name, suffix in (("HF_HOME", "hub"),):
        env = os.environ.get(env_name)
        if env:
            roots.append(Path(env) / suffix)
    for env_name in ("HUGGINGFACE_HUB_CACHE", "TRANSFORMERS_CACHE"):
        env = os.environ.get(env_name)
        if env:
            roots.append(Path(env))
    roots.extend([
        Path.home() / ".cache" / "huggingface" / "hub",
        Path("/root/.cache/huggingface/hub"),
        Path("/mnt/data/.cache/huggingface/hub"),
    ])
    dedup: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = root.as_posix()
        if key not in seen:
            seen.add(key)
            dedup.append(root)
    return dedup


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def is_hex_revision(value: object) -> bool:
    s = str(value or "").strip()
    if s.startswith("sha256:"):
        s = s.split(":", 1)[1]
    return len(s) in {40, 64} and all(c in "0123456789abcdefABCDEF" for c in s)


def discover_snapshots() -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    for root in cache_roots():
        if not root.exists():
            continue
        for config in list(root.glob("models--*/snapshots/*/config.json"))[:250]:
            snap = config.parent
            key = snap.as_posix()
            if key in seen:
                continue
            seen.add(key)
            data = read_json(config) or {}
            files = [p.name for p in snap.iterdir() if p.is_file()]
            has_weights = any(name.endswith((".safetensors", ".bin", ".pt")) for name in files) or any(snap.glob("*.safetensors.index.json"))
            has_tokenizer = any((snap / name).exists() for name in ("tokenizer.json", "tokenizer.model", "vocab.json", "merges.txt"))
            revision = snap.name
            model_type = str(data.get("model_type", ""))
            arch = ",".join(map(str, data.get("architectures", [])))
            looks_llama = "llama" in model_type.lower() or "llama" in arch.lower() or "mistral" in model_type.lower() or "gemma" in model_type.lower()
            found.append({
                "snapshot": snap.as_posix(),
                "revision": revision,
                "immutable_revision_shape": is_hex_revision(revision),
                "model_type": model_type,
                "architectures": data.get("architectures", []),
                "has_config": True,
                "has_weights": bool(has_weights),
                "has_tokenizer_asset": bool(has_tokenizer),
                "looks_llama_family": bool(looks_llama),
                "ready_for_public_trace_candidate": bool(is_hex_revision(revision) and has_weights and has_tokenizer and looks_llama),
            })
    return found


def existing_real_trace_artifacts() -> list[str]:
    paths: list[str] = []
    for pat in [
        "artifacts/probe-results/REV*_PUBLIC_TRACE_GATE_REAL_MODEL.json",
        "artifacts/trace-bundles/REV*_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz",
        "artifacts/trace-bundles/REV*_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json",
    ]:
        paths.extend(p.relative_to(ROOT).as_posix() for p in ROOT.glob(pat))
    return sorted(paths)


def build_audit() -> dict[str, Any]:
    transformers = optional_dep("transformers")
    torch_info = torch_runtime()
    snapshots = discover_snapshots()
    ready_snaps = [s for s in snapshots if s.get("ready_for_public_trace_candidate")]
    real_trace = existing_real_trace_artifacts()
    blockers: list[str] = []
    if not transformers.get("available"):
        blockers.append("transformers_dependency_absent")
    if not ready_snaps:
        blockers.append("no_cached_hf_model_snapshot_with_config_weights_tokenizer_detected")
    if not torch_info.get("cuda_available"):
        blockers.append("cuda_gpu_not_available_for_named_hardware_timing_in_this_capsule")
    if not real_trace:
        blockers.append("actual_public_pretrained_prefill_plus_cached_decode_exact_length_greedy_generation_trace_missing")
    blockers.append("named_hardware_sparse_vs_dense_timing_missing")
    seen: set[str] = set()
    blockers = [b for b in blockers if not (b in seen or seen.add(b))]
    ready_to_run_capture = bool(transformers.get("available") and ready_snaps)
    ready_for_timing = bool(ready_to_run_capture and torch_info.get("cuda_available") and real_trace)
    run_script = f"artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh"
    current_command = (
        f"MODEL_ID=<reviewed model id or local path> MODEL_REVISION=<immutable commit hash> "
        f"WEIGHTS_SOURCE=<reviewed source> LICENSE=<reviewed license> DECODE_STEPS=2 bash {run_script}"
    )
    return {
        "revision": REV,
        "revision_number": int(str(REV).replace("rev", "")),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "ready_to_run_cached_capture" if ready_to_run_capture else "pass_with_blockers",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": bool(real_trace),
        "gpu_fused_kernel_measured": False,
        "summary": "Execution audit for the public trace lane. It prefers running the trace over adding new gates and records current blockers precisely.",
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "cwd": ROOT.as_posix(),
            "transformers": transformers,
            "torch": torch_info,
        },
        "hf_cache_scan": {
            "roots": [p.as_posix() for p in cache_roots()],
            "snapshot_count": len(snapshots),
            "ready_llama_like_snapshot_count": len(ready_snaps),
            "ready_snapshots": ready_snaps[:10],
        },
        "existing_real_trace_artifacts": real_trace,
        "blockers": blockers,
        "ready_to_run_capture_in_this_environment": ready_to_run_capture,
        "ready_for_named_hardware_timing_in_this_environment": ready_for_timing,
        "current_launch_script": run_script,
        "current_command_template": current_command,
        "required_env": ["MODEL_ID", "MODEL_REVISION", "WEIGHTS_SOURCE", "LICENSE"],
        "optional_env": ["TOKENIZER_REVISION", "DECODE_STEPS", "ALLOW_DOWNLOAD", "ATTENTION_IMPLEMENTATION", "MAX_ROWS"],
        "decision": "run_current_launch_script_on_real_trace_environment_or_stop_pivot",
    }


def write_md(audit: dict[str, Any], path: Path) -> None:
    blockers = "\n".join(f"- `{b}`" for b in audit.get("blockers", [])) or "- none"
    ready = audit.get("ready_to_run_capture_in_this_environment")
    cuda = audit.get("runtime", {}).get("torch", {}).get("cuda_available")
    tf = audit.get("runtime", {}).get("transformers", {}).get("available")
    snap_count = audit.get("hf_cache_scan", {}).get("ready_llama_like_snapshot_count")
    cmd = audit.get("current_command_template")
    txt = f"""# Trace lane execution audit — {REVUP}

Status: `{audit.get('status')}`  
Promotion allowed: `false`

## Capsule facts

- transformers available: `{tf}`
- CUDA available: `{cuda}`
- ready cached Llama-like snapshots: `{snap_count}`
- ready to run capture here: `{ready}`

## Blockers

{blockers}

## Current launch command template

```bash
{cmd}
```

## Interpretation

This is not a new gate. It is an execution audit that collapses the trace lane to a single runnable command and records why this capsule cannot complete it. The next useful work is a real run in an environment with `transformers`, reviewed immutable model/tokenizer revisions, and hardware for timing, or an explicit stop/pivot decision.
"""
    path.write_text(txt, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT_AUDIT / f"{REVUP}_TRACE_LANE_EXECUTION_AUDIT.json")
    parser.add_argument("--md-out", type=Path, default=OUT_AUDIT / f"{REVUP}_TRACE_LANE_EXECUTION_AUDIT.md")
    parser.add_argument("--launch-packet", type=Path, default=OUT_RUN / f"{REVUP}_PUBLIC_TRACE_LAUNCH_PACKET.json")
    args = parser.parse_args()
    audit = build_audit()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    write_md(audit, args.md_out)
    packet = {
        "revision": REV,
        "package_name": META.get("package_name"),
        "status": audit["status"],
        "purpose": "Single-command public trace launch packet; no promotion unless capture and gate artifacts pass.",
        "command_template": audit["current_command_template"],
        "required_env": audit["required_env"],
        "optional_env": audit["optional_env"],
        "blockers_in_this_capsule": audit["blockers"],
        "expected_outputs": [
            f"artifacts/trace-bundles/{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.npz",
            f"artifacts/trace-bundles/{REVUP}_PUBLIC_LLAMA_POST_TRANSFORM_TRACE.provenance.json",
            f"artifacts/probe-results/{REVUP}_PUBLIC_TRACE_GATE_REAL_MODEL.json",
        ],
        "post_run_validation": [
            "python tools/public_trace_token_provenance_audit.py",
            "python tools/public_trace_generation_token_audit.py",
            "python tools/public_trace_generation_determinism_audit.py",
            "python tools/public_trace_capture_readiness_audit.py",
            "python tools/smoke_validate.py",
            "sha256sum -c CHECKSUMS.sha256",
        ],
        "promotion_rule": "A real public trace can unblock only trace acceptance; performance promotion still requires named-hardware sparse-vs-dense timing.",
    }
    args.launch_packet.parent.mkdir(parents=True, exist_ok=True)
    args.launch_packet.write_text(json.dumps(packet, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "blockers": audit["blockers"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
