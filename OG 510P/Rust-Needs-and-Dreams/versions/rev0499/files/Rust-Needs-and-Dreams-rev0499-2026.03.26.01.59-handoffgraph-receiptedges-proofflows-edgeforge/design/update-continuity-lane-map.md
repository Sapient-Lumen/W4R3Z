# Design: Update Continuity Lane Map (source-installed tools, prebuilt reinstall flows, receipt-driven updaters, bundle/app updaters, delegated managers, ownership/uninstall)

## Goal
Make the archive more precise about **what kind of update-continuity claim is actually being made**.

Rust already has many ways to move installed software forward, but the phrase “update support” still hides too much.
A `cargo install-update` run for a source-installed CLI, rerunning `cargo binstall`, an `axoupdater` check that loads a cargo-dist receipt, a Tauri bundle update with custom target matching and downgrade rules, a package-manager- or app-store-delegated flow, and a self-replace/uninstall path are **different but connected** lanes.

The worthy contribution here is therefore not another updater engine, release-feed service, or faux-universal “latest” badge.
It is a **portable lane map and evidence boundary** that lets tools say which update lane they occupy, what assumptions attach to it, where adapters are lossy, and which downstream consumers may reuse the claim honestly.

Read this together with:
- [`design/update-continuity-kit.md`](./update-continuity-kit.md)
- [`design/update-continuity-pilot-program.md`](./update-continuity-pilot-program.md)
- [`design/consumer-install-kit.md`](./consumer-install-kit.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/release-truth-stack.md`](./release-truth-stack.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`proposals/epic-update-continuity-kit.md`](../proposals/epic-update-continuity-kit.md)

## Why this note is needed now
The current Cargo/ecosystem signals line up around one conclusion: Rust needs a better **update-continuity contract**, not just more updater implementations.

- `cargo install` now documents that packaged `Cargo.lock` is ignored by default unless `--locked` is used, that the command operates at system/user level, and that install roots carry tracking files such as `.crates.toml` and `.crates2.json`. `--no-track` disables that metadata and Cargo’s concurrent-install protection. That means the baseline installed-tool lane already has lifecycle-bearing state and ownership implications.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
  https://doc.rust-lang.org/cargo/reference/config.html
- The Cargo 1.86 development-cycle report explicitly highlighted `cargo install-update` (`cargo-update`) as plugin of the cycle and said built-in support is still tracked in `#4101`. That is unusually direct evidence that installed-tool updates remain an ecosystem seam rather than a settled Cargo feature.
  https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- `cargo-binstall` now explicitly describes a search/fallback ladder through repository releases, quickinstall, alternate targets, and finally `cargo install`. That means prebuilt-binary upgrade-by-reinstall is a distinct lane, not just a cosmetic frontend over Cargo.
  https://github.com/cargo-bins/cargo-binstall
- cargo-dist 0.31.0 added mirror fallback for installers, and `axoupdater` explicitly keys its check/update behavior off install receipts produced by cargo-dist. That means receipt-driven updater flows are already real and cannot be reduced to generic release-feed polling.
  https://github.com/axodotdev/cargo-dist/releases
  https://github.com/axodotdev/axoupdater
- Tauri’s updater docs now make dynamic vs static update sources, target matching, downgrade control via `version_comparator`, and Windows `on_before_exit` hooks explicit. That means app-bundle update semantics are already a product surface with sharper rules than ordinary installed-tool refresh.
  https://v2.tauri.app/plugin/updater/
- `update-kit` explicitly models update as Detection -> Check -> Plan -> Apply, while `self-replace` exists because self-replace and self-uninstall remain platform-sharp, especially on Windows. Those are precisely the lane boundaries the archive should preserve instead of hiding inside crate-local APIs.
  https://docs.rs/update-kit/latest/update_kit/
  https://docs.rs/self-replace/latest/self_replace/
- The Cargo 1.90 development-cycle report says Rustup should only remove content it manages while Cargo and Rustup consider path transitions. That makes ownership and uninstall scope part of the same continuity story rather than an afterthought.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/

## The lane map

### Lane 1 — Source-installed tool lane (`cargo install` + `cargo-update`)
**What it is**
- An installed CLI or Cargo subcommand whose current state is rooted in `cargo install` metadata and source-build semantics.
- Update discovery and apply are usually performed by rerunning source builds or using a helper like `cargo install-update`.

**Why it matters**
- This is the clearest baseline update lane for Cargo-installed tools.
- It preserves rebuild semantics, `--locked` posture, install-root tracking, and configuration-discovery rules that other lanes do not share.

**What the archive should preserve**
- installed subject and install root,
- whether tracking files or `--no-track` posture existed,
- current version/source/build assumptions,
- check vs apply separation,
- and any imported install receipts or unknowns.

**What it should not pretend**
- that “latest on crates.io” equals what was installed,
- that check results equal apply results,
- or that all tool updates are source-build updates.

### Lane 2 — Prebuilt-binary reinstall lane (`cargo-binstall`, quickinstall, rerun install)
**What it is**
- A tool update flow that primarily refreshes an installed binary by selecting a prebuilt artifact and reinstalling it, sometimes falling back through quickinstall or `cargo install`.

**Why it matters**
- Candidate visibility, target matching, and fallback order are materially different from source-build lanes.
- Architecture mismatch or fallback-to-source outcomes can change what actually landed.

**What the archive should preserve**
- candidate artifact families considered,
- target/arch matching,
- fallback order,
- whether the final apply path was still prebuilt vs source-built,
- and any imported-lossiness when the result came from CI wrappers or shell history.

**What it should not pretend**
- that prebuilt and source-built updates are interchangeable,
- that a successful download proves the final applied binary,
- or that one chosen artifact describes the whole fallback lattice.

### Lane 3 — Receipt-driven updater lane (cargo-dist + `axoupdater`)
**What it is**
- An updater flow that starts from an existing install receipt and uses release-hosted metadata to decide whether an update is needed and how to apply it.

**Why it matters**
- Receipt presence, receipt schema/version, backend host family, and interrupted-install recovery are first-class facts here.
- This lane is closer to “managed application update” than to “rerun install.”

**What the archive should preserve**
- receipt identity and version,
- what installed subject the receipt claims,
- host/backend family,
- mirror/fallback posture,
- apply result and partial/interrupted residue,
- and rate-limit/auth caveats if they affect check semantics.

**What it should not pretend**
- that install receipts are universal,
- that release-hosted updater flows share Cargo-install semantics,
- or that receipt load success proves update apply success.

### Lane 4 — Bundle/app updater lane (Tauri-style application updates)
**What it is**
- An update flow for installed app bundles or installers whose semantics include bundle artifacts, signing, target matching, restart/exit behavior, and optional downgrade logic.

**Why it matters**
- This lane exposes product-facing lifecycle semantics that do not map cleanly onto CLI tool updates.
- Dynamic/static server behavior, custom targets, and before-exit hooks are all part of the public contract.

**What the archive should preserve**
- source kind (dynamic vs static update source),
- target matching/custom-target posture,
- comparator or downgrade policy,
- restart or before-exit hooks,
- and applied bundle/install mode on each platform.

**What it should not pretend**
- that app-bundle updates are just “download newer binary,”
- that server check rules equal apply rules,
- or that desktop-app and Cargo-tool update stories are one lane.

### Lane 5 — Delegated-manager lane (OS package manager, app store, externally owned updates)
**What it is**
- An installed subject whose update behavior is delegated to a package manager, app store, enterprise agent, or some other outside owner.

**Why it matters**
- Many Rust-built tools/apps eventually land here, and the absence of direct apply control is itself a continuity fact.
- The correct outcome is often a refusal/delegate plan rather than a direct apply attempt.

**What the archive should preserve**
- delegate/owner identity,
- what the current tool knows vs imports,
- explicit refusal/delegation plan,
- ownership boundary,
- and what uninstall or rollback facts remain unknown.

**What it should not pretend**
- that external ownership is a bug,
- that direct updater semantics still apply,
- or that the Rust-side tool may safely claim what the external manager eventually did.

### Lane 6 — Ownership / rollback / uninstall lane
**What it is**
- The lane where continuity claims stop being about “is there an update?” and become about what is owned, what can be reverted, what may be removed, and what residue remains.

**Why it matters**
- Cargo/Rustup path work and self-replace/self-delete behavior show that ownership and cleanup are not just tiny footnotes.
- Partial apply, downgrade, or uninstall mistakes can do more damage than a missed update.

**What the archive should preserve**
- managed vs co-located content,
- rollback eligibility and source,
- uninstall scope,
- cleanup policy,
- and any platform-sharp caveats.

**What it should not pretend**
- that “replace succeeded” implies “uninstall is safe,”
- that rollback is always available,
- or that path coincidence proves ownership.

### Lane 7 — Forensic/imported lane
**What it is**
- A reconstructed continuity story imported from logs, support tickets, CI, issue threads, or partial machine state instead of directly observed update operations.

**Why it matters**
- Real support and archaeology work often starts here.
- This lane is valuable only when lossiness remains explicit.

**What the archive should preserve**
- imported evidence sources,
- unknowns and contradictions,
- what was inferred vs observed,
- and which downstream consumers should treat the result as advisory only.

**What it should not pretend**
- that an imported story is as authoritative as direct capture,
- or that later reconstruction rewrites what was actually observed at the time.

## Key transitions the archive must keep explicit
1. **current installed subject ↔ candidate visibility**
   - what is installed is not the same truth as what updates were visible.
2. **check/plan ↔ apply**
   - deciding what should happen is not the same as what did happen.
3. **direct apply ↔ delegated apply**
   - external ownership changes what the Rust-side tool may claim.
4. **apply ↔ rollback/uninstall**
   - successful update does not prove cleanup, downgrade, or uninstall safety.
5. **direct capture ↔ imported forensics**
   - completeness and authority change, so downstream consumers must inherit explicit lossiness.

## What should change elsewhere in the archive
- **Update Continuity Kit** should remain the base artifact family, but it should now cite this lane map as the rule for what must stay separate.
- **Consumer Install Kit** should keep owning first-install subject/candidate/selection/receipt truth rather than silently absorbing later update events.
- **Distribution Contract Stack** should export install receipts and acquisition facts into Update Continuity without claiming the later lifecycle event.
- **Release Truth Stack** should export producer-side artifacts and updater material without pretending to know what an installed machine now contains.
- **Support Envelope**, **Policy**, and productization stacks should import bounded continuity facts instead of quietly narrating a hidden update model of their own.
- **Support/incident/archaeology consumers** should import the forensic lane with explicit uncertainty rather than retroactively inventing a cleaner update history than the evidence supports.
