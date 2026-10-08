# Mission audit — CloudtainerML rev0084 — active-key mask gate

**Package:** `CloudtainerML-rev0084-2026.07.06.04.37-activekeymaskgate-swifttern`  
**Generated:** 2026-07-06T04:37:00-04:00  
**Status:** non-promotional. No accepted public/pretrained trace and no named-hardware GPU/fused timing are claimed.

## Heart of the mission

CloudtainerML is a claim compiler and falsification wind tunnel. The useful output is not another registry entry; it is a hard decision about whether a model-architecture claim survives exact attention semantics, hostile controls, provenance checks, and real cost accounting.

## What changed in rev0084

rev0084 attacks the riskiest remaining trace-fidelity false positive after rev0083. Cached-decode traces can now distinguish physical exported K/V width from the active scored key prefix. This matters for static or sliding cache implementations: dense Q/K/V replay can be mathematically correct while masked cache slots are incorrectly counted as live attention work.

Concrete execution changes:

- advanced the public trace claim to `public_trace_claim_v6`;
- added `active_key_len_contract="mask_derived_active_prefix_v1"`;
- exported per-row `active_key_len` from the serialized additive score bias;
- changed absolute decode-position verification to use active scored key length, not physical cache width;
- refactored the gate to recompute active-key semantics from arrays instead of trusting attestation fields;
- added `tools/public_trace_active_keymask_audit.py`, which accepts a mixed prefill plus static-tail decode fixture and rejects a same-math bundle forged to physical K/V width.

## Why this is the riskiest useful move

The cube already blocks raw projection traces, missing mask semantics, prefill-only traces, and local q_len decode positions. The next way to get a false green light was subtler: a trace could include correct score bias and dense reference parity, yet still overcount active keys by treating masked static/sliding-cache storage as live attention. That would poison selector cost accounting and downstream sparse-vs-dense claims.

The new active-key-mask audit is deliberately narrow. It does not add registry doctrine. It creates a temporary good bundle and a temporary forged bundle with the same Q/K/V, scale, bias, and dense reference math. The forged bundle relabels `active_key_len` as the physical cache width. The public gate rejects it.

## What remains missing

The decisive evidence is still absent:

- no immutable public/pretrained Llama-family checkpoint has been captured in this capsule;
- no accepted public trace gate result exists;
- no named-hardware end-to-end sparse-vs-dense timing exists;
- no GPU/fused-kernel performance claim is supported;
- no selector/index/mask construction cost has been included in a deployment-grade result.

## What should happen next

Run the revised capture path only if a reviewed immutable public Llama-family snapshot and `transformers` are available. The command must request cached decode (`--decode-steps 2` or higher), pass mask fidelity, active_key_len, absolute position, provenance, and dense reference checks. If the public gate accepts, move directly to named-hardware measurement. If it cannot be run, stop or make one execution-enabling improvement; do not expand registries.

## Claim boundary

This revision hardens the trace acceptance contract. It is not public-model evidence and it is not a performance result.
