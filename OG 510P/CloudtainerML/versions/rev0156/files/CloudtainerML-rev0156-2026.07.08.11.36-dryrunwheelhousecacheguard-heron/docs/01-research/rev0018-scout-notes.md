# rev0019 scout notes — tail phase, provenance recovery, JANUS distortion, bank gates

This revision kept the C++/native trajectory. The new material is less about adding another cache trick and more about hardening acceptance tests: hidden safety tails, truthful-but-misleading fact selection, provenance-grounded gates, and sparse routing diversity.

## Sources promoted

- `SRC-0241` Provenance-grounded gating and adaptive recovery: reward gates, hallucination/source gates, and recovery are separable objects.
- `SRC-0242` JANUS: misleading outputs can use only true facts, so hallucination checks are not enough.
- `SRC-0243` Predictor-gated bank-wise sparsity: routing diversity across FFN banks is a compute analogue of cache diversity.
- `SRC-0244` Prefilling-dLLM: sparse chunk prefill and periodic chunk anchors are testable as chunk-cache routing.
- `SRC-0245` ConvMemory v2: protected recall first, rerank second.
- `SRC-0246` LC-QAT: a future tiny matrix/codebook test for 2-bit quantization-aware training.
- `SRC-0247` curriculum prerequisite graph gap detection: P2 graph diagnostic lane.
- `SRC-0248` trustworthy memory search: persistent memory must be searched with trust/provenance constraints.

## New implemented probes

```text
experiments/safety_tail_phase/safety_tail_phase.cpp
experiments/janus_goal_distortion/janus_distortion_probe.cpp
experiments/provenance_recovery_gate/provenance_recovery_probe.cpp
experiments/bankwise_sparse_gating/bankwise_sparse_probe.cpp
experiments/prefill_chunk_anchors/prefill_chunk_anchor_probe.cpp
```

## Audit/refactor

```text
tools/tail_contract_patcher.py
```

The patcher adds an explicit `summary.tail_contract` to current-revision probe artifacts. It does **not** create science; it marks whether an artifact has direct tail fields or only a surrogate schema contract.

## Working intuition after rev0019

1. Tail acceptance is now a cube invariant for lossy/cache/memory-selection probes.
2. Provenance/correction is no longer just a persistent-memory concern; it also belongs in synthetic data, summary, and curation gates.
3. Goal-conditioned distortion is a good red-team normal form because it decouples misleadingness from hallucination.
4. Sparse channel routing and sparse cache routing may share the same failure: rare group starvation.
5. Chunk anchors are worth testing as retrieval handles, but must be defended against becoming attention-sink leaks.
