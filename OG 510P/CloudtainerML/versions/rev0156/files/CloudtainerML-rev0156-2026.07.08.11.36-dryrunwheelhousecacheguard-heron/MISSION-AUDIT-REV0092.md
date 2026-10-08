# Mission audit — CloudtainerML rev0092 — mission/waste/pivot read

**Package:** `CloudtainerML-rev0092-2026.07.06.10.49-missionwastepivot-goldfinch`  
**Generated:** 2026-07-06T10:49:00-04:00  
**Status:** non-promotional deep read. No accepted public/pretrained checkpoint trace and no named-hardware sparse-vs-dense timing are claimed.

## Heart of the mission

CloudtainerML is a claim compiler and falsification wind tunnel for ML architecture ideas. The product is not a registry, a green test report, or a sparse-attention story. The product is a trustworthy decision chain:

```text
claim -> cheapest hostile falsifier -> semantic/exactness/cost/provenance vetoes -> measured implementation -> promote, stop, or pivot
```

The active scientific lane is narrower than the cube's ledgers: can a sparse/selected attention path preserve the actual model computation while avoiding enough score, metadata, retrieval, and value work to win end to end? The honest answer remains: not yet shown.

## What I verified locally

- The rev0091 validation path passes: token provenance, generated-token provenance, deterministic generation, capture readiness, smoke validation, and checksum verification all ran successfully in this capsule.
- Capture readiness is still blocked by environment rather than by the new v13 gate: `transformers_dependency_absent`, `no_cached_hf_model_snapshot_with_config_weights_tokenizer_detected`, and `cuda_gpu_not_available_for_named_hardware_timing_in_this_capsule`.
- rev0091's exact decode-count correction is directionally right. It prevents a dense-parity trace with fewer generated tokens than `decode_steps_requested` from masquerading as complete cached-decode evidence.

## What is missing

1. **The actual public model trace.** The cube still lacks an accepted immutable public/pretrained Llama-family prefill + cached-decode trace with post-transform Q/K/V, exact score semantics, mask-derived active key length, absolute positions, runtime RoPE position IDs, GQA/KV ownership, probability semantics, prompt and generated-token digests, greedy exact-length generation settings, and gate-recomputed dense parity.
2. **The actual systems result.** There is no named-hardware sparse-vs-dense timing with tokenization, cache ownership, selector/index/mask construction, metadata traffic, KV retrieval, value reads, quality, memory, and fallbacks included.
3. **A modern baseline harness.** Promotion should require comparison against strong implemented baselines such as eager/SDPA/FlashAttention-style dense attention, vLLM/PagedAttention-style KV management, and current sparse/KV-compression systems where applicable.
4. **A hard lane decision.** If real trace execution remains unavailable, the sparse-attention lane should stop or become explicitly blocked; it should not keep generating gate-only revisions.
5. **A smaller active frontier.** The cube has enough ideas and sources. It needs fewer active statuses, fewer live surfaces, and a short list of funded falsifiers.

## What has gone severely wrong or wasteful

### Corrected severe wrongness

Several earlier defects were genuinely severe because they could create false scientific evidence:

- pre-transform projection hooks could be treated as the score-path Q/K actually consumed by attention;
- score scale, bias/mask, and transform semantics were missing or self-attested;
- dense parity could be accepted as a flag rather than recomputed;
- mutable model/tokenizer/code revisions could pass as provenance;
- D-head costs could be substituted from a convenient global instead of the artifact;
- cached decode could be under-specified by missing generated tokens, generation strategy, or exact generated-token count.

Those fixes are mission-aligned. They defend the boundary between a trace-shaped object and the model/runtime computation it claims to represent.

### Remaining severe risk

The cube is now at risk of becoming a governance machine around absent evidence. rev0088 through rev0091 each closed a real replayability gap, but after exact prompt/generated-token/determinism/count gates, the next uncertainty is not another metadata field. It is whether the trace can actually be captured and whether a sparse implementation can beat dense systems under a real cost boundary.

### Waste that can be corrected over time

- **Registry entropy:** the current ledgers still show 643 open questions, 357 experiment cells, 53 idea-status strings, 47 experiment-status strings, and 324 source families. That is too many surfaces for a project whose product should be a short decision chain.
- **Lineage debt:** the inherited lineage audit still reports historical artifact-minting hazards. The fix-when-touched policy is acceptable only if normal workflows stop invoking old runners as if they were current evidence.
- **Duplicate/history weight:** this slim capsule has 57 exact duplicate groups with about 1,310,023 recoverable bytes, mostly repeated rev0076/rev0077 fixtures. This is not the dominant cost, but it is a symptom of copying evidence forward rather than object-addressing it.
- **Cognitive overhead:** the bigger waste is that every revision asks the reader to separate live evidence, frozen history, generated fixture, synthetic contract, public claim, and handoff prose. The package should make the current decisive experiment visible within one screen.

## Online research implications

The online check supports the cube's current skepticism:

- `max_new_tokens` is a maximum and `min_new_tokens` is the corresponding minimum-control lever, so rev0091's exact-length contract is not decorative; it closes a real API-semantics gap.
- Current Transformers attention backends make masks and backend selection consequential; a custom attention path can silently lose mask semantics if the matching mask interface is not registered.
- Modern efficient attention work is IO- and memory-system dominated. Sparse arithmetic savings alone are not enough; the decisive question is whether the runtime moves less data and wins wall-clock latency/throughput under real batching and cache management.
- Recent long-context systems research treats sparse attention as a pipeline + KV memory management problem. That suggests CloudtainerML should benchmark the full selection/retrieval/cache substrate, not just the selector math.

## What should change next

1. **Run the rev0091 capture script in a real trace environment or record the exact environment blocker.** Install/use `transformers`, choose a reviewed immutable public Llama-family snapshot, set model/tokenizer revisions to full content/commit hashes, and run `artifacts/capture-kit/REV0091_RUN_CACHE_PREFLIGHT_AND_CAPTURE.sh`.
2. **If capture passes, go straight to hardware.** Build a named-hardware dense-vs-sparse harness before adding another gate. Include tokenization, generation replay, active-key construction, index/mask construction, metadata, KV retrieval, value path, memory, quality, and tail latency.
3. **If capture cannot run, stop/pivot.** Write an explicit lane-stop memo or build only the smallest execution-enabling artifact: a dependency/provenance preflight that turns the current blockers into a runnable outside-capsule checklist.
4. **Thin the package slowly but deliberately.** Move toward content-addressed objects and revision manifests. Keep historical artifacts accessible, but stop copying full fixture families forward unless they are live inputs.
5. **Compress statuses only when touched.** Do not do a sweeping registry project now. When a cell or idea is touched, map it into a small taxonomy: `candidate`, `blocked_missing_evidence`, `falsified`, `measured_survivor`, `retired`, `archived_reference`.

## Speculation

The sparse-attention mechanism may or may not survive. The more durable invention here is the evidence discipline: a reusable architecture-claim compiler that refuses to confuse proxy FLOPs, green checks, or synthetic fixtures with runtime truth. If the session cannot obtain a public trace or GPU measurement, the best pivot may be to package CloudtainerML as a general claim-compiler scaffold and apply it to a lane with runnable public evidence, such as KV compression/eviction or quantized-cache quality/cost gates.

## Session decision

`promotion_allowed=false`. This revision is a read/research/pivot audit only. The next useful revision should be execution-facing: real public trace, named-hardware timing, or explicit stop/pivot.
