# Cargo Rebuild Why Kit fixtures

This fixture family exists to make **P-0469 Cargo Rebuild Explanation Kit** more concrete.

The goal is not to model every Cargo internal. The goal is to define a small, boring artifact family that can answer:

- which units rebuilt,
- which units were reused,
- which causes are directly observed versus conservative inference,
- which evidence lane produced the fact,
- and which command / profile / target / wrapper assumptions were in force.
- why the chosen baseline was authorized instead of a merely nearby session,
- and whether reverse-dependency fanout proves interface impact or only shows observed rebuilds.

## Intended first scenarios

1. `build_analysis_import_only` — import a Cargo build-analysis session and freeze it into a smaller stable receipt for review or CI handoff.
2. `check_then_build_workspace` — a tool-oriented invocation is followed by a fuller build and reuse collapses unexpectedly.
3. `wrapper_rustflags_drift` — changed wrapper or codegen flags invalidate reuse.
4. `shared_target_lock_hint` — cache locking or shared-build-dir assumptions complicate diagnosis.
5. `source_edit_reverse_dep_fanout` — source edits still fan out into broader rebuilds than users expect.
6. `compile_time_deps_vs_full_build` — tool-surface drift is adjacent evidence, not automatic rebuild proof.
7. `session_wording_drift_freeze` — imported unstable Cargo wording changes, but the stable bundle contract stays honest.
8. `contention_not_rebuild` — blocked shared roots create a waiting story without pretending that waiting itself is the rebuild cause.
9. `nearest_prior_session_is_not_comparable_without_authority_gate` — the closest earlier session is rejected because comparison authority matters more than timestamp proximity.
10. `release_prefers_same_profile_target_baseline_over_nearest_session` — a farther release-profile session is a better baseline than a nearer dev/test run.
11. `private_edit_rebuilds_dependents_without_interface_proof` — reverse fanout is visible but interface change remains unproven.
12. `cargo_check_baseline_needs_scope_gate_before_explaining_cargo_build` — a tempting nearby tool-only session needs an explicit scope gate.
13. `build_dir_split_changes_reuse_context_while_target_dir_stays_constant` — route drift changes reuse context even when final outputs stay familiar.
14. `portable_bundle_keeps_scope_route_and_adjacent_context_separate` — adjacent-lane imports stay visibly imported rather than being flattened into proof.

## Minimal bundle for 0.1

Core:
- `rebuild-context.toml`
- `unit-rebuilds.json`
- `rebuild.receipt.json`
- `notes.md`

When importing Cargo build-analysis sessions:
- `session-index.json`
- `timings-pointer.json`

Optional overlays:
- `fingerprint-delta.json`
- `cache-conflict.report.json`
- `evidence-source.receipt.json`
- `exactness.report.json`
- `baseline-authority.receipt.json`
- `comparison-scope.receipt.json`
- `artifact-route-drift.report.json`
- `reverse-impact.report.json`
- `rebuild-support-bundle.manifest.json`

## Evidence-lane rule

Every scenario should make clear whether a fact came from:

1. `cargo_report_import`
2. `live_capture`
3. `fingerprint_overlay`

The schema should preserve that distinction.
The crate should not silently blur imported Cargo facts and local heuristics into one certainty tone.

## Design rule

A fixture should prefer a **coarse but reliable cause** over a detailed but speculative one.

Good:
- `tool_invocation_drift_possible`
- `target_profile_split`
- `wrapper_or_flags_changed`
- `cache_conflict_possible`
- `manual_review_required`

Bad:
- pretending Cargo exposed a perfect invalidation proof chain when it did not.

## Added planning rule (2026-03-08)

When Cargo build-analysis is available, this fixture family should prefer:

1. importing Cargo session IDs and report output,
2. freezing that input into a smaller stable bundle,
3. and treating HTML timing replay as an attached human aid rather than the machine contract itself.

At the same time, the fixture family must remain useful on stable Cargo via `live_capture` scenarios.


## Added planning rule (2026-03-16)

The fixture family must now preserve two extra truths explicitly:

1. **source truth** — which bundle facts came from imported Cargo report output, JSONL/session logs, live capture, or optional overlays;
2. **exactness truth** — whether a claim is imported verbatim, normalized from observed facts, conservatively inferred, or still manual-review-only.

This is the minimum needed to keep P-0469 honest while Cargo's unstable report surfaces evolve.


## Added planning rule (2026-03-22)

The fixture family must now preserve two more truths explicitly:

1. **baseline authority** — why the selected comparison run was chosen, and why nearer alternates were rejected;
2. **reverse-impact honesty** — whether dependents merely rebuilt, whether a relink-only opportunity is plausible, and where interface change is still unproven.

This is the minimum needed to keep P-0469 honest as Cargo session/report tooling becomes easier to query but still does not directly prove semantic interface preservation.

## Added planning rule (2026-03-22, later pass)

The fixture family must now preserve two more truths explicitly:

1. **comparison scope** — whether candidate and baseline sessions belong to the same explanatory lane at all;
2. **artifact-route drift** — whether `build-dir`, `target-dir`, rust-analyzer private target-dir, or wrapper hash lanes changed the reuse context.

The bundle manifest must also keep **adjacent-lane imports** visible so tool-only or contention context is not silently promoted into rebuild proof.
