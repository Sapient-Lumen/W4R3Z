# Mission audit — REV0123 digest acceptance / capture refactor

Status: `pass_with_blockers`  
Promotion allowed: `false`  
Package: `CloudtainerML-rev0123-2026.07.07.15.34-digestacceptancerefactor-heron`  
Generated: `2026-07-07T15:34:00-04:00`

## This turn's priority call

The riskiest unfinished part is still the public-trace evidence lane: a real TinyLlama snapshot, real trace, selector/evaluation receipts, and named-hardware timing. Since this cloudtainer cannot supply the 2.2GB model snapshot or install/verify the missing capture runtime, the most substantive local move was to close a promotion hole rather than add doctrine.

## What changed substantively

1. **Digest proof is now part of public trace acceptance.** `experiments/public_trace_capture/hf_attention_trace_capture.py` now has a `--require-model-safetensors-sha256` option. When a public pretrained trace is requested with that flag, the capture refuses to proceed unless a local/cache snapshot candidate has a `model.safetensors` SHA-256 matching the pinned TinyLlama digest.
2. **The live public trace wrapper now requests that proof.** `REV0123_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh` passes `--require-model-safetensors-sha256`, so the stable `RUN_CURRENT_PUBLIC_TRACE.sh` path cannot accidentally promote from only revision strings plus structural checks.
3. **Trace/provenance packets now carry the digest fields.** The NPZ/provenance surfaces include the digest contract, expected SHA-256, observed SHA-256, match boolean, and snapshot proof summary.
4. **A focused audit guards the refactor.** `tools/public_trace_digest_acceptance_audit.py` checks the capture script, wrapper, and smoke surface for digest acceptance markers.
5. **The baseline-pressure note is narrowed to execution risk.** The online research note records that safetensors header validation is not byte authenticity and that timing claims must separately compete against SDPA/FlashAttention/PagedAttention-class pressure.

## Why this is real forward momentum

Rev0122 made hash verification available in snapshot preparation. Rev0123 pushes that from an operator option into the public capture acceptance boundary. That means a future real trace cannot become public-claim-ready unless the loaded local/cache model bytes match the expected TinyLlama weight file. This is a small code change, but it removes a severe wrong-result risk: a false public trace from a plausible but wrong local snapshot.

## What remains blocked here

- No complete TinyLlama snapshot is present in this cloudtainer.
- `transformers` is not importable here, so real capture still stops at the fast prerequisite gate.
- No named GPU/hardware timing receipt exists.
- No real selector/evaluation/handoff receipts over a real trace exist.

## Audit/refactor note

This was intentionally not a broad registry expansion. The refactor is localized to the live capture path and its smoke/audit guard. The next session should not add more static statuses unless it directly helps one of these: materialize snapshot, verify digest, install/lock capture runtime, run real trace, run selector/evaluation, run named-hardware baselines, or write the stop/pivot memo.

## Next action

Mount or materialize the exact TinyLlama snapshot, then run:

```bash
HASH_WEIGHTS=1 bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh
```

If it passes, run:

```bash
bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

If it cannot pass in the available environment, stop expanding gates and formalize the pivot toward the reusable claim-compiler product.
