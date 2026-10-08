# Cargo Rebuild Explanation Kit — comparison scope and artifact-route plan (2026-03-22)

## Product thesis

`cargo rebuild-why` should now freeze two more review objects explicitly:

1. **comparison scope** — whether the compared sessions belong to the same explanatory lane at all;
2. **artifact-route drift** — whether build-dir, target-dir, wrapper-hash lanes, or tool-owned route changes altered reuse context;
3. **portable bundle inventory** — one manifest that keeps rebuild evidence, route evidence, exactness, and adjacent-lane imports separate.

Without those three layers, a rebuild bundle can still mislead even if the cause vocabulary is careful.

## Why this matters now

Cargo’s current substrate is finally concrete enough that the next missing layer is not “record more build facts”.
The missing layer is **receiver-facing review structure**.

Three current upstream changes made that gap sharper:

- build-analysis sessions now persist across invocations and are queried through `cargo report` commands;
- Cargo docs now make `target-dir` and `build-dir` first-class distinct routes;
- rust-analyzer still documents a separate `cargo.targetDir` escape hatch that prevents locking at the cost of duplicated artifacts.

That means a bundle can tell the truth about rebuild causes and still mislead if it fails to say:

- whether `cargo check` is being compared to `cargo build` or `cargo test`,
- whether the workspace/target/profile surface changed,
- whether the intermediate route changed while the final artifact route stayed constant,
- and whether adjacent tool-only context needs import from a separate lane instead of being treated as proof.

## New receiver-facing artifacts

### `comparison-scope.receipt.json`

Records:
- candidate session id,
- baseline session id,
- comparison dimensions,
- dimension status (`match`, `compatible_with_caveat`, `mismatch`),
- whether the bundle remains `comparison_authorized`, `comparison_authorized_with_caveats`, or `manual_review_required`.

The important rule: **baseline selection** and **comparison scope** are not the same thing.
A baseline can be the best available candidate and still require caveats.

### `artifact-route-drift.report.json`

Records:
- before/after build-dir and target-dir routes,
- rust-analyzer private target-dir posture,
- wrapper hash lane changes,
- route-change classes,
- likely effect on reuse interpretation,
- whether the route drift is merely contextual or comparison-breaking.

The important rule: **route drift is not automatically the rebuild cause**, but it can change what reuse claims are honest.

### `rebuild-support-bundle.manifest.json`

Records:
- bundle id and subject,
- included artifacts,
- imported adjacent-lane context,
- human summary,
- redaction status,
- manual-review zones.

The important rule: **adjacent-lane context must stay explicitly imported**, not silently swallowed.

## Scenario priorities

### 1. `cargo_check_baseline_needs_scope_gate_before_explaining_cargo_build`
Show that a nearby `cargo check` session is tempting but not automatically valid as the explanation baseline for a fuller `cargo build` incident.

### 2. `build_dir_split_changes_reuse_context_while_target_dir_stays_constant`
Show that a route split can preserve final outputs while changing the meaning of reuse expectations.

### 3. `portable_bundle_keeps_scope_route_and_adjacent_context_separate`
Show that imported tool-only context can be useful without being promoted to direct rebuild proof.

## Lane boundaries this plan sharpens

### Not P-0494
If the main question is “what exactly did the tool-only workflow build, and should it fall back to a fuller build?”, that still belongs primarily to **P-0494**.
P-0469 only owns the **scope gate** that says such context was imported and constrained.

### Not P-0490
If the main question is “what blocked progress, for how long, and which shared root collided?”, that still belongs primarily to **P-0490**.
P-0469 may import contention context, but route drift is not a waiting diagnosis by itself.

### Not P-0035
If the main question is “when did this regress across many runs?”, that still belongs primarily to **P-0035**.
P-0469 stays incident-sized.

## Product shape after this pass

A worthy 0.1 crate in this lane should now feel like:

- session import/freeze,
- baseline-authority receipts,
- comparison-scope receipts,
- unit rebuild classification,
- artifact-route drift reports,
- reverse-impact reports,
- exactness/evidence-source receipts,
- and one portable rebuild-support bundle.

That is a better MVP than another visualizer because it gives another engineer something they can actually read, diff, archive, and trust.
