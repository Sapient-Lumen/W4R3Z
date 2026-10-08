# rev0014 audit/refactor notes

- Deduped duplicate source rows for LRKV and Gated DeltaNet-2 by rewriting references to canonical source IDs.
- Rewrote `tools/native_probe_audit.py` so every C++ probe output must declare the current revision and `summary.primary_metric`.
- Added `tools/native_family_report.py` to group native outputs by probe, row count, primary metric, and winner summary.
- Updated smoke validation to require rev0014 native outputs and reports.
- Regenerated manifest and checksums after validation.
