# rev0038 audit/refactor notes

Added `tools/hard_gate_compilation_report.py` to scan current sparse/gate/bridge/routing artifacts for:

- hard top-k / hard threshold deployment fields
- deployment gap fields
- exactness / reachability fields
- selected-edge or cost fields
- primary metric readiness

This is now separate from trained-mechanism readiness because a trained toy can be accurate while still failing to compile into a deployable hard sparse program.

The smoke validator was updated to require the hard-gate compilation report for the current revision.
