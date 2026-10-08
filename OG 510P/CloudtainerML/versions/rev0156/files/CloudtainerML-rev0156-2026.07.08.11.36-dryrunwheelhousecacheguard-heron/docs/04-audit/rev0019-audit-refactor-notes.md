# rev0019 audit/refactor notes

## Refactor work

- Added `tools/p0_integrity_report.py` to check P0 source/idea/cell/note connectivity and implementation outputs.
- Reran all native C++ probes with current-revision output names.
- Added direct current-revision smoke outputs for four new C++ probes.
- Kept retired side-lanes deleted; smoke validation still scans for forbidden retired-lane tokens.
- Preserved source-only native posture: no checked-in binaries.

## Audit intent

The cube is now large enough that priority drift is a real failure mode. The P0 integrity report checks whether every P0 idea has source bindings and whether implemented P0 cells have cell notes and current probe outputs where expected.

## Known weakness

Many probes still use synthetic utilities and hand-set constants. The next refactor should make HPO/phase-boundary runs less prior-friendly and more adversarial.
