# Gap: Rust still lacks a portable update-continuity contract above install receipts

## Summary
Rust has credible ingredients for **installation**, **release publishing**, **binary verification**, and several forms of **self-update**.
What it still lacks is one portable, reviewable boundary for the next question teams actually hit after install:

> what installation did this machine start from, what update candidates were considered, what comparator/policy/fallback logic decided the next step, what changed on disk or in the bundle, what can be rolled back or uninstalled safely, and who owns the result now?

Today that story is fragmented across:
- `cargo install` reinstall rules, lockfile/config posture, and install-root metadata,
- `cargo-update` workflows for `cargo install`ed tools,
- `cargo-binstall` upgrade-by-reinstall and fallback ladders,
- cargo-dist / `axoupdater` receipt-driven updater flows,
- Tauri’s app-bundle updater plugin,
- `update-kit` / `self-replace` style in-place updater crates,
- package-manager / app-store / delegated-manager ownership boundaries,
- and whatever shell history, updater feed, or support notes survived.

That fragmentation matters because an update is not just “another install.”
A real update has to preserve or explicitly reject:
- the currently installed subject and its provenance,
- channel, mirror, feed, and comparator policy,
- downgrade or rollback posture,
- partial/interrupted-apply handling,
- managed-content ownership and uninstall scope,
- and later support or incident conclusions.

## Why now
- `cargo install` documents reinstall triggers, ignores packaged `Cargo.lock` by default unless `--locked` is used, operates at system/user level, and keeps install-root tracking metadata such as `.crates.toml` / `.crates2.json`; `--no-track` disables both metadata and Cargo’s concurrent-install protection. That is already lifecycle state, not just one-shot download behavior.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
  https://doc.rust-lang.org/cargo/reference/config.html
- The Cargo 1.86 development-cycle report explicitly highlighted `cargo install-update` as the plugin of the cycle and said built-in support is being tracked in issue `#4101`. That is unusually direct evidence that Rust still lacks a first-class installed-tool update lane.
  https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- `cargo-binstall` is explicit that it searches release artifacts, quickinstall, alternate targets, and finally `cargo install`. That means “update this tool” can already mean materially different candidate and apply paths.
  https://github.com/cargo-bins/cargo-binstall
- cargo-dist’s February 2026 release added mirror-aware installer fallback, while `axoupdater` explicitly uses cargo-dist install receipts to learn the currently-installed version before checking or applying updates. That is exactly the point where install receipts stop being enough and update/apply continuity becomes its own missing layer.
  https://github.com/axodotdev/cargo-dist/releases
  https://github.com/axodotdev/axoupdater
- Tauri’s current updater docs make dynamic/static update sources, target matching, downgrade control, and Windows pre-exit hooks explicit. That is a mature application-updater surface, but still not a shared Rust continuity contract.
  https://v2.tauri.app/plugin/updater/
- `update-kit` explicitly describes a channel-aware pipeline of **Detection -> Check -> Plan -> Apply**, while `self-replace` explicitly exists because self-replacing and self-uninstall semantics are operationally sharp, especially on Windows. Those are strong signals that continuity is real, but currently crate-local.
  https://docs.rs/update-kit/latest/update_kit/
  https://docs.rs/self-replace/latest/self_replace/
- Cargo and rustup are also still clarifying install-path ownership: the Cargo 1.90 development-cycle report says Rustup should only remove content it manages. That means uninstall / cleanup truth can no longer be treated as a casual footnote.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/

## What is missing
The missing contribution is a thin **Update Continuity Kit** above install receipts and below broader support / productization conclusions.

It should make six truths portable without flattening them together:
1. current installed-subject truth;
2. update-candidate and comparator truth;
3. update-plan / refusal / delegation truth;
4. apply-result and partial-interruption truth;
5. rollback / downgrade / uninstall ownership truth;
6. bounded downstream handoff truth.

## What “good” looks like
- A machine-readable description of the current installed subject, including install-root ownership and imported acquisition receipts.
- Explicit candidate sets for update checks, including channel, mirror, host, target, and comparator posture.
- Explicit separation between **check/plan** and **apply**.
- Explicit representation of interrupted, partial, skipped, delegated, and rollback-needed outcomes.
- Explicit managed-content and uninstall scope so support tooling can distinguish “co-located” from “owned.”
- Diffable reports that say whether change happened in candidate discovery, comparator policy, chosen plan, apply result, rollback state, or ownership handoff.
- An explicit lane map so source-installed tool updates, prebuilt reinstall flows, receipt-driven updaters, bundle/app updaters, delegated-manager flows, and forensic imports do not collapse into one fake updater score.

## Candidate contribution
Promote an **Update Continuity Kit** with:
1. `installed-subject/v0` for what is currently installed, where, and under which owner/import assumptions,
2. `update-candidate-set/v0` for channels, feeds, mirrors, comparators, and refusal reasons,
3. `update-plan/v0` for the chosen next action,
4. `update-apply-report/v0` for what changed and what failed or was skipped,
5. `ownership-report/v0` and `rollback-report/v0` for cleanup, downgrade, uninstall, and managed-content truth,
6. `update-pack/v0` for bounded downstream handoff,
7. `design/update-continuity-lane-map.md` and `design/update-continuity-pilot-program.md` to keep the lanes and rollout honest.

## Distinction from nearby archive entries
- **Not Consumer Install Kit:** that kit owns one first-install event. Update Continuity Kit starts from an existing installed subject and governs change over time.
- **Not Distribution Contract Stack:** that stack owns the broader acquisition/install event — visible candidates, selection, verification, fallback, and install receipt. Update Continuity Kit imports the resulting installed subject and continues the lifecycle.
- **Not Release Truth Stack:** that stack owns producer-side releases, artifacts, installers, signatures, and published updater material. Update Continuity Kit imports release/update feeds without redefining them.
- **Not Migration Truth Stack:** that stack owns source/API/config migration for maintainers and adopters. Update Continuity Kit owns operational mutation of installed artifacts on machines.
- **Not Support Envelope Kit:** that kit owns supported versions/platforms and docs claims. Update Continuity Kit records what actually changed and what ownership/rollback state exists.
- **Not Airgap Kit:** that kit owns restricted-network topology and offline validation posture. Update Continuity Kit can import mirror/offline constraints but does not become the whole mirror story.
