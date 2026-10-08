# rev0071 — stage-pruned certified reuse policy

rev0070 made certified support reuse safe but slow. It also exposed a dead stage: block refinement certified no extra rows on the local learned trace. rev0071 removes that block stage and measures a scalar-only certificate plus fresh fallback.

## Result

- Raw anchor quality rate: `0.71875`
- Raw anchor speedup vs dense: `1.17325396777`
- Fresh histogram speedup vs dense: `0.639799755495`
- Two-stage certificate speedup: `0.571259481971`
- Scalar-only certificate quality rate: `1`
- Scalar-only certificate speedup: `0.600481744929`
- Scalar-only certified rows: `70`
- Scalar-only fallback rows: `42`
- False scalar-certified quality failures: `0`
- Block-stage extra certified rows: `0`
- Scalar-only sidecar read fraction: `0.01025390625`
- Two-stage sidecar read fraction: `0.09228515625`
- Block-read reduction from pruning: `0.888888888889`

## Interpretation

Stage pruning is a real refactor win: it removes dead block-sidecar work while preserving the safety veto on invalid raw reuse. It is still non-promotional because the safe scalar-only path remains slower than dense and does not beat the simpler fresh histogram baseline on this local CPU trace.
