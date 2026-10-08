# Crate ecosystem pathfinder — replay timebox and knowability plan (2026-03-23)

This note deepens **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** around a thin but important missing layer:
**freeze-time knowability**.

## Main judgment

A worthwhile next implementation pass should promote two more first-class review objects:

- `decision-timebox.receipt.json`
- `as-of-replay.report.json`

Those objects let a team say:

1. what evidence window the frozen starter-set decision actually used,
2. what very fresh releases or newly visible docs surfaces were still outside that window,
3. and what changed when the same task lane is replayed against the current ecosystem later.

## Why this layer matters now

Current official Rust/Cargo/crates.io/docs.rs sources make the gap unusually concrete.

### 1. `pubtime` makes freeze-time boundaries explicit instead of folkloric

The January 2026 crates.io update says the index now includes `pubtime`, and it explicitly names future cooldown periods and replay-as-of-date use cases.
That means the pathfinder lane can now stop hand-waving about “fresh releases” and start publishing a concrete timebox.

### 2. current search and package surfaces are still useful but not decision authority

Cargo `add` says it makes a best-effort source selection.
Cargo `info` says it displays package information and may choose a version based on the declared MSRV when none is specified.
Those are good inputs, but they do not settle task fit, starter-set policy, or what should count as the historically reviewed choice.

### 3. visible support stories can drift without the decision itself changing

Docs.rs metadata lets crates choose default targets and target sets, and the October 2025 docs.rs default-target change proves that what users see first can change later.
That means a current public docs landing page must not silently rewrite what a team originally reviewed.

### 4. search ordering is still not a trustworthy historical oracle

The active crates.io search discussion says ordering remains unresolved and that the current implementation uses weighted text ranking plus lexical tie-breaking for equal rank.
So the pathfinder lane should record search-derived evidence conservatively and refuse to treat current ordering as historical recommendation authority.

## Proposed review objects

### `decision-timebox.receipt.json`

Purpose: capture exactly **when** a starter-set decision was frozen and which evidence windows were in bounds.

Suggested fields:
- `task_lane`
- `starter_set`
- `frozen_at`
- `as_of_cutoff`
- `signal_cutoffs`
- `cooldown_policy_ref`
- `knowledge_scope`
- `blind_spots`
- `manual_review_required`

### `as-of-replay.report.json`

Purpose: compare **freeze-time basis** with **current-view replay** without silently blessing a replacement.

Suggested fields:
- `task_lane`
- `starter_set`
- `replay_mode`
- `baseline_timebox`
- `current_view_at`
- `candidate_deltas[]`
- `drift_events[]`
- `replay_verdict`
- `manual_review_required`
- `notes`

## Suggested workflow

### `cargo pathfinder freeze`
Emit the normal decision pack plus `decision-timebox.receipt.json`.

### `cargo pathfinder replay --lock starter-set.lock.json --as-of <timestamp>`
Reconstruct the decision basis for the declared as-of point and compare it with the current ecosystem surfaces.

### `cargo pathfinder doctor`
Flag:
- current-view evidence being mistaken for freeze-time evidence,
- new releases still inside a cooldown window,
- docs-surface drift being over-read as task-fit drift,
- and search/order changes being mistaken for authoritative recommendation changes.

## Distinctions the implementation must keep explicit

### Freeze-time basis is not current-view convenience

What looks best today may not have been published, visible, or cool-down-cleared when the starter set was frozen.

### Visibility drift is not task-fit drift

A docs.rs default-target shift or public docs posture improvement can justify review without automatically changing the recommended crate.

### Replay is not automatic replacement

A replay that finds a stronger current candidate should still leave replacement as a human decision unless policy says otherwise.

### `cargo add` / `cargo info` are not decision authority

Those commands are useful evidence imports.
They are not a substitute for the decision pack.

## Good proving grounds

1. a new release published just after a starter set was frozen,
2. a docs.rs target/default change that makes support look different later,
3. a current search order that differs from the originally reviewed basis,
4. a portable pathfinder bundle that keeps timebox, replay, and choice separate.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://github.com/rust-lang/crates.io/discussions/9325
- https://doc.rust-lang.org/cargo/commands/cargo-add.html
- https://doc.rust-lang.org/cargo/commands/cargo-info.html
- https://docs.rs/about/metadata
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
