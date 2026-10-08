# CELL-173: Query Move Phase Boundary Scan

Priority: P0

Status: runnable

Idea: IDEA-0172

Source: SRC-0202

Cheap first run: experiments/query_move_phase_boundary/query_move_phase_scan.cpp emits REV0014_QUERY_MOVE_PHASE_SCAN_SMOKE.json.

Metrics:
- latency proxy
- winner counts
- phase boundary

Baselines:
- move query
- move cache
- index-then-fetch
- recompute local

Stop condition: If one policy always wins, constants are too narrow.
