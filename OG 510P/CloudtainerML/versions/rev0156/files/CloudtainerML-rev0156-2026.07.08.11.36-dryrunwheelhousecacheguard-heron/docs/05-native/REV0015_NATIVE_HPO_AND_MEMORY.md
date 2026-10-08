# rev0015 native C++ additions

New native probes:

- `native_hpo_phase.cpp`: optimizer-state phase-boundary harness.
- `hypergraph_trace_probe.cpp`: structure-aware on-demand hypergraph memory.
- `memory_sycophancy_probe.cpp`: persistent memory extraction/sycophancy trap.
- `dfssm_quant_probe.cpp`: 1-bit scaffold plus low-rank correction for recurrent transition kernels.

Rationale: C++ is now used wherever high-volume deterministic sweeps, phase diagrams, stochastic simulators, or memory kernels are sane. Python remains the orchestration and report layer.
