# Mission audit — REV0126 prompt path gate fix

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What changed with substance

1. **Fixed a live-run blocker introduced by the prompt-manifest pivot.** `artifacts/capture-kit/REV0126_RUN_TINYLLAMA_PUBLIC_TRACE.sh` now defaults `PROMPT_MANIFEST` to `artifacts/prompts/${REVUP}_PUBLIC_TRACE_PROMPTS.txt`, matching the actual current manifest and the one-shot wrapper. In rev0125, the parent run wrapper still exported a missing `.jsonl` path, so a fully repaired runtime/snapshot could have failed after readiness when the one-shot wrapper inherited the bad environment variable.
2. **Expanded the live prompt-manifest audit from one-shot-only to full live-path coherence.** `tools/public_trace_live_prompt_manifest_audit.py` now checks the stable run alias, current run wrapper, current one-shot wrapper, run packet `prompt_count`, run packet `prompt_manifest_live_file`, and the actual prompt file together.
3. **Hardened smoke and live-script dependency audits.** `tools/smoke_validate.py` and `tools/current_live_script_dependency_audit.py` now fail if active current wrappers drift back to `PUBLIC_TRACE_PROMPTS.jsonl` or otherwise stop targeting the current `.txt` manifest.
4. **Kept focus on the riskiest incomplete lane.** No new doctrine/registry layer was added. This is a direct correction to a command path that could have wasted the next real runner after snapshot/runtime blockers were repaired.

## Online research incorporated

- Hugging Face Transformers offline mode still requires model files to be downloaded/cached before offline loading, so the snapshot/materialization step remains separate from final local-only capture.
- Hugging Face Hub dry-run and filtered download support keeps snapshot planning/materialization separable from capture runtime.
- Transformers attention backends now include eager, SDPA, FlashAttention variants, FlexAttention, and paged variants; backend/mask identity remains material for trace extraction, so the live capture must keep `ATTENTION_IMPLEMENTATION=eager` and explicit prompt/token provenance.
- Safetensors metadata parsing is useful for structure/shape checks, but byte authenticity still requires hashing the local `model.safetensors` payload against the expected digest.

## What is still blocked here

- No complete digest-authenticated TinyLlama snapshot is present in this cloudtainer.
- `transformers` is absent here, so real capture cannot run.
- No real public trace NPZ/provenance packet exists.
- No selector/evaluation/handoff receipts exist over a real trace.
- No named-hardware sparse-vs-dense/page-KV timing exists.

## Why this is not bureaucracy

The parent wrapper prompt default was a practical failure point, not documentation debt. It would let earlier gates pass and then fail the actual capture due to an inherited missing prompt-manifest path. The fix and audits are small, executable, and directly on the next evidence path.

## Next decisive move

Run:

```bash
HASH_WEIGHTS=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh
bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

If snapshot/runtime remain unavailable after this live-path fix, stop expanding gates and pivot to the claim-compiler handoff product: accept externally produced trace packets, verify digest/provenance/selector receipts, and defer sparse-performance promotion until named-hardware timing exists.
