# Pattern-control coverage matrix audit — rev0022

rev0016 introduced pattern red-team scaffolds. rev0017 and later revisions began adding controls. rev0022 makes the control status legible in one place via `CONTROL-COVERAGE-MATRIX.json`.

The audit finding is simple: most patterns still have case support but weak control coverage. The cube should not mature a pattern until it has at least:

- positive controls or fit cases;
- negative controls;
- counterexamples or boundary cases;
- rollback triggers;
- a second-pass source review for enough support records.

rev0022 improves `MKH-PAT-0017` by adding `MKH-CTL-0006`, but the pattern remains candidate-only. The matrix is a steering surface for future sessions, not a scoring game.
