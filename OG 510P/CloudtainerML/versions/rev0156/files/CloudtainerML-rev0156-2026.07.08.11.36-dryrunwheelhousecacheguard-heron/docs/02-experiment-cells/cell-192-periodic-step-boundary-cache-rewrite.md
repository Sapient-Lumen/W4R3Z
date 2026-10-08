# CELL-192: Periodic Step-Boundary Cache Rewrite

Priority: P1

Status: candidate

Idea: IDEA-0191

Source: SRC-0227

Cheap first run: No runnable probe yet; multi-hop traces with explicit step delimiters and rewrite choices.

Metrics:
- reasoning success
- cache bytes
- rewrite cost
- state preservation

Baselines:
- continuous eviction
- periodic consolidation
- learned merge
- oracle step rewrite

Stop condition: If delimiters are not predictive of cache state changes, require event detector.
