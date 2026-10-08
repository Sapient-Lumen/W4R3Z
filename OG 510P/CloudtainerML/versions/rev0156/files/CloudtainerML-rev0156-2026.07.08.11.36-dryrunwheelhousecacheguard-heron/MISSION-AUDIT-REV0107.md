# Mission audit — REV0107

Status: `pass_with_blockers`  
Promotion allowed: `false`  
Public/pretrained trace loaded: `false`  
GPU fused-kernel timing measured: `false`

## What changed

REV0107 closes a concrete endgame evidence hole: a human-readable evaluation verdict was not enough to prove what the evaluator actually checked. The revision adds a receipt contract that binds selector-entry permission to the exact public trace NPZ, provenance JSON, verifier code, and evaluator code hashes.

## Why this is riskiest now

The cube has already pinned prompt/token digests, generation length, greedy decode, dynamic cache, eager backend, local snapshot identity split, dtype/device/timing provenance, acceptance-bundle completeness, and a verdict layer. The remaining failure mode is handoff drift: a later operator could run selector/cost evaluation against a different trace, a stale provenance file, or a changed verifier while citing an old verdict. REV0107 makes that impossible to miss.

## Concrete changes

- `tools/public_trace_evaluation_verdict_audit.py` now emits `artifacts/probe-results/REV0107_PUBLIC_TRACE_EVALUATION_RECEIPT.json`.
- `tools/public_trace_selector_entry_gate.py` blocks selector/cost evaluation until the receipt says the verifier accepted the exact NPZ/provenance pair.
- `tools/public_trace_evaluation_receipt_audit.py` tests forged/missing receipt cases and confirms selector entry remains closed without an accepted verifier receipt.
- Current capture wrappers now pass the receipt path through the post-capture verdict and selector-entry gate.
- `RUN_CURRENT_PUBLIC_TRACE.sh` points to the current revision launcher.

## Refactor/audit result

This revision updates the active path rather than adding another doctrine surface. It also keeps stale/historical artifacts intact while narrowing current operator guidance to: readiness gate → one-shot capture → receipt-bound selector entry → named-hardware timing.

## Remaining blockers

- Real public TinyLlama NPZ/provenance pair is still absent in this cloudtainer.
- Selector/cost evaluation is blocked until the receipt says the verifier accepted the exact bundle.
- Promotion remains blocked after selector entry until named-hardware sparse-vs-dense timing exists.
