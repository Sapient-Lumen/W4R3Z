# CELL-183: Hypergraph Memory Trace Probe

Priority: P0

Status: runnable

Idea: IDEA-0182

Source: SRC-0136

Cheap first run: C++ structured-document retrieval toy; output REV0015_HYPERGRAPH_MEMORY_TRACE_SMOKE.json.

Metrics:
- success rate
- evidence hit rate
- false hit rate
- cost

Baselines:
- flat lexical top-k
- flat semantic top-k
- hierarchy sections then local
- hypergraph trace
- experience reuse
- oracle evidence

Stop condition: If flat semantic top-k wins except obvious hierarchy regimes, demote.
