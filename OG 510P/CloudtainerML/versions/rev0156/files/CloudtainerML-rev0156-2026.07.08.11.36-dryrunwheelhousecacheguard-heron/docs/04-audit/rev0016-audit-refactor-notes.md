# rev0019 audit/refactor notes

## Refactor actions

- Added `tools/native_hardening_report.py` to summarize current-revision native probes that harden existing lanes.
- Updated `tools/native_probe_audit.py` with explicit slugs for the new C++ probes.
- Updated `tools/smoke_validate.py` to require the new hardening report.
- Regenerated ledgers, root porch files, manifest, checksums, and revision metadata.
- Preserved source-only native policy: C++ probes compile into temporary directories during audit; no binaries are checked in.

## Why this matters

The native lane has enough probes that reentry now needs family reports, not just one compile receipt. The hardening report makes it easier to see which probes are testing claims already considered important, rather than expanding the idea cloud.
