# Epic proposal: Update Continuity Kit (`cargo update-continuity`, `update-pack/v0`)

## One-line thesis
Build a thin Rust companion layer for **consumer-side update continuity** that links **current installed subject**, **candidate/comparator truth**, **plan/apply/rollback results**, **managed-content ownership**, and **downstream support/policy/productization handoffs** without confusing them with either first-install receipts or producer-side release truth.

## Why this is now worth doing
Rust’s current update signals now point to a **shared lifecycle boundary above the ingredients** rather than another one-off updater helper:
- `cargo install` documents reinstall triggers, default lockfile ignoring, system/user-level config discovery, and install-root tracking metadata, with `--no-track` explicitly disabling metadata and concurrent-install protection.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
  https://doc.rust-lang.org/cargo/reference/config.html
- The Cargo 1.86 development-cycle report explicitly highlighted `cargo install-update` and said built-in support is being tracked in `#4101`.
  https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- `cargo-binstall` is explicit about fallback across repository releases, quickinstall, alternate targets, and `cargo install`, which means the prebuilt reinstall lane already exists as a distinct continuity story.
  https://github.com/cargo-bins/cargo-binstall
- cargo-dist now has mirrors and lower-risk interrupted-install handling, while `axoupdater` explicitly uses cargo-dist install receipts to learn and mutate installed state.
  https://github.com/axodotdev/cargo-dist/releases
  https://github.com/axodotdev/axoupdater
- Tauri’s updater docs expose dynamic/static update sources, target matching, downgrade control, and Windows before-exit hooks. That is a mature Rust app-update lane, but still not a shared ecosystem contract.
  https://v2.tauri.app/plugin/updater/
- `update-kit` already models the lifecycle as Detection -> Check -> Plan -> Apply, and `self-replace` already handles cross-platform self-replace/self-uninstall edge cases. Those are strong ingredients, but they remain crate-local today.
  https://docs.rs/update-kit/latest/update_kit/
  https://docs.rs/self-replace/latest/self_replace/
- Cargo and rustup are still tightening ownership semantics around shared install paths; Cargo 1.90 says Rustup should only remove content it manages. That makes uninstall/cleanup scope part of the same missing boundary.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/

What is still missing is the **kit-level boundary that says one installed Rust subject was reviewed with these update candidates, these comparator/hold/downgrade rules, this chosen plan, this apply result, this rollback/uninstall posture, and these bounded downstream conclusions**.

## Working name
- CLI: `cargo update-continuity`
- primary artifact: `update-pack/v0`

## Scope
### This epic should own
- installed-subject identity and import truth
- update candidate/comparator/fallback selection truth
- chosen update plan and refusal/delegation reasons
- apply results including interrupted / partial outcomes
- rollback, downgrade, uninstall, and managed-content ownership truth
- bounded support / incident / policy / productization handoffs
- verification of pack integrity and imported receipt references
- the lane rule in `design/update-continuity-lane-map.md`
- the ranked rollout in `design/update-continuity-pilot-program.md`

### This epic should not own
- a universal installer or package manager
- producer-side release manifests, signatures, or publish receipts
- one monopoly self-update engine
- one fake “latest” or “safe to update” badge
- flattening source-installed tools, prebuilt reinstall flows, desktop-app updaters, delegated package-manager flows, and uninstall ownership into one runtime model

## Candidate artifact family
### `installed-subject/v0`
The exact currently installed subject, version, path/owner scope, acquisition imports, and lifecycle unknowns.

### `update-candidate-set/v0`
Visible channels, feeds, mirrors, versions, target matches, comparators, and refusal reasons.

### `update-plan/v0`
What the system intends to do next: hold, notify, stage, apply, delegate, rollback, uninstall, or no-op.

### `update-apply-report/v0`
What actually changed, what provider/delegate performed it, which restart/pre-exit behavior happened, and what partial/interrupted residue remains.

### `rollback-report/v0`
What rollback or downgrade path exists, whether it was exercised, and what residue remains.

### `ownership-report/v0`
Which content is managed, what uninstall scope exists, and what is merely co-located.

### `update-pack/v0`
The portable bundle linking install-state identity, candidate discovery, plan/apply/rollback/ownership facts, raw evidence, and bounded handoff notes.

### `update-diff/v0`
What changed between two lifecycle states, with separate sections for:
- current-subject drift
- candidate/comparator drift
- chosen-plan drift
- apply-result drift
- rollback-policy drift
- ownership/uninstall drift

### `update-handoff/v0`
Lossy summaries for CLI/client/extension/operator productization, support, incident response, security/policy, and assistant/editor consumers.

## Recommended rollout
1. source-installed tool lane (`cargo install` + `cargo-update`)
2. prebuilt reinstall lane (`cargo-binstall` + fallback ladder)
3. cargo-dist / `axoupdater` receipt-driven lane
4. Tauri bundle/app updater lane
5. delegated-manager + ownership/uninstall lane
6. broader support/productization handoff lane

This rollout should be driven by [`design/update-continuity-lane-map.md`](../design/update-continuity-lane-map.md) and [`design/update-continuity-pilot-program.md`](../design/update-continuity-pilot-program.md), with Distribution Contract, Release Truth, and productization stacks importing the result rather than replacing it.

## What makes this epic “epic” rather than incremental
An incremental tool would improve one lane:
- a nicer self-update crate,
- a nicer updater feed format,
- a nicer reinstall helper,
- or a nicer dashboard for latest versions.

An epic contribution here instead gives Rust one **portable update continuity contract** above those lanes.
That is strategically different because it can:
- let source-installed tools, prebuilt-binary tools, receipt-driven app updaters, and delegated-manager cases share one lifecycle vocabulary;
- keep current install truth distinct from candidate discovery and from apply result;
- keep rollback/uninstall ownership explicit instead of implicit;
- let support/product/policy consumers reuse update lifecycle facts;
- and absorb future Cargo or app-updater features without forcing every downstream layer to reinvent lifecycle archaeology.

## Design principles
- **Current installed subject truth is not candidate truth.**
- **Check/plan truth is not apply truth.**
- **Direct apply is not delegated apply.**
- **Rollback/downgrade truth is not uninstall truth.**
- **Ownership is not path coincidence.**
- **Release/install stories remain adjacent, not collapsed.**
- **Lossiness and delegation are explicit.**
- **The kit remains thin.**

## Success conditions
This epic is succeeding when Rust teams can say:
- “this is the exact installed subject we started from,”
- “these are the update candidates and comparator rules we considered,”
- “this is the plan we chose or delegated and why,”
- “this is what actually changed on disk or in the bundle,”
- “this is whether rollback, downgrade, or uninstall is possible and who owns it,”
- and “this is what downstream support/product/policy consumers may safely conclude,”

without reconstructing the story from install logs, updater JSON, release pages, path guesses, and local memory.

## Read this with
- `gaps/update-continuity-detection-selection-apply-rollback-and-uninstall.md`
- `design/update-continuity-kit.md`
- `design/update-continuity-lane-map.md`
- `design/update-continuity-pilot-program.md`
- `design/distribution-contract-stack.md`
- `design/release-truth-stack.md`
- `design/cli-productization-stack.md`
- `design/client-productization-stack.md`
