## Current note (rev0488)
Each top-band contract0 now also has a paired **artifact schema pack** under `schemas/top-band-v0/` and validated specimen payloads under `specimens/kernel-contract-witnesses-v0/`.
Use the contract note when the question is “what surface must this implementation honor?”, the witness bundle when the question is “what should that surface look like when exercised?”, and the schema pack when the question is “what minimum machine-readable JSON family should still validate after implementation drift?”


## Current note (rev0486)
The repo now also has a first **kernel contract witness corpus** under `specimens/kernel-contract-witnesses-v0/`.
That means contract notes no longer float free of examples: the archive can now show a concrete exercised output family for each already-earned top-band contract0.

# Kernel interface contracts (rev0485)

This corpus holds the archive's **first explicit command/file/schema contracts** for top-band kernels.
These are narrower than kernel briefs and more machine-facing than slice notes.
They answer “what surface must a first implementation honor?” rather than only “what should the repo contain?” or “what lands first?”

Current contract corpus:
- `build-state-pack.contract0.md`
- `debug-acceptance-matrix.contract0.md`
- `package-intake-review-kit.contract0.md`
- `safety-critical-readiness-cards.contract0.md`

Intentionally absent for now:
- **Navigation / Defaults / Claims Commons** — still `hold`; the blocker is renewal burden and stewardship cadence, not missing command/schema imagination.

Default use:
- start here when a kernel and slice already exist and the next question is “what exact surface should an implementation expose?”;
- return to the slice note when the question is about milestone scope;
- return to the kernel brief when the question is about repo shape;
- return to the live packet when verdict posture changes.
