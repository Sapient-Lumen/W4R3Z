# Debugger visualizer compatibility — activation and origin plan (2026-03-22)

## Product goal

Deepen **P-0491 Debugger Visualizer Compatibility Kit** so that a bundle can answer not only “what asset exists?” but also:

1. how that visualizer was expected to become active in the debugger,
2. what artifact or support script is actually the effective formatter origin for a backend lane,
3. and what exact artifacts should be handed to another maintainer or support engineer as one portable review bundle.

## New first-class artifacts

- `activation-route.receipt.json`
  - backend family and target triple
  - route verdict (`embedded_autoloaded`, `embedded_present_safe_path_blocked`, `embedded_present_backend_unsupported`, `external_toolchain_script`, `external_debugger_config`, `manual_commands_required`, `unsupported_by_design`, `manual_review_required`)
  - referenced asset ids / script refs
  - activation evidence and warning text
  - concise human summary safe to paste into release notes or support replies

- `formatter-origin.receipt.json`
  - backend family
  - origin kind (`repo_embedded_asset`, `repo_external_asset`, `toolchain_support_script`, `debugger_builtin_formatter`, `user_local_config`, `manual_review_required`)
  - authority class (`primary_for_lane`, `supporting_only`, `derived_projection`, `manual_review_required`)
  - references to embedded assets, shipped scripts, or toolchain wrappers
  - notes on when the crate’s own asset is present but not the active formatter for that lane

- `visualizer-support-bundle.manifest.json`
  - compact manifest that points to policy, assets manifest, activation-route receipts, formatter-origin receipts, backend matrix receipts, render-golden reports, and drift reports
  - explicit redaction section and manual-review flags
  - share-safe summary for release-review or support handoff

## Suggested commands / UX

- `cargo visualizer-compat inspect-activation`
  - emits an activation-route receipt for configured lanes
- `cargo visualizer-compat inspect-origin`
  - emits a formatter-origin receipt for each backend lane
- `cargo visualizer-compat bundle`
  - assembles a portable visualizer-support bundle from the current receipts

## Theory-of-practice rules

Never say a backend is “supported” without also recording the activation route.

Never treat a toolchain-provided launcher script or debugger-local formatter config as the same kind of evidence as a crate-embedded visualizer asset.

Never let LLDB-family support be reported as if it were proven by an embedded Rust visualizer when the effective route is a separate formatter mechanism.

Never let GDB safe-path refusal degrade into a generic “asset failed” verdict.

## MVP order

1. stabilize `activation-route.receipt.json`,
2. stabilize `formatter-origin.receipt.json`,
3. stabilize `visualizer-support-bundle.manifest.json`,
4. teach the existing backend matrix to reference those artifacts,
5. add tiny scenario fixtures for GDB safe-path, toolchain-script origin, and portable bundles,
6. only then widen backend/version probing.
