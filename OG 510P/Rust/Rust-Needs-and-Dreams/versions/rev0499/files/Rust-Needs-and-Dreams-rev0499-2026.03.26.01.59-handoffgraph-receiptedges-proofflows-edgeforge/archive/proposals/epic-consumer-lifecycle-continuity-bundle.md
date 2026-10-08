# Epic Proposal: Consumer Lifecycle Continuity Bundle (`cargo lifecycle` + `consumer-lifecycle-pack/v0`)

## One-sentence pitch
Make Rust consumer-side continuity boring by standardizing a portable **install → update → rollback/uninstall → route-change** receipt chain instead of leaving installed-state ownership, home changes, and support archaeology scattered across installer logs, package-manager state, and tool-local updaters.

## Deliverables
- `cargo lifecycle` reference tool
- schemas:
  - `consumer-lifecycle-brief/v0`
  - `managed-state/v0`
  - `update-plan/v0`
  - `update-receipt/v0`
  - `rollback-receipt/v0`
  - `uninstall-receipt/v0`
  - `route-change-receipt/v0`
  - `consumer-lifecycle-pack/v0`
  - `consumer-lifecycle-handoff/v0`
- adapters/importers for:
  - `install-pack/v0`
  - `install-receipt/v0`
  - `update-continuity` lane artifacts
  - `distribution-contract-pack/v0`
  - `route-pack/v0`
  - selected release/support/incident/policy attachments
- docs:
  - first-install to managed-state recipe
  - source-build vs prebuilt continuity recipe
  - rollback / uninstall ownership recipe
  - route/home change review recipe
  - support / incident archaeology handoff guide

## Why now (signals)
- Cargo install already defines install-root precedence, source classes, reinstall triggers, packaged-lock behavior, and config-discovery boundaries, which means there are real first-party lifecycle semantics to import rather than invent.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- Cargo uninstall removes packages installed with `cargo install` and uses the same root-precedence model, which makes ownership scope a first-class lifecycle fact instead of a hidden filesystem assumption.
  https://doc.rust-lang.org/cargo/commands/cargo-uninstall.html
- Cargo package says `--exclude-lockfile` is not for general use because some consumers expect the lockfile, including `cargo install --locked`, which means producer release posture and consumer continuity are already linked.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Source replacement is only for exact-copy mirrors and not for patching or private registries; vendored sources are read-only and modifications should use `[patch]` or `path`, which means route changes and divergent local carries already have different official semantics.
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
  https://doc.rust-lang.org/cargo/commands/cargo-vendor.html
- Cargo’s 1.86 development update explicitly highlighted `cargo install-update` as a plugin and said built-in installed-binary update support is still being tracked, so the continuity gap is real and current.
  https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- The archive’s Epic Contribution Ladder 2026 now ranks Consumer Lifecycle Continuity in the top buildable band, but until now did not specify the MVP artifact family clearly enough.
  ../design/epic-contribution-ladder-2026.md

## Non-goals
- replacing Cargo, rustup, system package managers, or installer ecosystems;
- shipping a background update daemon;
- pretending all installed software is owned by one manager;
- flattening route changes into ordinary updates;
- flattening producer release evidence into consumer mutation receipts;
- turning lifecycle review into a machine-wide package inventory empire.

## Strategic value
This deserves promotion because it gives the archive a **consumer-side continuity composition point**.
With it:
- install tools and package managers can export comparable continuity receipts without pretending they are the same tool;
- support and incident workflows can import current ownership and recent mutation truth without shell-history archaeology;
- workstation migration and local overlay consumers can preserve route/home changes explicitly;
- future update support in Cargo can land into a portable receipt family instead of another isolated local state file.

The prize is not another updater.
The prize is a reviewable consumer-side continuity boundary that other tools can import.

## Proposed shape
Ship a narrowly scoped bundle layer:
1. import `install-pack/v0` and `install-receipt/v0` as the first-install boundary;
2. record update/rollback/uninstall events as typed lifecycle receipts rather than one generic mutation blob;
3. import route/home changes explicitly from route-level evidence instead of flattening them into version changes;
4. maintain one current `managed-state/v0` with explicit ownership and drift posture;
5. emit bounded handoffs for support / incident / policy / inventory / archaeology consumers;
6. provide diffing that preserves event-class distinctions and `INCONCLUSIVE` posture.

## Critical design bet
The critical bet is that **consumer lifecycle continuity should stop at managed-state and mutation truth**.
That means:
- first-install truth is imported,
- current managed ownership is explicit,
- update / rollback / uninstall / route-change events are explicit,
- downstream handoffs are explicit,
- but release orchestration, package-admission verdicts, registry governance, and universal package management stay outside the bundle.

Without that boundary, the contribution either stays too weak to matter or bloats into a fake universal software manager.

## Milestones
1. **v0 first-install + current-state lane**
   - `consumer-lifecycle-brief` / `managed-state`
   - import `install-pack/v0`
2. **v0.2 update / rollback lane**
   - `update-plan` / `update-receipt` / `rollback-receipt`
   - preserve route/home and ownership outcomes explicitly
3. **v0.3 uninstall / ownership lane**
   - `uninstall-receipt`
   - record retained shared or unmanaged state
4. **v0.4 route-change lane**
   - `route-change-receipt`
   - preserve exact-copy-vs-divergent continuity posture
5. **v1 downstream handoffs**
   - `consumer-lifecycle-pack` / `consumer-lifecycle-handoff`
   - support support / incident / archaeology consumers without overclaiming authority

## Execution order
Use [`design/consumer-lifecycle-continuity-bundle.md`](../design/consumer-lifecycle-continuity-bundle.md) as the top-level bundle definition.
Then roll out beneath it in this order:
1. [`proposals/epic-consumer-install-kit.md`](./epic-consumer-install-kit.md)
2. [`proposals/epic-update-continuity-kit.md`](./epic-update-continuity-kit.md)
3. [`proposals/epic-distribution-contract-stack.md`](./epic-distribution-contract-stack.md)
4. route/home-change imports from the Distribution-Route Mobility stack
5. bounded support / incident / policy consumers

## Success metrics
- humans can reconstruct current consumer-side ownership and recent mutation history from one pack;
- updates, rollbacks, uninstalls, and route changes remain visibly distinct;
- support / incident consumers can import lifecycle truth without re-scraping terminals or CI logs;
- tool-local updaters and manager state files can normalize into one bounded ecosystem vocabulary;
- the ecosystem gets one explainable continuity seam instead of scattered installer logs, updater state, and path folklore.
