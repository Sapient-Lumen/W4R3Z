# Design: Distribution Contract execution blueprint (2026 Q1)

## Goal
Turn the archive's consumer-side **delivery / acquisition / ownership** seam into a sharper **buildable program**.

The missing contribution is not another installer monopoly, another app-store dream, another release host, or another updater that silently claims ownership of everything in `~/.cargo/bin`.
It is a disciplined companion layer that makes Rust's **release import → route visibility → selection/fallback → verification → installed ownership → handoff** story reviewable across local machines, CI, mirrors, package-manager imports, support, and later assistant/editor consumers.

Read this note when the question is narrower than the broad ladder:

> if a serious Rust team wants to build the archive's consumer-side delivery contribution, what should that project actually ship in theory and practice?

Read with:
- `design/distribution-contract-2026Q1.md`
- `design/distribution-contract-stack.md`
- `design/distribution-contract-pilot-program.md`
- `design/consumer-install-kit.md`
- `design/consumer-lifecycle-continuity-bundle.md`
- `design/cargo-artifact-contract-execution-blueprint-2026Q1.md`
- `proposals/epic-distribution-contract-stack.md`

## Why this note is needed now
The archive already knew that **Distribution Contract** mattered.
What it still lacked was a crisper answer to **what the missing contribution should look like**.

Fresh ecosystem signals sharpen that answer:
- Cargo's current install docs still say `cargo install` manages Cargo's local installed binary set, chooses an install root through local config and environment, supports crates.io / git / path / alternate registries, and ignores packaged `Cargo.lock` unless `--locked` is used.
  https://doc.rust-lang.org/cargo/commands/cargo-install.html
- Cargo's config docs say `install.root` writes executables under a chosen root and tracks installed executables with files like `.crates.toml` and `.crates2.json`, which makes installed-state ownership a first-class local fact instead of a side effect.
  https://doc.rust-lang.org/cargo/reference/config.html
- rustup's installation docs still say rustup installs into Cargo's `bin` directory by default, while its channel/toolchain docs keep channel/version/host selection explicit. That means delivery already includes policy-like route choice and shared-path consequences.
  https://rust-lang.github.io/rustup/installation/index.html
  https://rust-lang.github.io/rustup/concepts/channels.html
  https://rust-lang.github.io/rustup/concepts/toolchains.html
- The Cargo 1.86 development-cycle update still highlights `cargo install-update` as a plugin and says built-in installed-binary update support is still tracked separately, which means lifecycle continuity remains outside Cargo's canonical delivery boundary.
  https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- The Cargo 1.90 development-cycle update says Rustup should only remove content it manages in shared paths. That is direct evidence that install ownership and uninstall scope are not solved by path coincidence alone.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- `dist` / cargo-dist now explicitly separates build and distribute phases, emits machine-readable manifests, and in its 0.31.0 release added mirror-style fallback hosting plus work to reduce partial-install risk.
  https://github.com/axodotdev/cargo-dist
  https://github.com/axodotdev/cargo-dist/blob/main/CHANGELOG.md
- cargo-binstall is explicit that acquisition is a route/fallback problem: it searches releases and artifacts, may use a third-party artifact host, may fall back to alternate targets, and only finally falls back to `cargo install`.
  https://github.com/cargo-bins/cargo-binstall
- release-plz keeps producer-side release automation increasingly normal through `update`, `release-pr`, and `release`, which raises the value of a stable handoff between release truth and consumer delivery truth.
  https://release-plz.dev/docs/usage

Taken together, those signals say the archive should stop describing the delivery seam only as a stack.
It should describe a real contribution shape.

## Headline answer
If one serious team wants to build the archive's clearest consumer-side delivery contribution, the answer should now be:

> Build a **Distribution Contract layer** that imports upstream release and artifact truth, records visible delivery candidates and chosen routes, preserves verification and installed-ownership facts, and emits reviewable packs and handoffs for update, uninstall, support, incident, policy, and later assistant/editor consumers.

That answer is deliberately narrower than “solve installation and updates forever”.
It is also deliberately stronger than “wrap a few installers”.

## What this contribution should be in theory

### Core thesis
A distribution system becomes ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact delivery subject was requested;**
2. **what release or artifact truth was imported into delivery;**
3. **which route classes and concrete candidates were visible;**
4. **which route actually won, and why fallback or refusal happened;**
5. **what verification and ownership facts were established on the machine;**
6. **what downstream consumer may honestly conclude from the result.**

If a project still needs shell history, host pages, installer scripts, support transcripts, and local path archaeology to reconstruct that story, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable delivery review and ownership handoff**.

It should include:
- delivery-subject capture;
- imports from release and artifact packs;
- visible candidate catalogs and policy posture;
- selected-route and fallback truth;
- verification receipts;
- installed-ownership and managed-content claims;
- bounded handoffs to update/uninstall/support/policy consumers.

It should not become:
- a replacement package manager;
- a replacement rustup;
- a universal updater first;
- a release-host monopoly;
- or a hosted software catalog that outruns local machine truth.

### Separation rule
The contribution must preserve at least six distinct truth classes:
- **release-import truth** — what upstream release / artifact / signature / provenance material was attached;
- **route/catalog truth** — which route classes and concrete candidates were visible;
- **selection/fallback truth** — which path was preferred, chosen, refused, or used only as fallback;
- **verification truth** — what checks actually ran, passed, warned, failed, or were skipped;
- **installed-ownership truth** — what landed on disk and which tool claims to manage it;
- **consumer truth** — what update/uninstall/support/policy consumers may conclude, with what lossiness.

This is the largest theory/practice guardrail in the design.
Without it, every “install succeeded” summary becomes confidence soup.

### Shape rule
This contribution should begin as a **reference layer + report/pack command + adapter/acceptance corpus**.
That means:
- a **reference layer** for route classes, ownership vocabulary, and handoff semantics;
- a thin **command / pack layer** for collecting, diffing, and exporting distribution packs;
- and an **adapter/acceptance corpus** for source-build, prebuilt, mirror, delegated, and shared-path ownership lanes.

It should not begin as a service, central marketplace, or updater empire.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo distribution-contract subject`
- `cargo distribution-contract catalog`
- `cargo distribution-contract compose`
- `cargo distribution-contract verify`
- `cargo distribution-contract own`
- `cargo distribution-contract diff`
- `cargo distribution-contract handoff --to <update|uninstall|support|incident|policy|inventory|assistant>`
- `cargo distribution-contract pack`

The tool should **import** leaf install and release surfaces when available rather than replace them.

### Public artifact spine

#### Imported/internal families
- `release-pack/v0`
- `artifact-pack/v0`
- `install-pack/v0`
- `install-receipt/v0`
- `binpack/v0`
- `binverify-report/v0`
- `airgap-pack/v0`
- optional package-manager / delegated-install attachments

#### Public review families
- `distribution-subject/v0`
- `delivery-catalog-report/v0`
- `delivery-selection-report/v0`
- `delivery-verification-report/v0`
- `delivery-ownership-report/v0`
- `distribution-contract-brief/v0`
- `distribution-contract-pack/v0`
- `distribution-contract-diff/v0`
- `distribution-contract-handoff/v0`

### Minimum schema disciplines
Every public artifact should keep these fields first-class:
- **subject identity** — requested app/crate/version/channel/target/host, route policy, install root, and environment lane;
- **import posture** — which upstream release or artifact materials were attached, absent, canonical, lossy, or third-party;
- **catalog anchors** — route class, provider, host or mirror, candidate ordering, target matching, and delegated/provider class;
- **selection anchors** — preferred route, actual route, fallback reasons, refusal reasons, and divergence from policy;
- **verification anchors** — checksum/signature/attestation/build-from-source/lockfile or other checks, each with pass/warn/fail/skip posture;
- **ownership anchors** — paths mutated, manager identity, managed scope, co-located unmanaged content, and uninstall/update implications;
- **reason-coded conclusions** — installed / partial / delegated / unmanaged / inconclusive with explicit ambiguity;
- **consumer limits** — what update/uninstall/support/policy/assistant consumers may and may not claim.

### Commands and what they should emit

#### `cargo distribution-contract subject`
Purpose:
- capture one delivery subject;
- record requested artifact/app identity, desired channel/version/target, route policy, and install root posture;
- emit `distribution-subject/v0`.

Important rule:
- do not let one downloaded file name or one path mutation impersonate the requested delivery subject.

#### `cargo distribution-contract catalog`
Purpose:
- record which route classes and concrete candidates were visible;
- preserve target matching, channel ordering, mirror ordering, and delegated/imported routes;
- emit `delivery-catalog-report/v0`.

Important rule:
- “could have used” and “did use” must stay distinct.

#### `cargo distribution-contract compose`
Purpose:
- compose leaf install receipts plus upstream release/artifact imports into one reviewable record;
- emit `delivery-selection-report/v0` and `distribution-contract-pack/v0`.

Important rule:
- leaf install truth remains canonical for the leaf mutation event.

#### `cargo distribution-contract verify`
Purpose:
- attach verification outcomes and skipped checks;
- emit `delivery-verification-report/v0`.

Important rule:
- artifact existence, signature availability, and local verification are different facts and must not collapse.

#### `cargo distribution-contract own`
Purpose:
- record what the acquiring tool claims to own and what remains merely co-located;
- emit `delivery-ownership-report/v0`.

Important rule:
- shared path is not shared ownership.

#### `cargo distribution-contract diff`
Purpose:
- compare two packs while preserving the distinction between:
  - changed release imports,
  - changed visible routes,
  - changed selected route or fallback behavior,
  - changed verification posture,
  - and changed ownership / consumer conclusions.

#### `cargo distribution-contract handoff`
Purpose:
- emit smaller update/uninstall/support/incident/policy/assistant slices without making those slices canonical by themselves.

## Ranked feature set

### P0 — required for a worthy v0
- explicit delivery-subject capture;
- imports from release and artifact truth rather than host-page scraping alone;
- at least one **source-build** route and one **prebuilt** route;
- selected-route and refusal/fallback reasons;
- verification statuses with `pass` / `warn` / `fail` / `skip` posture;
- installed-ownership summaries with managed vs unmanaged distinction;
- one portable brief plus one portable pack;
- lossiness-visible exports for support or update consumers.

### P1 — strong near-term extensions
- mirror and multi-host fallback posture;
- rustup/cargo shared-path ownership contrast;
- delegated package-manager or install-script imports;
- artifact-contract attachments for exact final-output identity;
- update/uninstall planning handoffs;
- restricted-network imports from `airgap-pack/v0`.

### P2 — do later or fold elsewhere
- hosted software catalog portals;
- one-click universal updater UX;
- package-manager replacement ambitions;
- central telemetry or download-scoring empires;
- support dashboards that outrun the underlying pack.

## Pilot lanes that best prove the idea

### 1) `cargo install` source-build lane
Prove:
- that source-build acquisition can preserve requested subject, lockfile posture, install-root posture, and managed-content truth without pretending it was a prebuilt download.

### 2) cargo-binstall prebuilt/fallback lane
Prove:
- that visible candidate ordering, prebuilt preference, alternate-target use, third-party-host use, and `cargo install` fallback can all remain reviewable.

### 3) cargo-dist mirror / installer lane
Prove:
- that producer-side build/distribute truth, machine-readable manifests, mirror ordering, and partial-install caveats can be imported without becoming the canonical local machine record.

### 4) rustup + Cargo shared-path ownership lane
Prove:
- that shared bin paths do not imply shared uninstall/update authority and that ownership must remain explicit.

### 5) bounded consumer handoff lane
Prove:
- that update/uninstall/support/incident/policy consumers can import bounded delivery truth instead of reverse-engineering installs from logs and screenshots.

## What a strong v1 would unlock
A strong v1 would let the ecosystem say:
- “this machine got a prebuilt artifact from a mirror after the preferred host failed”; 
- “this install built from source and intentionally ignored packaged lock truth”; 
- “this updater may touch these files but not the rest of the shared path”; 
- and “this support summary is only a lossy slice of the canonical delivery pack”.

That is the real prize.
Not another installer.
A believable, reviewable delivery boundary.

## Wrong shapes to kill first
Kill these directions before they widen:
- the **one universal installer** fantasy;
- the **Rust app store** fantasy;
- the **binary-only worldview** that erases source builds;
- the **release page = install truth** mistake;
- the **same path = same owner** mistake;
- and the **support screenshot = canonical delivery record** mistake.
