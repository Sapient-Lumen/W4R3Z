# Design: Consumer Lifecycle Continuity Bundle (shared receipt chain for install → update → rollback/uninstall → route change)

## Goal
Turn the consumer side of Rust software into a **reviewable continuity corridor** instead of a pile of installer logs, local path folklore, ad hoc update plugins, and support guesses.

The bundle should make seven things explicit and portable:
1. **what the managed subject is right now**,
2. **how it first arrived**,
3. **which route/home/channel it currently uses**,
4. **which update or rollback choices were visible**,
5. **what mutation actually happened on disk**,
6. **what ownership scope is still claimed**, and
7. **what downstream consumers may import without redefining the lifecycle.**

The worthy contribution here is **not** a universal installer, universal updater, package-manager replacement, or app store.
It is the thin bundle layer above existing install/update/distribution notes that gives Rust one reusable consumer-side receipt chain.

Read this together with:
- [`design/consumer-install-kit.md`](./consumer-install-kit.md)
- [`design/update-continuity-kit.md`](./update-continuity-kit.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/distribution-route-mobility-stack.md`](./distribution-route-mobility-stack.md)
- [`design/release-truth-stack.md`](./release-truth-stack.md)
- [`proposals/epic-consumer-lifecycle-continuity-bundle.md`](../proposals/epic-consumer-lifecycle-continuity-bundle.md)

## Why now
Fresh official Cargo/Rust signals all point toward the same missing layer:
- Cargo install explicitly defines install-root precedence, source classes (`crates.io`, `--git`, `--path`, `--registry`), reinstall triggers, lockfile behavior, and config-discovery boundaries. In particular, installed binaries live in an install root, packaged `Cargo.lock` is ignored unless `--locked` is passed, and non-`--path` installs ignore project-local config discovery and instead begin at `$CARGO_HOME/config.toml`.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- Cargo uninstall is a real inverse lane, but it only knows about packages installed with `cargo install` and uses the same root-precedence model, which means uninstall truth is not the same thing as “everything in this directory”.
  https://doc.rust-lang.org/cargo/commands/cargo-uninstall.html
- Cargo packaging docs say `--exclude-lockfile` is **not for general use** because some consumers expect a lockfile, including `cargo install --locked`, which means producer release choices and consumer update continuity are already linked through lock posture.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- Cargo’s source-replacement docs say exact-copy mirrors are different from patching and different from private registries; Cargo vendor says vendored sources are read-only and directs actual modifications toward `[patch]` or `path` dependencies. That means consumer route/home changes and local divergent carries already have different official meanings.
  https://doc.rust-lang.org/cargo/reference/source-replacement.html
  https://doc.rust-lang.org/cargo/commands/cargo-vendor.html
- Cargo’s 1.86 development update explicitly highlighted `cargo install-update` as a plugin and said built-in support is still being tracked, which means installed-binary update continuity remains outside Cargo proper.
  https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- The archive’s own Epic Contribution Ladder 2026 now ranks Consumer Lifecycle Continuity as one of the most buildable top-band candidates, but until now it did not have a single note that states what the bundle should actually be.
  ./epic-contribution-ladder-2026.md

Taken together, the missing contribution is not “install better” or “self-update better”.
It is “make the **consumer lifecycle itself** portable, reviewable, and handoff-ready across install, update, rollback, uninstall, and route changes.”

## Bundle members
Treat this as a deliberate bundle composed from existing leaves and stacks:
- **Consumer Install Kit** owns first-install candidate discovery, selection, and receipt truth.
- **Update Continuity Kit** owns compare / plan / apply / rollback / uninstall event truth after first install.
- **Distribution Contract Stack** owns stack-level consumer acquisition and ownership handoff across lanes.
- **Distribution-Route Mobility Stack** owns home / route changes and exact-copy-vs-divergent distinctions.
- **Release Truth Stack** remains upstream producer evidence that may be imported but never substituted for consumer receipts.

This note exists because the archive needed a sharper claim about the **composition boundary above those files**.

## Core artifact family

### 1. `consumer-lifecycle-brief/v0`
A concise summary for humans and assistants:
- subject label and current selected version
- install root / ownership summary
- current route class and current manager/tool summary
- last lifecycle mutation (`INSTALL`, `UPDATE`, `ROLLBACK`, `UNINSTALL`, `ROUTE_CHANGE`, `REPAIR`, `UNKNOWN`)
- current continuity posture (`MANAGED`, `PARTIAL`, `IMPORTED`, `UNOWNED`, `UNKNOWN`)
- warning / drift / incompleteness summary
- freshness / review timestamp

### 2. `managed-subject/v0`
Identity for the consumer-managed thing:
- package / binary / app subject identity
- selected version or version set
- installed binary set / selected components
- target triple / host tuple
- install root / scope identity
- manager identity (`cargo-install`, `package-manager`, `installer`, `custom`, `unknown`)
- route-class summary

### 3. `managed-state/v0`
What is currently claimed as owned:
- imported `managed-subject/v0`
- current route/home details
- currently managed files / links / directories when practical
- unmanaged-adjacent or partially-owned warnings
- lock posture summary where relevant
- release / install / update receipt backreferences
- current support / sunset / incident posture pointers when present

### 4. `lifecycle-event/v0`
Common header for any consumer mutation:
- event id
- event class (`INSTALL`, `UPDATE`, `ROLLBACK`, `UNINSTALL`, `REPAIR`, `ROUTE_CHANGE`, `IMPORT`)
- runner identity
- timestamp
- prior-state ref
- planned-vs-observed posture
- success / partial / failure / inconclusive outcome

### 5. `update-plan/v0`
What change is proposed before mutation:
- current managed-state ref
- visible candidate/update set summary
- policy or channel constraints
- selected target state
- refusal reasons for skipped candidates
- expected route/home continuity or change
- expected ownership and rollback consequences

### 6. `update-receipt/v0`
What update actually happened:
- imported `lifecycle-event/v0`
- prior and resulting version/state refs
- actual route/home used
- fetched artifacts / rebuilt-from-source summary
- verification results and skipped checks
- ownership mutations and replaced files
- warnings / lossy imports / residual drift

### 7. `rollback-receipt/v0`
What reversal or downgrade actually happened:
- imported `lifecycle-event/v0`
- triggering reason
- target prior state / selected fallback
- data-loss or compatibility warnings
- remaining drift and unresolved leftovers

### 8. `uninstall-receipt/v0`
What was removed and what was left behind:
- imported `lifecycle-event/v0`
- removed binaries / links / directories
- retained shared/unmanaged content
- root-scope confirmation
- residual state summary

### 9. `route-change-receipt/v0`
How a managed subject moved homes without pretending that is “just an update”:
- imported `lifecycle-event/v0`
- prior route class and new route class
- equivalence-vs-divergence posture
- continuity intent (`MIRROR_SWITCH`, `REGISTRY_MOVE`, `PREBUILT_TO_SOURCE`, `SOURCE_TO_PREBUILT`, `LOCAL_CARRY`, `SUCCESSOR_ROUTE`, `UNKNOWN`)
- compatibility / verification consequences
- required downstream handoffs

### 10. `consumer-lifecycle-pack/v0`
Attachable bundle linking:
- `consumer-lifecycle-brief/v0`
- current `managed-state/v0`
- latest install / update / rollback / uninstall / route-change receipts
- imported release/install evidence pointers
- bounded support / incident / policy / inventory handoffs

### 11. `consumer-lifecycle-handoff/v0`
Lossy but explicit export for downstream consumers such as:
- support and incident intake,
- policy / inventory / trust consumers,
- archaeology and workstation migration,
- local org overlays and environment/bootstrap consumers.

## Reference UX
A reference implementation could expose:
- `cargo lifecycle status` — emit current `managed-state/v0`
- `cargo lifecycle plan-update` — emit `update-plan/v0`
- `cargo lifecycle record --from <tool|receipt|log>` — normalize a real event into a lifecycle receipt
- `cargo lifecycle diff <state-a> <state-b>` — compare managed states without flattening route changes into ordinary updates
- `cargo lifecycle pack` — bundle `consumer-lifecycle-pack/v0`

## Theory of change
The critical design move is to separate:
- **managed subject**,
- **current owned state**,
- **candidate change set / policy**,
- **specific event type**,
- **actual mutation receipt**,
- and **downstream handoff**.

That separation matters because current Rust practice often collapses them into one fake story:
- a release page becomes “what the user now has”,
- an install log becomes “proof of current ownership”,
- a self-update tool becomes “the lifecycle authority”,
- a vendored or mirrored lane becomes “the same thing, just elsewhere”,
- or an uninstall command becomes “everything under this path is gone now”.

If those truths stay flattened together, the ecosystem will keep getting point tools without ever gaining one boring consumer-side continuity vocabulary that other layers can reuse.

## Shared stack role
This bundle should be treated as the archive’s **consumer continuity composition point**.
It is:
- above **Consumer Install** and **Update Continuity**,
- beside **Distribution Contract** and **Distribution-Route Mobility**,
- downstream from **Release Truth**,
- and upstream of support / incident / policy / inventory / archaeology consumers.

That makes it a good epic candidate precisely because it reuses existing archive leaves instead of requiring another new empire.

## Adjacent boundaries
- **Consumer Install Kit** still owns first visible candidates, selection, and first receipt.
- **Update Continuity Kit** still owns detailed event lanes like compare / apply / rollback / uninstall.
- **Distribution Contract Stack** still owns acquisition/ownership composition at the stack level.
- **Distribution-Route Mobility Stack** still owns route-class semantics and home changes.
- **Release Truth Stack** still owns producer publication and attachments.
- **Package Admission / Trust / Policy** remain importing consumers rather than silently becoming lifecycle authority.

## MVP boundary
A worthy first implementation should prove exactly four things:
1. import first-install truth from the Consumer Install lane;
2. record one update event with explicit route/home and ownership outcomes;
3. record one rollback or uninstall event without overstating ownership;
4. emit one bounded handoff for support/incident/policy consumers.

That is enough to validate the bundle without becoming a universal updater or environment manager.

## Non-goals
Do **not** turn this into:
- a universal installer,
- a self-update daemon,
- a package-manager abstraction layer,
- a machine-wide package inventory empire,
- or a fake single “current version is healthy” score.

Also avoid flattening:
- route changes into ordinary updates,
- ownership claims into path existence,
- producer release evidence into consumer mutation receipts,
- uninstall success into proof that no related state remains.

## Success criteria
- humans can reconstruct a managed Rust subject’s consumer lifecycle from one portable bundle;
- install, update, rollback, uninstall, and route change remain visibly distinct;
- ownership scope is explicit enough to avoid overstated uninstall/update claims;
- support / incident / policy consumers can import lifecycle truth without re-scraping shell histories;
- the ecosystem gets one explainable consumer-side continuity seam instead of scattered installer conventions, updater logs, and path folklore.
