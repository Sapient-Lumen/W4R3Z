# Bin path from test inference

This scenario exists because Cargo's March 2026 build-dir-v2 call for testing names this failure mode explicitly.
The crate should prefer `CARGO_BIN_EXE_*` where possible instead of preserving test-path inference as a pretend contract.
