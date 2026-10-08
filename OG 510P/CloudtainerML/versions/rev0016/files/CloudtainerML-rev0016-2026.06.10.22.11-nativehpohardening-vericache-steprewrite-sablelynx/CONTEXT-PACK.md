# CloudtainerML context pack — rev0016

Project stance: discover and test small-scale transformer/memory/cache ideas in this CPU cloudtainer. Use C++ for stable high-volume probes and Python for orchestration, dashboards, and training when needed.

## What changed now

- Added `vericache_guard_probe.cpp` for exactness/verification around lossy KV.
- Added `step_rewrite_probe.cpp` for reasoning-step cache rewrite clocks.
- Added `memory_provenance_phase.cpp` for persistent-memory safety phase diagrams.
- Added `native_hardening_report.py` to summarize hardening artifacts.

## Current pressure

The cube should stop rewarding methods that only reduce average error. Long decode, tool calls, and remembered misconceptions make tail failures first-class.
