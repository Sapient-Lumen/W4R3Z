# REV0118 runtime/offline fail-fast research

Status: `research_complete_non_promotional`  
Promotion allowed: `false`

## Why this matters

The riskiest unfinished path is not another registry: it is a real public TinyLlama trace with receipts. Rev0118 online research supports a simple engineering rule: if the capsule lacks the runtime dependency, a complete local snapshot, or a CUDA timing device, the live lane should stop early and write a blocker receipt rather than continue into expensive probes.

## External references checked

- Hugging Face Transformers offline installation docs: offline/fenced execution requires downloaded and cached files ahead of time, with snapshot/local-only workflow (`https://huggingface.co/docs/transformers/en/installation`).
- Transformers v4.47.1 offline mode docs: `HF_HUB_OFFLINE=1` is the documented offline environment control for Transformers workflows (`https://huggingface.co/docs/transformers/v4.47.1/installation`).
- Hugging Face Hub environment variables: hub behavior is controlled through environment variables such as `HF_HUB_OFFLINE` (`https://huggingface.co/docs/huggingface_hub/en/package_reference/environment_variables`).
- Safetensors docs: safetensors is a simple, safe, fast tensor serialization format and is preferable for model-weight provenance/security expectations (`https://huggingface.co/docs/safetensors/en/index`).
- PyTorch CUDA Event docs and NVIDIA CUDA runtime docs: CUDA events are the relevant device timing primitive; named-hardware timing remains unavailable in a no-CUDA capsule (`https://docs.pytorch.org/docs/stable/generated/torch.cuda.Event.html`, `https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__EVENT.html`).

## Design consequence implemented

`tools/public_trace_readiness_gate.py` now classifies prerequisite blockers and returns `blocked_here_fail_fast` unless the operator explicitly chooses debug continuation with `--continue-after-prereq-blockers`. Stable `RUN_CURRENT_PUBLIC_TRACE.sh` now uses the strict gate; one-shot capture and snapshot prepare use strict environment preflight.

## Remaining blocker

The next meaningful step is not more doctrine. It is to install/verify the runtime, provide or materialize a reviewed immutable TinyLlama snapshot, and run the current trace lane on named CUDA hardware.
