# Cargo Build-Dir Consumer Transition Kit fixtures

This fixture family exists to make **P-0489 Cargo Build-Dir Consumer Transition Kit** less abstract.

The point is not to stabilize Cargo internals from the outside.
The point is to standardize one small migration bundle another maintainer can review.

## Core bundle files

- `consumer-inventory.manifest.json`
- `layout.snapshot.json`
- `consumer-audit.report.json`
- `consumer-need.report.json`
- `path-contract.json`
- `adapter-plan.json`
- `adapter-authority.receipt.json`
- `adapter-viability.report.json`
- `windowed-viability.matrix.json`
- `transition.receipt.json`
- optional `transition.diff.json`
- optional `rehearsal-support-bundle.manifest.json`
- `notes.md`

## Scenario families

### `deps_scrape_ci`
Proves the classic fragile case:
- a helper scrapes `target/debug/deps`,
- the need is real,
- but the path assumption is not a public Cargo contract,
- so the bundle must either offer a safer adapter or say `manual_review_required`.

### `out_dir_helper`
Proves that not every `target/.../build/...` consumer should keep scraping:
- some helpers really want build-script-owned outputs,
- the sharper contract is `OUT_DIR` and/or build-script JSON,
- and the bundle should route the consumer there conservatively.

### `new_layout_rehearsal`
Proves that the crate should help compare:
- legacy layout observation,
- `-Zbuild-dir-new-layout` rehearsal,
- changed risk posture,
- without overclaiming breakage it cannot prove.

### `redirect_to_artifact_handoff`
Proves that some consumers never needed intermediate layout at all:
- they actually want a final artifact,
- so the right answer is to redirect them away from build-dir assumptions.

### `bin_path_from_test_inference`
Proves that some helpers are really trying to locate a built binary from a test lane:
- the failure mode is concrete in the March 2026 call for testing,
- the sharper adapter is often `CARGO_BIN_EXE_*`,
- and the bundle should keep older-Cargo fallback pressure explicit through an adapter-viability report.

### `target_dir_from_out_dir_inference`
Proves that not every `OUT_DIR`-adjacent guess is really about build-script-owned output:
- some helpers try to infer target-dir from `OUT_DIR` or from their own binary path,
- that is a layout-coupled guess, not a stable contract,
- and the bundle should separate true build-script contracts from guessed workspace topology with a conservative viability class.

### `rustc_user_requested_artifact_lookup`
Proves that some consumers are really asking for a user-requested artifact while scraping compiler-oriented locations:
- the gap may be partly solved by handoff surfaces,
- partly blocked on upstream features,
- and the bundle should preserve that distinction.

## Design guardrails

- Keep observed facts, consumer needs, adapter suggestions, adapter authority, and adapter-viability windows separate.
- Prefer small stable schemas over giant directory dumps.
- Preserve `manual_review_required` whenever no honest adapter exists.
- Optimize for issue attachments, CI review bundles, and upgrade rehearsals.

## 2026-03-23 refresh

This fixture family now also exists to prove four additional truths:

1. **consumer-need truth** — what job the workflow was actually trying to do;
2. **adapter-authority truth** — what source class authorizes the suggested route;
3. **windowed-viability truth** — which Cargo/layout windows really hold;
4. **rehearsal-bundle truth** — whether those facts travel together for migration review.
