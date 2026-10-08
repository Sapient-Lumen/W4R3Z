# Debugger Visualizer Compatibility Kit fixtures

This fixture family is for **P-0491 Debugger Visualizer Compatibility Kit**.
Its goal is not to automate every debugger workflow.
Its goal is to make the first **visualizer compatibility receipt** reviewable.
It should keep three things separate: the asset bytes, the activation/trust conditions, and the backend lane itself.

## Core bundle shape

- `visualizer-policy.toml` — intended backend lanes, target triples, and safe-path/external-formatter expectations
- `visualizer-assets.manifest.json` — discovered embedded/external assets plus provenance
- `backend-matrix.receipt.json` — attempted backend probes, activation evidence, and conservative verdicts
- `activation-route.receipt.json` — how a visualizer was expected to become active for each backend lane
- `formatter-origin.receipt.json` — which asset, wrapper, or debugger-local configuration is actually the effective formatter origin
- `render-golden.report.json` — tiny normalized value-render expectations
- `embed-vs-external.report.json` — what is embedded, what is external, what is manual-only
- `probe-surface.receipt.json` — which debugger surface, version, OS class, and delivery route were actually observed
- `comparison-basis.receipt.json` — whether two visualizer observations are honestly comparable
- `visualizer-support-bundle.manifest.json` — shareable portable bundle that keeps artifacts separate
- `visualizer-drift.diff.json` — compatibility drift between releases or toolchain matrices
- `notes.md` — compact scenario explanation

## Scenario families

- `natvis_msvc_supported/` — embedded NatVis asset on MSVC with expected support
- `gdb_safe_path_blocked/` — embedded GDB asset present but blocked by missing trust/auto-load safe-path configuration
- `gdb_safe_path_blocked_records_activation_route_instead_of_asset_failure/` — support bundle records safe-path refusal as activation-route truth
- `external_backend_route/` — embedded assets exist for documented lanes while another backend is intentionally routed through an external/manual lane
- `rust_lldb_wrapper_is_formatter_origin_not_repo_embedded_visualizer/` — LLDB lane is attributed to a toolchain formatter route rather than crate-embedded assets
- `portable_bundle_keeps_assets_activation_and_formatter_origin_separate/` — bundle shape separates asset, route, and origin artifacts
- `natvis_pdb_embedded_surface_is_not_same_as_solution_file_surface/` — Visual Studio NatVis delivery route becomes explicit probe-surface evidence
- `lldb_dap_and_lldb_cli_need_explicit_comparison_basis/` — LLDB CLI and DAP lanes require an explicit comparison-basis receipt
- `gdb_versioned_printer_package_drift_is_not_plain_asset_failure/` — GDB package-version or objfile-registration drift is compared honestly
- `malformed_asset_manual_review/` — asset discovery succeeds but probing cannot confidently classify beyond failure/manual review

## Schema starter set

- `visualizer-compat.schema.json` — coarse bundle summary
- `visualizer-policy.schema.json` — intended backend/target policy
- `visualizer-assets.manifest.schema.json` — assets, embedding mode, attachment point, provenance
- `backend-matrix.receipt.schema.json` — backend probe verdicts and evidence
- `activation-route.receipt.schema.json` — activation-route truth per backend lane
- `formatter-origin.receipt.schema.json` — effective formatter origin per backend lane
- `render-golden.report.schema.json` — normalized render-golden comparisons
- `embed-vs-external.report.schema.json` — embedded versus external/manual backend routing
- `probe-surface.receipt.schema.json` — debugger surface, version, OS class, and delivery route
- `comparison-basis.receipt.schema.json` — comparability and drift classification between two observations
- `visualizer-support-bundle.manifest.schema.json` — portable support-bundle layout
- `visualizer-drift.diff.schema.json` — release-to-release compatibility changes
