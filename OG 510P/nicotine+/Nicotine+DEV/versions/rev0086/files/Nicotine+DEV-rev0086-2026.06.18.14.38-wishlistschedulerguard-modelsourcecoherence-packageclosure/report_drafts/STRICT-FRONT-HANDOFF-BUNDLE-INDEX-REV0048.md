# Strict/front handoff bundle index — rev0048

This is the maintainer-facing entry point for the rev0048 handoff export. The minimized packet folders live under `handoff/rev0048/`.

## Recommended review order

1. `handoff/rev0048/01-transfer-session-identity` — U-123
2. `handoff/rev0048/02-peer-primary-election` — PB-01
3. `handoff/rev0048/03-search-response-source-admission` — SEARCH-RESP-01A, SEARCH-RESP-01B-BUDDY, SEARCH-RESP-01C-ROOM
4. `handoff/rev0048/04-search-response-parser-budget` — SEARCH-RESP-PARSE-BUDGET-A, SEARCH-RESP-PARSE-BUDGET-B

## Verification

- Use `tools/probe_rev0048_handoff_export.py` for file/hash structure.
- Use `tools/probe_rev0046_strict_bundle_integration.py` with the external source bundle for the full seven-packet regression stack.
- Use `tools/probe_rev0047_filing_preflight.py` for report/source-anchor preflight.

No source tree is embedded in the rev0048 ZIP.
