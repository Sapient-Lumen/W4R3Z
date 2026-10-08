# Crash Artifact & Symbolication Workbench Kit — product plan (2026-03-21)

This note sharpens **P-0101 Crash Artifact & Symbolication Workbench Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0101** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not become a hosted crash service, a new stackwalker, or a universal debugger frontend.
It should provide one boring, reviewable **crash support contract** above today's capture, symbolication, and report-generation substrate.

`0.1` should make six things first-class:

1. **capture basis** — whether the artifact came from in-process capture, an external monitor, an imported OS artifact, a synthetic test, or manual review;
2. **module identity** — the module table, identifier posture, and confidence basis used for lookup;
3. **symbol route** — which local, bundled, native, and server-backed symbol routes were allowed and in what order;
4. **analysis coverage** — how much of the report is well-supported, unresolved, missing, corrupt, or soft-error-tainted;
5. **report determinism** — whether another team can reproduce the report from bundled artifacts alone;
6. **share-safety** — what sensitive material is included, stripped, redacted, or still requires manual review.

## What `0.1` should provide other people

- one compact `capture-basis.receipt.json`
- one compact `module-identity.receipt.json`
- one compact `symbol-route.receipt.json`
- one compact `analysis-coverage.report.json`
- one compact `report-determinism.receipt.json`
- one compact `share-safety.receipt.json`
- one compact `crash-bundle.manifest.json`
- one compact `crash.summary.md`
- one compact `crash-diff.report.json`
- one portable review/support bundle

## Commands worth shipping first

- `cargo crashworkbench capture`
- `cargo crashworkbench inspect`
- `cargo crashworkbench doctor`
- `cargo crashworkbench diff`
- `cargo crashworkbench bundle`

## What to import, not reinvent

- capture facts from `minidumper` / `minidump-writer` when present
- stackwalk facts from `rust-minidump` / `minidump-stackwalk`
- native-debug-info route facts from `wholesym`
- broad debug-info format support from `symbolic`
- Breakpad symbol lookup conventions and symbol stats instead of inventing new symbol identity stories
- manual JSON/TOML descriptors when the exact capture/symbolication backend is outside the current adapter set

## Suggested `0.1` doctor warnings

- `capture_mode_unknown_or_mixed`
- `module_identity_missing_debug_and_code_id`
- `symbol_route_depends_on_live_network`
- `symbol_route_uses_unfrozen_system_debuginfo`
- `analysis_has_unresolved_or_corrupt_symbol_gaps`
- `report_not_replayable_from_bundle`
- `bundle_contains_raw_memory_or_paths_without_safe_share_receipt`
- `module_identity_conflicts_with_symbol_match_basis`

## First proving-ground scenarios

1. **An external monitor capture with stack sanitization needs an explicit capture-basis receipt, not just “we wrote a minidump.”**
2. **A Windows crash with missing debug IDs but present code IDs needs an explicit module-identity fallback story.**
3. **A local bundle using Breakpad symbols is not the same replay story as a live symbol-server route.**
4. **Mixed native-debuginfo and Breakpad lookup needs a coverage report, not one fake green stack trace.**
5. **A safe-share bundle needs explicit stripping/redaction receipts for memory, paths, and symbol payloads.**

## What to leave for later

- hosted dashboards and upload services
- GUI viewers
- fully automatic privacy classification
- universal crash capture for every OS/runtime combination
- deep deduplication / clustering systems
