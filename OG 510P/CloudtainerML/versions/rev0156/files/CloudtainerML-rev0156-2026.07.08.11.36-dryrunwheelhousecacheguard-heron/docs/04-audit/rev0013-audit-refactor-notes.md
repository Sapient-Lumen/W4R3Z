# rev0013 audit/refactor notes

## Native audit refactor

`tools/native_probe_audit.py` now compiles every `experiments/*/*.cpp` file in a temporary directory, runs each probe with a revisioned output path, and rejects checked-in binary candidates. The cube remains source-only while proving native code works.

## Datacube axis refactor

The baby datacube axes were updated to include:

- `memory_object`
- `transport_or_compute`
- `failure_mode`
- `implementation_tier`
- `budget`

This makes room for residual checkpoints, query routing, token quenching, adapters, fast-weight states, and plain KV caches without pretending they are one object.

## Traceability / ledgers

Added source IDs `SRC-0201` through `SRC-0210`, ideas `IDEA-0161` through `IDEA-0170`, questions `Q-0306` through `Q-0325`, and cells `CELL-162` through `CELL-171`.

## Known rough edges

- The C++ probes write JSON directly without a common helper library. This is intentionally dependency-free but repetitive.
- `gated_delta_memory` is a negative/rough first probe; its hand-built decoupled gates underperform tied scalar gates in the smoke setup.
- Several new systems-cost cells are not model-training probes, but they sharpen which memory objects are worth building.
