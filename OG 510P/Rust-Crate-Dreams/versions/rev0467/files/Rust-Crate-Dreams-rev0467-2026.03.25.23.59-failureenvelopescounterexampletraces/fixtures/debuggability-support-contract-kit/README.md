# Debuggability Support Contract Kit fixtures

This fixture family is for **P-0486 Debuggability Support Contract Kit**.
Its goal is not to automate debuggers end to end.
Its goal is to make the first support contract **reviewable**.

## Core bundle shape

- `debuggability-policy.toml` — intended support posture per profile / target
- `debuggability.receipt.json` — observed settings, capture sources, and artifact inventory
- `symbol-layout.manifest.json` — binary → sidecar mapping
- `visualizer.manifest.json` — debugger visualizer assets and backend targets
- `support-posture.report.json` — conservative user-facing verdict
- `support-class.policy.json` — explicit meaning and minimum evidence for posture classes
- `artifact-handoff.manifest.json` — canonical/copy/archive truth for symbols and primary artifacts
- `debugger-backend-coverage.report.json` — debugger-family / OS / version coverage plus capability ceilings
- `backend-observation.receipt.json` — exact debugger-family / version / capability observations
- `source-lookup-impact.report.json` — path-hygiene consequences kept separate from broad posture
- `source-material.manifest.json` — lookup materials and share posture after trimming/remapping
- `session-scope.receipt.json` — exact checked subject scope such as live local, remote, or post-mortem
- `capability-witness.report.json` — task-level debugger evidence rather than broad support folklore
- `claim-ceiling.report.json` — strongest honest outward-facing claim after task and scope limits are considered
- `debug-support-bundle.manifest.json` — portable review handoff bundle for release/support use
- `debuggability-drift.diff.json` — posture drift between two builds
- `notes.md` — compact scenario explanation

## Scenario families

- `windows_msvc_pdb_interactive/` — full debuginfo, expected `pdb`, embedded NatVis asset
- `linux_line_tables_only_backtrace/` — enough for backtraces, not enough to confidently promise rich interactive debugging
- `macos_dsym_missing_sidecar/` — expected `dSYM` absent or weaker than policy
- `release_strip_regression/` — release profile drift that weakens debugger support without changing the entire app story
- `linux_split_dwarf_sidecar/` — split DWARF sidecars discovered and reported separately from the main binary so Linux support posture stays explicit
- `release_debug_zero_implicit_strip_drift/` — release posture weakened by subtle debug/strip drift rather than an obvious crash
- `build_dir_layout_v2_sidecar_relocation/` — path churn that should not be mistaken for posture churn unless handoff truth broke
- `trim_paths_with_source_lookup_boundary/` — privacy-oriented path changes that weaken or obscure source lookup without necessarily destroying all debugger value
- `windows_natvis_pdb_must_not_imply_uniform_backend_coverage/` — Microsoft-oriented sidecars/assets that still do not prove uniform debugger-family support
- `artifact_rich_build_still_needs_manual_review_for_async_and_expr/` — symbol-rich builds that still need explicit evidence before claiming async-debugging or expression-evaluation support
- `windows_msvc_lane_observed_but_not_portable_to_other_backends/` — one observed Visual Studio lane that must not imply cross-backend support
- `trim_paths_keeps_paths_private_but_internal_source_archive_still_needed/` — privacy-improving path changes that still require explicit source-material accounting
- `portable_bundle_keeps_sidecars_backend_evidence_and_source_materials_separate/` — portable support bundle that joins posture, sidecars, backend evidence, and source materials without flattening them
- `core_dump_symbolication_is_not_live_session_scope/` — post-mortem inspection is a different session scope than live debugging
- `locals_backtrace_and_pretty_render_do_not_settle_rust_expression_eval/` — healthy basic debugging evidence that still stops short of expression-evaluation claims
- `lldb_linux_witness_does_not_settle_macos_or_pdb_lanes/` — one checked LLDB/Linux lane that does not settle other OS / format lanes
- `portable_bundle_keeps_posture_scope_and_capability_witnesses_separate/` — portable bundle that keeps posture, subject scope, task evidence, and claim ceilings distinct

## Schema starter set

- `debuggability.schema.json` — coarse receipt / bundle summary
- `debuggability-policy.schema.json` — intended support posture policy
- `symbol-layout.manifest.schema.json` — primary artifact to sidecar mapping
- `visualizer.manifest.schema.json` — visualizer asset/backend map
- `support-posture.report.schema.json` — conservative support verdict plus policy match
- `support-class.policy.schema.json` — support-class meaning plus minimum evidence
- `artifact-handoff.manifest.schema.json` — canonical/copy/archive truth for symbol and release handoff
- `debugger-backend-coverage.report.schema.json` — debugger-family coverage plus capability ceilings and portable-claim ceiling
- `backend-observation.receipt.schema.json` — exact backend-family / version / capability observations
- `source-lookup-impact.report.schema.json` — path-hygiene/source-lookup consequences
- `source-material.manifest.schema.json` — lookup materials and share posture after trimming/remapping
- `session-scope.receipt.schema.json` — exact checked subject scope and launch/attach/dump route
- `capability-witness.report.schema.json` — task-level debugger evidence matrix
- `claim-ceiling.report.schema.json` — strongest honest outward-facing claim after narrower evidence is considered
- `debug-support-bundle.manifest.schema.json` — portable review handoff bundle
- `debuggability-drift.diff.schema.json` — release-to-release posture changes
