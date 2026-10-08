
## Current note (rev0486)
Each top-band contract0 now has a paired illustrative witness bundle under `specimens/kernel-contract-witnesses-v0/`.
Use the contract note when the question is “what surface must this implementation honor?” and the witness bundle when the question is “what should that surface look like when exercised honestly?”.

# Top-band kernel interface contracts (rev0485)

This folder keeps **contract0** notes for top-band kernels that have already earned a bounded v0 and a slice-0 milestone.
Each contract is deliberately narrower than the kernel brief and stricter than the slice note.

Current contract set:
- `build-state-pack.contract0.md`
- `debug-acceptance-matrix.contract0.md`
- `package-intake-review-kit.contract0.md`
- `safety-critical-readiness-cards.contract0.md`

Working rule:
- use contracts to fix command/file/schema posture,
- use slices to keep milestone scope bounded,
- and keep stable imports, experimental imports, and negative states visibly separate.
