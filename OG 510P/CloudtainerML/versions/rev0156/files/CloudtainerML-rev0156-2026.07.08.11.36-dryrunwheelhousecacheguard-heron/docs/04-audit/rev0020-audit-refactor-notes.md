# rev0020 audit/refactor notes

- Added `tools/memory_safety_report.py` to aggregate current-revision memory/trust/provenance/safety probes.
- Extended the smoke validator to require the current memory-safety report.
- Kept C++ source-only; native audit still syntax-compiles probes and inspects current-revision JSON outputs.
- Added new P0 cells with direct tail/catastrophic metrics rather than surrogate-only contracts.
- Regenerated manifests/checksums after validation.
