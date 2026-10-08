# Online research notes — REV0153

Status: `non_promotional_context_only`  
Created: `2026-07-08T09:58:00-04:00`

## Sources checked

- Hugging Face Hub environment variables documentation: `HF_HOME`, `HF_HUB_CACHE`, `HF_XET_CACHE`, offline mode, and timeout variables remain the relevant controls for cache-root binding and local-only evidence capture.
- Hugging Face Hub download guide: `snapshot_download`/cache behavior supports the prepare-then-capture split and revision-bound model materialization.
- Transformers installation/offline documentation: offline operation depends on files being present locally and on local-only loading behavior, reinforcing that capture should not download.
- TinyLlama model card/tree: the target remains the public `TinyLlama/TinyLlama-1.1B-Chat-v1.0` Llama-family checkpoint; the package still makes no model-performance claim.
- ACM artifact review/badging guidance and recent artifact-evaluation papers: runnable scripts, complete inventories, and reproducible receipts are higher-value than more internal doctrine.

## Effect on this revision

The changes stay operational: make failure handoff explicit, keep cache/offline variables bound before runtime imports, keep snapshot preparation separate from local-only capture, and trim historical capture-kit wrappers out of the active package.

## Speculative risk

The large remaining risk is not that the runner lacks enough narrative. It is that a capable host reaches a slow network or environment failure and the session loses the first actionable blocker. REV0153 therefore prioritizes the first-blocker status receipt and external-runner live closure over adding any new conceptual lane.
