# rev0006 worklog — peer-binding deep dive and coherence gate

Build timestamp: `2026.06.12.15.24` America/New_York.

## What changed

rev0006 deliberately moved from registry-building to one high-risk workup:

1. Touched the Batch 02 peer/request-binding group: U-123, U-158, U-165, U-168, U-171, U-176, U-181, U-217, plus U-169 as a carry-over because it is the same transfer-binding family.
2. Added a coherence/composability layer so individually plausible fixes are checked against each other before becoming recommendations.
3. Ran a minimal U-123 duplicate-token microprobe across all three source lanes.
4. Rewrote the strict document to remain empty but explain the near misses.
5. Updated the full ranked queue with rev0006-specific columns while preserving the original Pass 195/rev0005 history.

## Outcome

No finding is promoted to the strict document.

The best next real-work item is **U-123**, not because it is proven high impact, but because it is now the most compact and reproducible static-to-dynamic bridge: a local microprobe shows active-transfer overwrite across 3.3.10, 3.3.x, and master.

The most important refactor is **not** a document rule; it is a technical consolidation:

- U-168, U-176, U-165, U-171, and U-181 belong under **PB-01 peer connection identity/generation binding**.
- U-123, U-158, and U-169 belong under **TR-01 transfer lifecycle provenance**.
- U-217 belongs under **PR-01 allowed heavy-response/request-generation gating**, and its original phrasing is partially obsolete for master.

## Files added

- `data/rev0006_peer_binding_deepdive.csv/json/jsonl`
- `data/rev0006_coherence_map.csv/json`
- `data/rev0006_cluster_refactor.csv/json`
- `data/rev0006_public_overlap_delta.csv/jsonl`
- `data/rev0006_ranked_audit_queue.csv/json`
- `evidence/rev0006-source-trace-peer-binding.md`
- `evidence/rev0006-u123-microprobe.md`
- `evidence/rev0006-u123-duplicate-token-microprobe.jsonl`
- `evidence/rev0006-web-public-overlap-batch02.md`
- `docs/COHERENCE-AND-CHANGESET-STRATEGY.md`
- `docs/BATCH02-PEER-BINDING-DEEPDIVE.md`
- `tools/coherence_cluster_linter.py`
- `tools/replay_u123_duplicate_token_probe.py`
