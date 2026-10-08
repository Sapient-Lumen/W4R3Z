# rev0019 audit/refactor notes

## Refactor work

- Added `tools/tail_risk_report.py` to scan current-revision probe artifacts for lossy/cache-like probes lacking catastrophic-tail, exactness, stale-error, or safety-flip fields.
- Added `tools/probe_taxonomy_audit.py` to classify current-revision probes into coarse families: cache compression, safety-tail, persistent memory, reasoning credit, attention architecture, latent compute, and meta-optimization.
- Extended `tools/native_probe_audit.py` to recognize four new C++ probe output slugs.
- Extended `tools/smoke_validate.py` to require the two new dashboard reports.
- Added taxonomy fields to the four new C++ probe outputs.

## Native status

Native audit now sees 21 C++ probe files and checks syntax plus current-revision smoke outputs. No checked-in binaries are accepted.

## Known debt

- Several older lossy-like probes are flagged by the tail report as missing explicit tail contracts.
- Some old probe artifacts still lack explicit taxonomy fields and are classified by filename/summary heuristics.
- Native HPO is not yet wired into the safety-subspace probe; this is a candidate rev0019 hardening target.
