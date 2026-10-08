# rev0739 unemployment-insurance access and integrity refactor note

This revision repairs the next critical gap identified in `metadata/gap_ledger.json`: pandemic unemployment-insurance fraud / claimant-access governance. It adds a substantive UI policy docket and applied case packet, plus a UI-specific test matrix, while refactoring the lint path so new test matrices use the common validator rather than copy-pasted blocks.

Changed surfaces:

- `archive/913-*` adds the UI integrity / access policy docket.
- `archive/914-*` adds the pandemic UI / PUA applied case packet.
- `metadata/unemployment_insurance_tests.json`, `schema/unemployment_insurance_tests.schema.json`, `tools/build_unemployment_insurance_tests.py`, and `generated/UNEMPLOYMENT_INSURANCE_TESTS.*` add testable review criteria.
- `metadata/gap_ledger.json` marks `GAP-002` repaired and moves the next substantive target to watchlist / border / law-enforcement automation.
- `metadata/source_health.json` upgrades UI source keys from queued to checked or implementation-clock status.
- `tools/lint_archive.py` now validates credential, representative, disaster, and unemployment-insurance test matrices through the same generic function, reducing maintenance debt while preserving strict generated-output checks.

The archive should still resist adding more registries before it adds the next high-risk applied case. The useful pattern is now: one substantive case, one bounded test matrix, one source-health update, and one small refactor per revision.
