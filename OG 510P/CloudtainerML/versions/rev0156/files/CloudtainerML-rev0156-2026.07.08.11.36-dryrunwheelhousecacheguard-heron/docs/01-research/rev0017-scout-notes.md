# rev0019 scout notes — alignment tails, FlowTrace, Hasse masks, topic-graph memory

This revision continued the memory/cache hunt but shifted the acceptance criteria: average reconstruction and ordinary task utility are no longer enough for lossy cache probes. The strongest new paper pressure came from **Alignment Collapse Under KV Cache Quantization**, which claims low-bit KV quantization can preserve perplexity while damaging safety/refusal behavior through low-dimensional activation subspaces. That landed as a C++ safety-subspace quantization tail probe.

## New sources promoted

- **Alignment Collapse Under KV Cache Quantization** (`SRC-0127`, promoted to P0): tail/safety metrics are now mandatory for lossy-cache work.
- **FlowTracer** (`SRC-0234`): attention-induced DAG flow is a crisp toy for reasoning-token credit assignment.
- **Hasse Diagrams for Attention** (`SRC-0235`): mask choice can be scored as reachability/leakage/redundancy rather than just as a named architecture trick.
- **REAL** (`SRC-0236`) and **Infini Memory** (`SRC-0172`, promoted): persistent memory needs revision, validity, topic structure, confidence, provenance, and iterative evidence inspection.
- **False Success in LLM Agents** (`SRC-0237`): confident completion language is not a reliable state verifier.
- **T1-Bench** (`SRC-0238`): multi-domain agent evaluation is a useful future stressor, but not yet P0.
- **LiteReason** (`SRC-0239`): latent/discrete reasoning remains a P1 compute-budget lane.
- **Does Reasoning Preserve Alignment?** (`SRC-0240`): reasoning improvements can regress trustworthiness; this pairs naturally with safety-tail cache work.

## New implemented probes

```text
experiments/alignment_quant_subspace/alignment_subspace_probe.cpp
experiments/flowtrace_credit_assignment/flowtrace_credit_probe.cpp
experiments/hasse_mask_frontier/hasse_mask_probe.cpp
experiments/topic_graph_memory/topic_graph_memory_probe.cpp
```

## New audit/refactor layer

```text
tools/tail_risk_report.py
tools/probe_taxonomy_audit.py
```

These do not replace the probe dashboards. They expose two missing normal forms: “does this lossy probe have a catastrophic-tail contract?” and “what family does this probe actually belong to?”

## Working intuition after rev0019

1. Cache compression should be judged by **tail/exactness/safety** as well as reconstruction.
2. Reasoning credit assignment is a graph problem worth testing before tiny training.
3. Persistent memory is now split between **topic-document maintenance** and **temporal confidence graphs**, not just flat retrieval versus graph retrieval.
4. C++ is increasingly the right substrate for phase diagrams; Python is now mostly the cube/report layer.
