#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0103"))
REVUP = REV.upper()
OUT = ROOT / "artifacts" / "audit"
OUT.mkdir(parents=True, exist_ok=True)


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8", errors="replace")


def load_gate():
    path = ROOT / "experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py"
    spec = importlib.util.spec_from_file_location("_runtime_gate_" + REVUP, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load gate surrogate")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    capture = read("experiments/public_trace_capture/hf_attention_trace_capture.py")
    gate_text = read("experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py")
    one_shot = (
        read("artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh")
        + "\n"
        + read(f"artifacts/capture-kit/{REVUP}_RUN_TINYLLAMA_PUBLIC_TRACE.sh")
        + "\n"
        + read(f"artifacts/capture-kit/{REVUP}_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh")
    )

    required_capture_terms = [
        "PUBLIC_RUNTIME_PROVENANCE_CONTRACT",
        "--torch-dtype",
        "--device",
        "_runtime_device_dtype_summary",
        "runtime_provenance_verified",
        "requested_torch_dtype",
        "resolved_torch_dtype",
        "actual_primary_device",
        "timing_clock_contract",
        "timing_cpu_perf_counter_recorded",
        "named_hardware_timing_measured",
    ]
    for term in required_capture_terms:
        if term not in capture:
            errors.append("capture helper missing runtime/dtype/timing term: " + term)

    required_gate_terms = [
        "PUBLIC_RUNTIME_PROVENANCE_CONTRACT",
        "PUBLIC_RUNTIME_PROVENANCE_FIELDS",
        "verify_runtime_provenance_contract",
        "runtime device/dtype/timing provenance",
        "named_hardware_timing_measured",
    ]
    for term in required_gate_terms:
        if term not in gate_text:
            errors.append("gate surrogate missing runtime contract term: " + term)

    for term in ["TRACE_TORCH_DTYPE", "TRACE_DEVICE", "--torch-dtype", "--device"]:
        if term not in one_shot:
            errors.append("current launcher path does not expose/pass " + term)

    try:
        gate = load_gate()
        good: dict[str, Any] = {
            "runtime_provenance_contract": gate.PUBLIC_RUNTIME_PROVENANCE_CONTRACT,
            "requested_torch_dtype": "float32",
            "resolved_torch_dtype": "torch.float32",
            "requested_device_policy": "auto",
            "actual_primary_device": "cpu",
            "model_parameter_dtype_set": json.dumps(["torch.float32"]),
            "model_device_set": json.dumps(["cpu"]),
            "model_parameter_tensor_count": 42,
            "cuda_available": False,
            "cuda_device_count": 0,
            "cuda_device_name": "not_available",
            "cuda_device_capability": "not_available",
            "timing_clock_contract": gate.PUBLIC_TIMING_CLOCK_CONTRACT,
            "timing_cpu_perf_counter_recorded": True,
            "timing_cuda_synchronized": False,
            "timing_cuda_event_recorded": False,
            "capture_elapsed_seconds": 0.01,
            "named_hardware_timing_measured": False,
            "runtime_provenance_verified": True,
        }
        cases = {
            "good_runtime_contract_passes": bool(gate.verify_runtime_provenance_contract(good).get("runtime_provenance_verified")),
            "missing_resolved_dtype_rejected": not bool(gate.verify_runtime_provenance_contract({k: v for k, v in good.items() if k != "resolved_torch_dtype"}).get("runtime_provenance_verified")),
            "timing_promotion_claim_rejected": not bool(gate.verify_runtime_provenance_contract({**good, "named_hardware_timing_measured": True}).get("runtime_provenance_verified")),
            "implicit_dtype_rejected": not bool(gate.verify_runtime_provenance_contract({**good, "requested_torch_dtype": "implicit_default"}).get("runtime_provenance_verified")),
        }
        for name, ok in cases.items():
            if not ok:
                errors.append("runtime contract test failed: " + name)
    except Exception as exc:
        cases = {"gate_import_or_case_execution_failed": repr(exc)}
        errors.append("could not execute gate runtime contract cases: " + repr(exc))

    blockers = [
        "runtime_dependencies_missing_here",
        "actual_public_pretrained_trace_missing",
        "named_hardware_sparse_vs_dense_timing_missing",
    ]
    audit = {
        "revision": REV,
        "revision_number": int(REV.replace("rev", "")),
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass_with_blockers" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "runtime_provenance_contract": "trace_runtime_device_dtype_timing_v1",
        "timing_clock_contract": "synchronized_perf_counter_or_cuda_event_v1",
        "summary": "Verifies that public trace capture and gate paths now require explicit torch dtype, device placement, runtime parameter dtype/device sets, synchronized timing-clock metadata, and a refusal to treat capture timing as named-hardware promotion evidence.",
        "case_results": cases,
        "errors": errors,
        "warnings": warnings,
        "blockers": blockers,
        "online_research_basis": [
            {"url": "https://huggingface.co/docs/transformers/en/main_classes/model", "note": "from_pretrained/model loading is part of runtime provenance; dtype/device must be explicit."},
            {"url": "https://huggingface.co/docs/transformers/en/attention_interface", "note": "attention backend identity is explicitly selectable and must be bound to dtype/device."},
            {"url": "https://docs.pytorch.org/docs/stable/generated/torch.cuda.Event.html", "note": "CUDA events are timing/synchronization markers; timing provenance must identify clock and synchronization."},
        ],
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_DEVICE_DTYPE_TIMING_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace device/dtype/timing audit — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        "Promotion allowed: `false`",
        "",
        "This audit prevents a public trace from silently changing load dtype, device placement, or timing-clock semantics after prompt/cache/backend identity has already been pinned.",
        "",
        "## Contract checks",
        "",
    ]
    for k, v in cases.items():
        md.append(f"- `{k}` = `{v}`")
    md.extend(["", "## Blockers", ""])
    md.extend([f"- `{b}`" for b in blockers])
    (OUT / f"{REVUP}_PUBLIC_TRACE_DEVICE_DTYPE_TIMING_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "errors": errors, "case_results": cases}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
