# Design: Update Continuity Kit (`cargo update-continuity`, update / rollback / uninstall truth)

## Goal
Turn Rust software updates from a mix of install receipts, release-feed folklore, updater-specific JSON, path ownership assumptions, and post-failure shell archaeology into a **portable update boundary**.

This kit should make six things explicit:
1. **what installed subject the machine started from**,
2. **what update candidates and comparators were considered**,
3. **which plan, refusal, or delegation path was selected**,
4. **what apply result actually occurred**,
5. **what rollback / downgrade / uninstall / ownership facts hold now**,
6. **what downstream consumers may import without redefining the lifecycle event**.

The worthy contribution here is **not** another updater crate, package-manager wrapper, app-store shim, or release-feed service.
It is the thin consumer-side lifecycle boundary above first-install receipts and below broader product/support conclusions that multiple Rust lanes already need.

Read this together with:
- [`design/update-continuity-lane-map.md`](./update-continuity-lane-map.md)
- [`design/update-continuity-pilot-program.md`](./update-continuity-pilot-program.md)
- [`design/consumer-install-kit.md`](./consumer-install-kit.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/release-truth-stack.md`](./release-truth-stack.md)
- [`proposals/epic-update-continuity-kit.md`](../proposals/epic-update-continuity-kit.md)

## Why now
Fresh upstream and ecosystem signals all point the same way:
- `cargo install` now documents concrete reinstall triggers, default lockfile ignoring unless `--locked` is used, install-root tracking files, and the fact that `--no-track` disables both tracking metadata and Cargo’s concurrent-install protection. That means ordinary Cargo installs already have lifecycle state that later update tools must interpret.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
  https://doc.rust-lang.org/cargo/reference/config.html
- The Cargo 1.86 development-cycle report highlighted `cargo install-update` and said built-in support is being tracked in `#4101`, which is unusually direct evidence that installed-binary update continuity remains outside Cargo proper.
  https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- `cargo-binstall` is explicit that it searches repository releases, quickinstall, alternate targets, and finally `cargo install`. That means update behavior already spans materially different candidate and apply paths.
  https://github.com/cargo-bins/cargo-binstall
- cargo-dist and `axoupdater` make release-hosted, receipt-driven updater flows real, while the February 2026 cargo-dist release added mirrors and explicitly reduced risk around interrupted partial installation.
  https://github.com/axodotdev/cargo-dist/releases
  https://github.com/axodotdev/axoupdater
- Tauri’s updater docs now expose dynamic versus static update sources, downgrade customization, platform-target matching, and Windows before-exit hooks. That is strong evidence that update semantics are already a first-class product surface for Rust apps.
  https://v2.tauri.app/plugin/updater/
- `update-kit` openly models update as **Detection -> Check -> Plan -> Apply**, and `self-replace` exists specifically because replace/delete semantics are platform-sharp. Those are the exact ingredients a shared continuity layer should preserve without swallowing whole updater implementations.
  https://docs.rs/update-kit/latest/update_kit/
  https://docs.rs/self-replace/latest/self_replace/
- Cargo and rustup are still clarifying install-path ownership and uninstall cleanup; the Cargo 1.90 cycle says Rustup should only remove content it manages. That pushes ownership and uninstall scope into first-class lifecycle truth instead of afterthoughts.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/

Taken together, ideal Rust now needs a **consumer-side update continuity layer** above install truth and below support / productization / incident consumers.

## Base artifact family

### 1. `installed-subject/v0`
Identity for the exact installed subject the machine starts from:
- package / binary / app identity
- current version and source/import hints
- install root and mutation scope
- install manager or imported acquisition profile
- current channel / feed / comparator defaults when known
- evidence links to one or more install receipts
- explicit unknowns and imported-lossiness notes

### 2. `update-candidate-set/v0`
The visible next-step options:
- checked channel(s), host(s), feed(s), or mirrors
- candidate versions / releases / artifacts
- target/platform matching
- comparator policy (`greater-than`, `not-equal`, custom policy, pinned, hold)
- refusal reasons and filtered-out candidates
- verification preconditions and network/offline posture

### 3. `update-plan/v0`
The chosen action boundary:
- no-op / hold / notify / download / stage / apply / delegate / uninstall / rollback
- candidate chosen and why
- fallback order and refusal notes
- preconditions (permissions, free space, restart, supported platform, signatures, etc.)
- whether apply is in-place, side-by-side, package-manager delegated, or external-tool delegated

Design rule: **check/plan truth is not apply truth**.

### 4. `update-apply-report/v0`
What actually happened when the plan ran:
- start/end timestamps
- staged assets and applied assets
- files or bundle elements mutated
- delegated tool/provider used
- restart / pre-exit / post-relaunch requirements
- pass/fail/warn/inconclusive/interrupted status
- partial-install indicators and recovery hints

### 5. `rollback-report/v0`
The recovery lane:
- rollback eligibility and source
- downgrade policy versus emergency rollback policy
- rollback action performed, skipped, unsupported, or delegated
- prior version / state references when available
- remaining drift or residue

### 6. `ownership-report/v0`
Managed-content scope after mutation:
- which paths/artifacts are owned by this updater or manager
- co-located but unmanaged content notes
- uninstall scope
- cleanup policy
- handoff to rustup / OS package manager / app-store / external manager when relevant

### 7. `update-pack/v0`
Portable bundle containing:
- `installed-subject/v0`
- `update-candidate-set/v0`
- `update-plan/v0`
- optional `update-apply-report/v0`
- optional `rollback-report/v0`
- optional `ownership-report/v0`
- raw attachments (release feed snippets, updater JSON, logs, delegated-tool receipts, support notes)
- bounded downstream handoffs

### 8. `update-diff/v0`
Diffable review artifact for comparing two update events or states:
- current-subject drift
- candidate/comparator drift
- chosen-plan drift
- apply-result drift
- rollback-policy drift
- ownership / uninstall-scope drift

### 9. `update-handoff/v0`
Lossy summaries for downstream consumers such as:
- CLI / Client / Extension / Operator productization
- Support / incident response
- Distribution archaeology
- Policy / security review
- assistant / editor views

## Reference UX
A reference implementation could expose:
- `cargo update-continuity detect` — emit `installed-subject/v0`
- `cargo update-continuity check` — emit `update-candidate-set/v0`
- `cargo update-continuity plan` — emit `update-plan/v0`
- `cargo update-continuity apply` — emit `update-apply-report/v0`
- `cargo update-continuity rollback` — emit `rollback-report/v0`
- `cargo update-continuity own` — emit `ownership-report/v0`
- `cargo update-continuity diff --against <ref|path>` — compare lifecycle states without flattening them into release or install claims
- `cargo update-continuity pack` — bundle `update-pack/v0`

## Theory of change
The key design move is to separate:
- **current installed-subject truth**,
- **visible update-candidate and comparator truth**,
- **plan / refusal / delegation truth**,
- **apply-result truth**,
- **rollback / uninstall / ownership truth**,
- and **downstream handoff**.

That separation matters because today’s Rust tooling often collapses these into one fake story:
- a release feed becomes “the update result,”
- a successful check becomes “the machine is updated,”
- a package-manager or installer invocation becomes “owned forever by this tool,”
- an interrupted install becomes “probably fine,”
- or a support answer treats “latest release exists” as proof of what a user machine now contains.

If those truths stay flattened together, downstream tools will keep duplicating partial lifecycle models and every updater lane will keep reinventing the same support archaeology.

## Shared stack role
This kit is a lower-level anchor between the archive’s **Distribution Contract / Productization / Support** corridor.
It should be treated as:
- a **Distribution Contract** import for the starting install receipt and selected acquisition facts,
- a **Release Truth** / **Signed Binaries** / **Airgap** consumer when update candidates come from those systems,
- a reusable input to **CLI Productization**, **Client Productization**, **Extension Productization**, and **Operator Productization** when shipped software evolves in place,
- and a bounded evidence source for support / incident / policy consumers.

## Adjacent kits and boundaries
- **Consumer Install Kit** owns one first-install event: install subject, visible candidates, selection, verification, mutation, and install receipt.
- **Distribution Contract Stack** owns the broader consumer-side acquisition event around catalogs/channels/fallback/install receipts.
- **Release Truth Stack** owns producer-side releases, binaries, installers, updater artifacts, signatures, and provenance.
- **Migration Truth Stack** owns maintainer/adopter source and compatibility migration. Update Continuity Kit owns operational mutation of installed software on machines.
- **Support Envelope Kit** owns platform/runtime/version support posture. Update Continuity Kit records what actually changed, what remains installed, and what rollback/uninstall facts exist.
- **Policy Kit** owns explicit allow/hold/waive decisions consuming imported evidence. Update Continuity Kit records candidate, plan, and apply facts.
- **Airgap Kit** owns restricted-network topology and validation posture. Update Continuity Kit may import mirror or offline constraints without becoming the whole airgap story.

## Ranked execution path
The lane rule lives in [`design/update-continuity-lane-map.md`](./update-continuity-lane-map.md), and the ranked rollout lives in [`design/update-continuity-pilot-program.md`](./update-continuity-pilot-program.md).
The intended order is:
1. source-installed tool lane,
2. prebuilt reinstall lane,
3. receipt-driven updater lane,
4. bundle/app updater lane,
5. delegated-manager + ownership lane,
6. forensic/support handoff lane.

That order deliberately proves direct, Cargo-adjacent lanes first and only then widens into app-bundle, delegated, and support-heavy paths.
