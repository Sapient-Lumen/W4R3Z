# rev0013 native frontier

C++ is now the preferred implementation tier for:

- deterministic cost models,
- large synthetic cache sweeps,
- quantization/byte-budget loops,
- streaming coresets and adversarial retention tests,
- tree-search and rollout allocation simulators,
- fast-weight memory updates.

Python remains preferred for:

- training tiny neural models,
- data generation with NumPy/PyTorch,
- plotting and dashboards,
- ledger/audit/report orchestration.

## Source-only rule

Do not check compiled binaries into the cube. `tools/native_probe_audit.py` compiles into a temp directory and records outputs under `artifacts/probe-results/`.

## Rev0013 native probes

| Probe | Source | Output |
|---|---|---|
| Express coreset | `experiments/express_streaming_coreset/express_coreset.cpp` | `REV0013_EXPRESS_STREAMING_CORESET_SMOKE.json` |
| Token precision frontier | `experiments/native_token_precision_frontier/token_precision_frontier.cpp` | `REV0013_NATIVE_TOKEN_PRECISION_FRONTIER_SMOKE.json` |
| Residual stream KV object | `experiments/residual_stream_kv/residual_stream_kv.cpp` | `REV0013_RESIDUAL_STREAM_KV_SMOKE.json` |
| Query move/cache cost | `experiments/query_move_cache/query_move_probe.cpp` | `REV0013_QUERY_MOVE_CACHE_SMOKE.json` |
| Gated delta memory | `experiments/gated_delta_memory/gated_delta_memory_probe.cpp` | `REV0013_GATED_DELTA_MEMORY_SMOKE.json` |
