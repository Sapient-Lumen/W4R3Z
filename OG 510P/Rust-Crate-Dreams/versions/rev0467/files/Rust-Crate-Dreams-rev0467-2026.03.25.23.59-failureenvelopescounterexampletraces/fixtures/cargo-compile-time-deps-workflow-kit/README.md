# Cargo Compile-Time-Deps Workflow Kit fixtures

This fixture family exists to make **P-0494 Cargo Compile-Time-Deps Workflow Kit** less abstract.

The point is not to prove that tool-facing workflows are “as good as” `cargo build`.
The point is to export one honest bundle another person can review.

## Core bundle files

- `tool-build.receipt.json`
- `compile-surface.manifest.json`
- `parity-check.report.json`
- `fallback.plan.json`
- `comparison-baseline.lock`
- `override-command.receipt.json`
- `selection-coverage.report.json`
- `workspace-invocation.receipt.json`
- `root-lane.receipt.json`
- `evidence-source.receipt.json`
- `tool-session.link.json`
- `notes.md`

## Scenario families

### `rust_analyzer_separate_target_dir`
Proves the positive case:
- rust-analyzer-style workflow,
- separate target dir to reduce lock contention,
- acceptable editor-oriented parity,
- duplicated artifacts acknowledged rather than hidden.

### `missing_sysroot_src`
Proves that the bundle should say:
- editor/build workflow is configured,
- but sysroot source assumptions are incomplete,
- so capability is degraded and the fix is concrete.

### `target_mismatch_editor_vs_terminal`
Proves that the bundle can say:
- the editor/tool and terminal build are not aiming at the same target surface,
- so parity claims should be conservative,
- and the next step is target alignment or full-build fallback.

## Design guardrails

- Keep observed facts and conservative inference distinct.
- Prefer small stable schemas over editor-specific log scraping.
- Do not let the fixture family imply that tool-facing commands inherit `cargo build` guarantees.

### `label_scoped_override_vs_workspace_baseline`
Proves that the bundle can say:
- a custom override command used `{label}`-style package scoping,
- the observed tool run is therefore narrower than a workspace build claim,
- and the comparison baseline must be frozen explicitly instead of implied.

### `relative_override_command_manual_review`
Proves that the bundle can say:
- the user supplied a custom relative command path,
- the command may still emit JSON and partly work,
- but the invocation provenance is weak enough that the output should stay `manual_review_required`.

### `paired_buildscripts_override_toolchain_specific`
Proves that the bundle can say:
- a toolchain-specific override was used deliberately,
- check/build-script command pairing matters,
- and the resulting workflow can still be an acceptable tool surface without pretending it is a full build.

### `alltargets_false_dev_proc_macro_gap`
Proves that the bundle can say:
- `allTargets = false` reduced target-class coverage,
- a dev-dependency proc-macro lane never became available,
- and the result should stay conservative rather than pretending the proc-macro is just broken.

### `check_workspace_false_first_run_leakage`
Proves that the bundle can say:
- the configured expectation was package-scoped diagnostics,
- startup behavior still observed broader workspace leakage,
- and the receipt should stay manual-review-first until the run shape stabilizes.

### `linked_projects_once_opened_root_scope`
Proves that the bundle can say:
- there were multiple linked projects,
- `once` invocation changed the working-directory/root interpretation,
- and the comparison baseline is narrower than a per-workspace claim unless frozen explicitly.

### `build_dir_separated_target_dir_still_shared`
Proves that the bundle can say:
- rust-analyzer isolation changed `target-dir`,
- but `build-dir` remained shared or otherwise not proven isolated,
- so lock-relief and parity claims must stay narrower than “all roots are independent now.”

### `build_dir_new_layout_manual_review`
Proves that the bundle can say:
- the workflow touched build-dir / target-dir assumptions during the new-layout transition,
- the observed tool result may still be usable,
- but root-lane exactness is weak enough that manual review and/or a fuller build is the honest answer.

### `imported_build_analysis_session`
Proves that the bundle can say:
- a tool-facing run had optional supporting evidence from Cargo build-analysis sessions,
- the session link is useful provenance,
- but it does not silently upgrade the tool run into a stronger correctness claim.
