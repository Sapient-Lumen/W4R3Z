#!/usr/bin/env python3
"""Frozen historical rev0074 public-trace capture kit and replay dry-run.

This is a practical bridge from the slim offline capsule to the missing public /
pretrained trace evidence.  It does not claim public evidence locally.  Instead
it emits a small, self-contained capture/replay kit, checks runtime readiness,
then proves the exact ingest + native QK replay path on a non-public Q/K/V
fixture so the same commands can be run on a model-enabled machine.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import shutil
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HISTORICAL_RUNNER = True
ORIGINAL_REV = "rev0074"
REV = ORIGINAL_REV
REVUP = REV.upper()
STAMP = "2026-06-18T18:52:00-04:00"

OUT = ROOT / "artifacts" / "probe-results" / f"{REVUP}_PUBLIC_TRACE_CAPTURE_KIT.json"
MAN = ROOT / "artifacts" / "run-manifests" / f"{REVUP}_PUBLIC_TRACE_CAPTURE_KIT_RUN_MANIFEST.json"
KIT_DIR = ROOT / "artifacts" / "capture-kit"
TRACE_DIR = ROOT / "artifacts" / "trace-bundles"
NATIVE_IN = ROOT / "artifacts" / "native-inputs" / f"{REVUP}_PUBLIC_TRACE_CAPTURE_KIT_REPLAY_INPUT.bin"
BUILD_DIR = ROOT / "artifacts" / "native-build" / "public_trace_capture_kit"
GATE_SCRIPT = ROOT / "experiments" / "public_trace_gate_surrogate" / "public_trace_gate_surrogate.py"
CAPTURE_HELPER = ROOT / "experiments" / "public_trace_capture" / "hf_attention_trace_capture.py"
QK_CPP = ROOT / "experiments" / "trace_packet_qk_native_replay" / "trace_packet_qk_native_replay.cpp"
QK_EXE = BUILD_DIR / "trace_packet_qk_native_replay"
THIS = Path(__file__).resolve()
REGIME_IDS = {"low_support_lt12": 0, "mid_support_12_28": 1, "high_support_ge28": 2}
DEFAULT_REPEATS = int(os.environ.get("CTML_PUBLIC_TRACE_KIT_REPEATS", "220"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def module_status(name: str) -> dict[str, Any]:
    try:
        mod = __import__(name)
        return {"available": True, "version": str(getattr(mod, "__version__", "unknown"))}
    except Exception as exc:
        return {"available": False, "error": repr(exc)}


def environment_status() -> dict[str, Any]:
    torch_status = module_status("torch")
    cuda_available = False
    cuda_device_count = 0
    if torch_status.get("available"):
        try:
            import torch  # type: ignore
            cuda_available = bool(torch.cuda.is_available())
            cuda_device_count = int(torch.cuda.device_count()) if cuda_available else 0
        except Exception:
            cuda_available = False
            cuda_device_count = 0
    hf_home = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))
    hub = hf_home / "hub"
    cached = []
    if hub.exists():
        cached = [p.name for p in hub.glob("models--*")][:50]
    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "torch": torch_status,
        "transformers": module_status("transformers"),
        "transformer_lens": module_status("transformer_lens"),
        "cuda_available": cuda_available,
        "cuda_device_count": cuda_device_count,
        "hf_home": hf_home.as_posix(),
        "hf_hub_exists": hub.exists(),
        "cached_model_count_sampled": len(cached),
        "cached_models_sample": cached,
        "capture_helper_present": CAPTURE_HELPER.exists(),
        "capture_helper_sha256": sha256_file(CAPTURE_HELPER) if CAPTURE_HELPER.exists() else None,
        "gate_present": GATE_SCRIPT.exists(),
        "gate_sha256": sha256_file(GATE_SCRIPT) if GATE_SCRIPT.exists() else None,
        "native_qk_cpp_present": QK_CPP.exists(),
        "native_qk_cpp_sha256": sha256_file(QK_CPP) if QK_CPP.exists() else None,
        "compiler": shutil.which("g++") or shutil.which("c++"),
    }


def load_gate_module():
    spec = importlib.util.spec_from_file_location("public_trace_gate_surrogate_rev0075", GATE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import public trace gate")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def source_fixture() -> Path:
    candidates = [
        TRACE_DIR / f"{REVUP}_PUBLIC_TRACE_EXTERNAL_DRYRUN_QKV.npz",
        TRACE_DIR / "REV0073_SELF_DECLARED_LOCAL_FIXTURE_QKV.npz",
        TRACE_DIR / "REV0072_TRACE_CLAIM_FIXTURE_QKV.npz",
        TRACE_DIR / "REV0062_TINY_TRAINED_QK_TRACE_PACKET.npz",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("no q/k/v fixture available for capture-kit dry-run")


def read_qkv_npz(path: Path, *, limit: int | None = 64) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    z = np.load(path, allow_pickle=False)
    files = set(z.files)
    if {"q", "k", "v"}.issubset(files):
        q = np.asarray(z["q"], dtype=np.float64)
        k = np.asarray(z["k"], dtype=np.float64)
        v = np.asarray(z["v"], dtype=np.float64)
    elif {"queries", "keys", "values"}.issubset(files):
        q = np.asarray(z["queries"], dtype=np.float64)
        k = np.asarray(z["keys"], dtype=np.float64)
        v = np.asarray(z["values"], dtype=np.float64)
    else:
        raise ValueError("NPZ must contain q/k/v or queries/keys/values for native QK replay")
    if q.ndim != 2 or k.ndim != 3 or v.ndim != 3 or k.shape[0] != q.shape[0] or v.shape[:2] != k.shape[:2] or k.shape[2] != q.shape[1]:
        raise ValueError(f"bad q/k/v shapes: q={q.shape} k={k.shape} v={v.shape}")
    if limit is not None:
        limit = min(limit, q.shape[0])
        q, k, v = q[:limit], k[:limit], v[:limit]
    if "regime" in files:
        regimes = [str(x) for x in np.asarray(z["regime"]).astype(str)[: q.shape[0]]]
    else:
        regimes = ["unknown"] * int(q.shape[0])
    return q, k, v, regimes


def regime_id(name: str) -> int:
    if name in REGIME_IDS:
        return REGIME_IDS[name]
    # Public/pretrained traces may use arbitrary labels.  Unknown labels are
    # still replayable, but excluded from named low/mid/high support slices.
    return -1


def export_native_input(trace_npz: Path, *, limit: int | None = 64) -> dict[str, Any]:
    q, k, v, regimes = read_qkv_npz(trace_npz, limit=limit)
    NATIVE_IN.parent.mkdir(parents=True, exist_ok=True)
    ids = np.asarray([regime_id(r) for r in regimes], dtype=np.int32)
    with NATIVE_IN.open("wb") as f:
        f.write(b"CTMLTR62")
        f.write(struct.pack("<QQQQ", q.shape[0], k.shape[1], q.shape[1], v.shape[2]))
        f.write(np.ascontiguousarray(q, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(k, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(v, dtype=np.float64).tobytes(order="C"))
        f.write(np.ascontiguousarray(ids, dtype=np.int32).tobytes(order="C"))
    return {
        "trace_npz": trace_npz.relative_to(ROOT).as_posix() if trace_npz.is_relative_to(ROOT) else trace_npz.as_posix(),
        "trace_npz_sha256": sha256_file(trace_npz),
        "native_input": NATIVE_IN.relative_to(ROOT).as_posix(),
        "native_input_sha256": sha256_file(NATIVE_IN),
        "rows": int(q.shape[0]),
        "n_tokens": int(k.shape[1]),
        "d_key": int(q.shape[1]),
        "d_value": int(v.shape[2]),
        "regime_counts": {r: regimes.count(r) for r in sorted(set(regimes))},
        "unknown_regime_rows": int(sum(1 for r in regimes if regime_id(r) < 0)),
    }


def compile_native() -> dict[str, Any]:
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    compiler = shutil.which("g++") or shutil.which("c++")
    if compiler is None:
        raise RuntimeError("no C++ compiler available for native QK replay")
    cmd = [compiler, "-O3", "-std=c++17", str(QK_CPP), "-o", str(QK_EXE)]
    subprocess.run(cmd, cwd=ROOT, check=True)
    return {
        "compiler": compiler,
        "command": " ".join(cmd),
        "native_exe": QK_EXE.relative_to(ROOT).as_posix(),
        "cpp_sha256": sha256_file(QK_CPP),
    }


def run_native(repeats: int) -> dict[str, Any]:
    proc = subprocess.run([str(QK_EXE), str(NATIVE_IN), str(max(1, repeats))], cwd=ROOT, text=True, capture_output=True, check=True)
    return json.loads(proc.stdout)


def write_capture_kit_files() -> dict[str, Any]:
    KIT_DIR.mkdir(parents=True, exist_ok=True)
    readme = KIT_DIR / f"{REVUP}_PUBLIC_TRACE_CAPTURE_KIT_README.md"
    runner = KIT_DIR / f"{REVUP}_RUN_PUBLIC_TRACE_CAPTURE_AND_REPLAY.sh"
    schema = KIT_DIR / f"{REVUP}_PUBLIC_TRACE_PROVENANCE_SCHEMA.json"
    checklist = KIT_DIR / f"{REVUP}_PUBLIC_TRACE_CAPTURE_CHECKLIST.md"
    readme.write_text(f"""# CloudtainerML {REV} public trace capture kit

This kit is the smallest handoff for the remaining blocker: capture a real public/pretrained Q/K/V trace bundle, prove its provenance, then replay it through the CloudtainerML sparse-attention gates.

It is intentionally fail-closed. A trace is **not** public/pretrained merely because it is schema-valid. It must have both:

1. NPZ self-attestation fields emitted by `experiments/public_trace_capture/hf_attention_trace_capture.py`; and
2. a matching JSON provenance manifest with reviewed model/source/license fields and the NPZ SHA-256.

## Minimal local-files-only command

```bash
python experiments/public_trace_capture/hf_attention_trace_capture.py \
  --model <local-public-model-id-or-path> \
  --out artifacts/trace-bundles/PUBLIC_MODEL_QKV.npz \
  --provenance-out artifacts/trace-bundles/PUBLIC_MODEL_QKV.provenance.json \
  --public-pretrained-trace \
  --weights-source '<exact public checkpoint/source>' \
  --license '<model license/source terms>' \
  --provenance-reviewed
```

Then validate and replay:

```bash
python experiments/public_trace_capture_kit/public_trace_capture_kit.py \
  --trace-npz artifacts/trace-bundles/PUBLIC_MODEL_QKV.npz \
  --provenance-json artifacts/trace-bundles/PUBLIC_MODEL_QKV.provenance.json \
  --claim-public \
  --repeats 300
```

Do not pass `--allow-download` to the capture helper unless network/model-source policy allows downloads and the provenance manifest records that fact.
""", encoding="utf-8")
    runner.write_text("""#!/usr/bin/env bash
set -euo pipefail
MODEL="${1:?model id or local model path}"
OUT="${2:-artifacts/trace-bundles/PUBLIC_MODEL_QKV.npz}"
MAN="${3:-artifacts/trace-bundles/PUBLIC_MODEL_QKV.provenance.json}"
WEIGHTS_SOURCE="${WEIGHTS_SOURCE:?set WEIGHTS_SOURCE to exact public checkpoint/source}"
LICENSE_NOTE="${LICENSE_NOTE:?set LICENSE_NOTE to model license/source terms}"
python experiments/public_trace_capture/hf_attention_trace_capture.py \
  --model "$MODEL" \
  --out "$OUT" \
  --provenance-out "$MAN" \
  --public-pretrained-trace \
  --weights-source "$WEIGHTS_SOURCE" \
  --license "$LICENSE_NOTE" \
  --provenance-reviewed
python experiments/public_trace_capture_kit/public_trace_capture_kit.py \
  --trace-npz "$OUT" \
  --provenance-json "$MAN" \
  --claim-public \
  --repeats "${REPEATS:-300}"
""", encoding="utf-8")
    runner.chmod(0o755)
    schema_payload = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CloudtainerML public/pretrained trace provenance manifest",
        "type": "object",
        "required": [
            "trace_claim_version", "public_pretrained_trace", "source_type", "model_id", "weights_source", "license",
            "trace_npz_sha256", "schema", "capture_tool", "capture_tool_sha256",
            "generated_from_local_tiny_model", "uses_random_weights", "provenance_reviewed",
        ],
        "properties": {
            "trace_claim_version": {"const": "public_trace_claim_v1"},
            "public_pretrained_trace": {"const": True},
            "source_type": {"enum": ["public_pretrained_hf", "public_pretrained_transformerlens", "public_pretrained_manual_export"]},
            "model_id": {"type": "string", "minLength": 1},
            "weights_source": {"type": "string", "minLength": 1},
            "license": {"type": "string", "minLength": 1},
            "trace_npz_sha256": {"type": "string", "pattern": "^[0-9a-fA-F]{64}$"},
            "schema": {"enum": ["qkv_npz_v1", "scores_values_npz_v1"]},
            "capture_tool": {"type": "string", "minLength": 1},
            "capture_tool_sha256": {"type": "string", "pattern": "^[0-9a-fA-F]{64}$"},
            "generated_from_local_tiny_model": {"const": False},
            "uses_random_weights": {"const": False},
            "provenance_reviewed": {"const": True},
        },
        "additionalProperties": True,
    }
    schema.write_text(json.dumps(schema_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checklist.write_text(f"""# Public trace capture checklist — {REV}

- [ ] `transformers` or TransformerLens is installed in the capture environment.
- [ ] The model is a public/pretrained checkpoint, not local tiny, random, or fixture weights.
- [ ] The model source and license/source terms are recorded.
- [ ] The capture helper emits NPZ self-attestation fields.
- [ ] The JSON manifest SHA-256 matches the NPZ.
- [ ] `public_trace_gate_surrogate.py` accepts the public/pretrained claim.
- [ ] Native QK replay runs on the captured packet.
- [ ] GPU/fused-kernel timing is still not claimed unless separately measured.
""", encoding="utf-8")
    files = [readme, runner, schema, checklist]
    return {p.relative_to(ROOT).as_posix(): sha256_file(p) for p in files}


def compact_gate(payload: dict[str, Any]) -> dict[str, Any]:
    decl = payload.get("external_trace_declaration", {})
    prov = decl.get("provenance_status", {})
    npz = prov.get("npz_metadata_status", {})
    summ = payload.get("summary", {})
    return {
        "trace_gate_status": payload.get("trace_gate_status"),
        "external_trace_loaded": payload.get("external_trace_loaded"),
        "declared_public_pretrained_trace": decl.get("declared_public_pretrained_trace"),
        "public_pretrained_trace_loaded": payload.get("public_pretrained_trace_loaded"),
        "accepted_as_public_pretrained_trace": decl.get("accepted_as_public_pretrained_trace"),
        "provenance_status": prov.get("status"),
        "provenance_errors": prov.get("errors", [])[:10],
        "npz_metadata_status": npz.get("status"),
        "npz_red_flag_terms": npz.get("red_flag_terms", []),
        "oracle_leakage_rows": int(summ.get("oracle_leakage_rows") or 0),
        "trace_row_count": int(summ.get("trace_row_count") or 0),
        "result_row_count": int(summ.get("result_row_count") or 0),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace-npz", type=Path, default=None, help="optional external Q/K/V public trace bundle to validate and replay")
    ap.add_argument("--provenance-json", type=Path, default=None, help="paired provenance manifest for public/pretrained claims")
    ap.add_argument("--claim-public", action="store_true", help="attempt to accept the bundle as public/pretrained evidence")
    ap.add_argument("--limit-rows", type=int, default=64)
    ap.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    args = ap.parse_args()

    env = environment_status()
    kit_files = write_capture_kit_files()
    gate = load_gate_module()
    trace_npz = args.trace_npz or source_fixture()
    trace_npz = trace_npz if trace_npz.is_absolute() else ROOT / trace_npz
    provenance_json = args.provenance_json
    if provenance_json is not None and not provenance_json.is_absolute():
        provenance_json = ROOT / provenance_json

    gate_payload = gate.run(
        trace_npz,
        public_pretrained_trace=bool(args.claim_public),
        trace_source_label=("rev0074_capture_kit_candidate" if args.claim_public else "rev0074_capture_kit_nonpublic_dryrun"),
        bundle_model_id=None,
        bundle_license=None,
        provenance_json=provenance_json,
    )
    gate_summary = compact_gate(gate_payload)

    exported = export_native_input(trace_npz, limit=max(1, args.limit_rows))
    compiled = compile_native()
    native = run_native(max(1, args.repeats))

    public_loaded = bool(gate_summary.get("public_pretrained_trace_loaded"))
    capture_executable = bool(env["torch"].get("available") and env["transformers"].get("available") and env.get("cached_model_count_sampled", 0) > 0)
    native_speed = float(native.get("timing", {}).get("mass_histogram_speedup_vs_dense_qk_online", 0.0))
    native_quality = float(native.get("all_rows", {}).get("quality_rate", 0.0))
    public_replay_ready = bool(gate_summary.get("external_trace_loaded") and exported["rows"] > 0 and native.get("rows") == exported["rows"])
    promotion_allowed = bool(public_loaded and native_quality >= 0.999 and native_speed > 1.0 and False)  # GPU/fused timing is still absent.

    summary = {
        "kit_files_written": len(kit_files),
        "capture_executable_in_this_capsule": capture_executable,
        "trace_npz_used": exported["trace_npz"],
        "external_trace_loaded": bool(gate_summary.get("external_trace_loaded")),
        "public_pretrained_trace_loaded": public_loaded,
        "public_replay_adapter_ready": public_replay_ready,
        "native_qk_replay_rows": int(native.get("rows", 0)),
        "native_mass_histogram_quality_rate": native_quality,
        "native_mass_histogram_speedup_vs_dense_qk_online": native_speed,
        "oracle_leakage_rows": int(gate_summary.get("oracle_leakage_rows") or 0),
        "promotion_allowed": promotion_allowed,
        "blocked_reason": None if public_loaded else "no accepted public/pretrained trace bundle supplied; local dry-run remains non-public",
        "remaining_blockers": [
            "actual_public_pretrained_trace_bundle_missing" if not public_loaded else "gpu_fused_attention_kernel_timing_missing",
            "native_replay_is_cpu_materialized_path_not_gpu_fused_kernel",
            "score_storage_materialization_claim_must_remain_separate",
        ],
    }
    artifact = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": f"{REVUP}_PUBLIC_TRACE_CAPTURE_KIT",
        "generated_at": STAMP,
        "status": "public_trace_capture_kit_ready_no_public_trace_loaded" if not public_loaded else "public_trace_bundle_ingested_native_cpu_replayed_gpu_still_missing",
        "measurement_scope": "portable public/pretrained Q/K/V capture kit, fail-closed public claim gate, and native CPU QK replay adapter dry-run; no GPU/fused timing claim",
        "promotion_allowed": promotion_allowed,
        "public_pretrained_trace_loaded": public_loaded,
        "gpu_fused_kernel_measured": False,
        "environment": env,
        "capture_kit_files": kit_files,
        "gate_result": gate_summary,
        "native_input": exported,
        "native_build": compiled,
        "native_result": native,
        "summary": summary,
        "interpretation": "rev0074 turned the public/pretrained trace blocker into a portable capture-and-replay kit. This capsule can prove the path on a non-public Q/K/V fixture, but it still does not contain an accepted public/pretrained trace bundle or GPU/fused kernel timing.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "project": "CloudtainerML",
        "revision": REV,
        "artifact": OUT.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256_file(OUT),
        "generated_at": STAMP,
        "command": "python experiments/public_trace_capture_kit/public_trace_capture_kit.py",
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.platform(),
        "source_files": {
            THIS.relative_to(ROOT).as_posix(): sha256_file(THIS),
            GATE_SCRIPT.relative_to(ROOT).as_posix(): sha256_file(GATE_SCRIPT),
            CAPTURE_HELPER.relative_to(ROOT).as_posix(): sha256_file(CAPTURE_HELPER),
            QK_CPP.relative_to(ROOT).as_posix(): sha256_file(QK_CPP),
        },
        "inputs": {
            exported["trace_npz"]: exported["trace_npz_sha256"],
            exported["native_input"]: exported["native_input_sha256"],
        },
        "capture_kit_files": kit_files,
        "promotion_allowed": promotion_allowed,
        "public_pretrained_trace_loaded": public_loaded,
        "gpu_fused_kernel_measured": False,
    }
    MAN.parent.mkdir(parents=True, exist_ok=True)
    MAN.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": artifact["status"], "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
