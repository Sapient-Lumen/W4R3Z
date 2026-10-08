# Mission audit — REV0124 capture decision / local-only evidence refactor

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What changed with substance

1. **Evidence capture is now local-only.** The live `REV0124_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh` wrapper no longer passes `--allow-download` to `hf_attention_trace_capture.py`. Network access remains available to the snapshot-preparation/readiness materializer when `ALLOW_DOWNLOAD=1` is intentionally set, but the evidence capture itself must load from an already materialized local/cache snapshot.
2. **Public promotion has one final decision point.** `experiments/public_trace_capture/hf_attention_trace_capture.py` no longer computes `effective_public` before token provenance and generation determinism are known. The final promotion boolean is assigned once, after score-path fidelity, token provenance, generation-token provenance, generation determinism, runtime provenance, and digest-authenticated model provenance have all been computed.
3. **The refactor is executable-audited.** `tools/public_trace_capture_decision_refactor_audit.py` parses the capture helper and fails if `effective_public`, `effective_source_type`, `phase_contract_verified`, `score_path_fidelity_verified`, `fidelity_verified`, or `provenance_complete` drift back into multi-assignment or premature-decision form.
4. **The online baseline pressure was recorded.** `artifacts/research/REV0124_EXTERNAL_BASELINE_PRESSURE_RESEARCH.*` records why future sparse claims must beat current SDPA/FlexAttention/FlashAttention/vLLM/xFormers/cache-strategy baselines under named hardware rather than rely on toy dense loops.

## Why this was the risky part

The older capture helper was not currently promoting false evidence, but it had a dangerous maintenance seam: promotion-ish booleans were computed, overwritten, and then computed again after later gates. That is exactly the kind of future-edit trap that can create accidental overclaim. Rev0124 makes the public decision flow boring and single-point.

The other risk was run drift. If capture itself can download, then evidence depends on network/cache behavior at the moment of capture. The archive already has a preparation phase; rev0124 uses it. Public capture should be the consumer of a reviewed, digest-authenticated snapshot, not the downloader of one.

## Still blocked here

- No complete TinyLlama snapshot is present in this cloudtainer.
- `transformers` is not importable here.
- No real public TinyLlama trace was captured.
- No selector/evaluation/handoff receipts from a real trace exist.
- No named-hardware timing exists.

## Best next action

Run snapshot preparation first, then capture:

```bash
HASH_WEIGHTS=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh
bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

If the runtime/snapshot blockers remain unresolved after that, stop adding gates and write the pivot memo for the reusable claim-compiler product.
