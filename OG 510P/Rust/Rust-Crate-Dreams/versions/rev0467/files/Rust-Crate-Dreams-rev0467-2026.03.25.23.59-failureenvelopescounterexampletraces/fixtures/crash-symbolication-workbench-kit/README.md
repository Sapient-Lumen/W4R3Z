# Crash Artifact & Symbolication Workbench Kit fixtures

These fixtures exercise the `0.1` artifact vocabulary for **P-0101 Crash Artifact & Symbolication Workbench Kit**.

## Core schemas

- `capture-basis.receipt.schema.json`
- `module-identity.receipt.schema.json`
- `symbol-route.receipt.schema.json`
- `analysis-coverage.report.schema.json`
- `report-determinism.receipt.schema.json`
- `share-safety.receipt.schema.json`
- `crash-bundle.manifest.schema.json`

## Scenario families

- `external_monitor_capture_and_stack_sanitization_need_capture_receipt/` — monitor-process capture and stack-sanitization posture need an explicit capture receipt.
- `debug_id_and_code_id_fallback_must_be_explicit_for_windows_modules/` — Windows module lookup posture needs explicit identity/fallback truth.
- `offline_breakpad_bundle_is_not_same_as_live_symbol_server_route/` — offline bundles and live symbol-server routes need distinct symbol-route and determinism receipts.
- `native_debuginfo_and_breakpad_paths_need_coverage_report_not_one_green_state/` — mixed symbol routes need explicit coverage truth.
- `safe_share_bundle_redacts_memory_paths_and_symbols_but_keeps_triage_truth/` — safe-share posture must be explicit about what was stripped or retained.

The point of this fixture pack is to stop future passes from flattening:

- capture posture,
- module identity,
- symbol route,
- analysis coverage,
- replayability,
- and share-safety

into one fake “crash report available” story.
