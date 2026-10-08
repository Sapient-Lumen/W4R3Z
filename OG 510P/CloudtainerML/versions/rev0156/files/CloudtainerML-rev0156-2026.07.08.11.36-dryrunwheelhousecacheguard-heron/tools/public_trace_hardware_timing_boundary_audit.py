#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = json.loads((ROOT / "CUBE-META.json").read_text(encoding="utf-8"))
REV = str(META.get("revision", "rev0105"))
REVUP = REV.upper()
REVNO = int(REV.replace("rev", ""))
OUT = ROOT / "artifacts" / "audit"
MAN = ROOT / "artifacts" / "run-manifests"
OUT.mkdir(parents=True, exist_ok=True)
MAN.mkdir(parents=True, exist_ok=True)


def read(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    capture = read("experiments/public_trace_capture/hf_attention_trace_capture.py")
    gate = read("experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py")
    readiness = read("tools/public_trace_readiness_gate.py")
    docs = "\n".join(read(rel) for rel in ["START_HERE.md", "START_HERE_SLIM.md", "README.md", "PRIORITY-LIST.md", "MISSION-KERNEL.md"])

    required_pairs = [
        ("capture helper", capture, "named_hardware_timing_measured"),
        ("capture helper", capture, '"named_hardware_timing_measured": False'),
        ("gate surrogate", gate, "named_hardware_timing_measured must remain false"),
        ("readiness gate", readiness, "hardware_timing_boundary"),
        ("docs", docs, "named-hardware"),
        ("docs", docs, "promotion"),
    ]
    for label, text, needle in required_pairs:
        if needle not in text:
            errors.append(f"{label} missing hardware-timing boundary marker: {needle}")

    timing_contract = {
        "revision": REV,
        "revision_number": REVNO,
        "contract": "named_hardware_sparse_vs_dense_timing_promotion_v1",
        "status": "blocked_missing_named_hardware_timing",
        "promotion_allowed": False,
        "trace_capture_timing_is_diagnostic_only": True,
        "requires_accepted_public_trace_before_timing_promotion": True,
        "required_named_hardware_fields": [
            "hardware_run_id",
            "machine_owner_or_lab",
            "gpu_name",
            "gpu_uuid_or_redacted_stable_id",
            "gpu_count",
            "driver_version",
            "cuda_runtime_version",
            "torch_version",
            "transformers_version",
            "attention_backend_dense",
            "attention_backend_sparse_candidate",
            "model_id",
            "model_revision",
            "trace_gate_artifact_sha256",
            "dtype",
            "batch_shape",
            "context_lengths",
            "decode_steps",
            "warmup_iterations",
            "measured_iterations",
            "timing_clock",
            "cuda_event_timing_used",
            "torch_cuda_synchronize_before_after",
            "dense_latency_ms_p50_p95",
            "sparse_latency_ms_p50_p95",
            "quality_or_exactness_delta",
            "raw_command_log",
        ],
        "minimum_acceptance_rule": "No speed/performance promotion unless a gate-accepted public trace is paired with named hardware, dense baseline, sparse candidate, identical prompts/shapes/dtype, warmups, repeated trials, CUDA-event or equivalent synchronized GPU timing, and raw logs.",
    }
    (MAN / f"{REVUP}_NAMED_HARDWARE_TIMING_CONTRACT.json").write_text(json.dumps(timing_contract, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md_contract = [
        f"# Named hardware timing contract — {REVUP}",
        "",
        "Status: `blocked_missing_named_hardware_timing`  ",
        "Promotion allowed: `false`",
        "",
        "Trace capture timing is diagnostic provenance only. Promotion timing requires a separate named-hardware sparse-vs-dense run after the public trace gate accepts a real model trace.",
        "",
        "## Required fields",
    ]
    md_contract.extend(f"- `{x}`" for x in timing_contract["required_named_hardware_fields"])
    (MAN / f"{REVUP}_NAMED_HARDWARE_TIMING_CONTRACT.md").write_text("\n".join(md_contract) + "\n", encoding="utf-8")

    blockers = [
        "named_hardware_sparse_vs_dense_timing_missing",
        "accepted_public_trace_required_before_performance_promotion",
    ]
    audit = {
        "revision": REV,
        "revision_number": REVNO,
        "package_name": META.get("package_name"),
        "archive_name": META.get("archive_name"),
        "status": "pass_with_blockers" if not errors else "fail",
        "promotion_allowed": False,
        "public_pretrained_trace_loaded": False,
        "gpu_fused_kernel_measured": False,
        "summary": "Separates diagnostic trace-capture timing from named-hardware sparse-vs-dense promotion evidence.",
        "boundary_checks": {
            "capture_forces_named_hardware_false": '"named_hardware_timing_measured": False' in capture,
            "gate_rejects_named_hardware_true_in_trace_provenance": "named_hardware_timing_measured must remain false" in gate,
            "readiness_gate_runs_this_audit": "hardware_timing_boundary" in readiness,
            "docs_state_named_hardware_boundary": "named-hardware" in docs and "promotion" in docs,
        },
        "blockers": blockers,
        "errors": errors,
        "warnings": warnings,
        "online_research_basis": [
            {
                "source": "Hugging Face Transformers generation docs",
                "url": "https://huggingface.co/docs/transformers/main_classes/text_generation",
                "note": "Generation cache and decoding knobs are explicit runtime semantics; performance comparisons must bind them rather than inherit defaults.",
            },
            {
                "source": "Hugging Face attention interface docs",
                "url": "https://huggingface.co/docs/transformers/attention_interface",
                "note": "Attention backend and mask conventions differ, so timing evidence must name the dense and sparse/candidate backends.",
            },
            {
                "source": "PyTorch CUDA Event docs",
                "url": "https://docs.pytorch.org/docs/stable/generated/torch.cuda.Event.html",
                "note": "CUDA events are synchronization markers for monitoring device progress and measuring timing.",
            },
            {
                "source": "Torch-TensorRT performance tuning guide",
                "url": "https://docs.pytorch.org/TensorRT/user_guide/performance_tuning.html",
                "note": "GPU benchmarks need warmups, synchronization, CUDA events, and consistent precision.",
            },
        ],
    }
    (OUT / f"{REVUP}_PUBLIC_TRACE_HARDWARE_TIMING_BOUNDARY_AUDIT.json").write_text(json.dumps(audit, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    md = [
        f"# Public trace hardware timing boundary audit — {REVUP}",
        "",
        f"Status: `{audit['status']}`  ",
        "Promotion allowed: `false`",
        "",
        "This audit closes a false-green path where diagnostic capture timing could be mistaken for named-hardware sparse-vs-dense evidence.",
        "",
        "## Blockers",
    ]
    md.extend(f"- `{b}`" for b in blockers)
    md.extend(["", "## Errors"])
    md.extend([f"- `{e}`" for e in errors] if errors else ["- none"])
    (OUT / f"{REVUP}_PUBLIC_TRACE_HARDWARE_TIMING_BOUNDARY_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({"status": audit["status"], "errors": errors, "blockers": blockers}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
