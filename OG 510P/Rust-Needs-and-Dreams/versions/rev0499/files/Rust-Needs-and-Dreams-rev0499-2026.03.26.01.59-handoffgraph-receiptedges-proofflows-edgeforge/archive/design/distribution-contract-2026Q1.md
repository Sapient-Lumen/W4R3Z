## Execution addendum (rev0444)
Read `design/distribution-contract-execution-blueprint-2026Q1.md` immediately after this note when the question is no longer only “does consumer-side delivery need a contract?” but “what should that contribution actually ship in theory and practice?”

Interpretation rule:
- this note still names the seam and its truth classes;
- the new blueprint now says more explicitly what the worthy contribution should look like as a buildable project;
- **Consumer Install Kit** remains the leaf install lane, **Cargo Artifact Contract** remains an upstream substrate, and **Update Continuity** remains downstream;
- and future revisions should keep release imports, route visibility, selection/fallback, verification, installed ownership, and consumer handoff separate before widening into installers, updaters, or software catalogs.

# Design: Distribution Contract (2026 Q1)

## Goal
Make Rust software delivery reviewable by standardizing one thin boundary for **release import**, **visible delivery routes**, **selection / fallback**, **verification posture**, **installed ownership**, and **downstream handoffs**.

This contract sits *between* producer-side release truth and later lifecycle continuity.
It is deliberately narrower than “solve installation and updates forever” and broader than “one installer receipt”.

## Why this is a frontier now
The current Rust delivery/tooling direction is no longer just “people can script their releases somehow”.
It is actively creating **multiple acquisition routes with distinct semantics** that downstream tools need to preserve instead of flattening:

- `cargo install` is explicit that installed binaries live in an install root, can come from crates.io / git / path / alternate registry sources, and ignore the packaged `Cargo.lock` by default unless `--locked` is used.
  - https://doc.rust-lang.org/cargo/commands/cargo-install.html
  - https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo’s 1.86 development-cycle report highlighted `cargo install-update` and said built-in installed-binary update support is still being tracked, which means consumer-side continuity is still outside Cargo proper.
  - https://blog.rust-lang.org/inside-rust/2025/02/27/this-development-cycle-in-cargo-1.86/
- Cargo’s 1.90 development-cycle report says rustup should only remove content it manages, because shared install paths can contain binaries that were never installed by rustup. That makes ownership and uninstall scope a first-class delivery fact instead of an afterthought.
  - https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- `cargo-dist` is now a serious release/distribution layer with explicit **Plan, Build, Host, Publish, Announce** phases, machine-readable manifests, installer/runtime configuration, mirror fallback, and work on reducing partial-installation risk.
  - https://github.com/axodotdev/cargo-dist
  - https://github.com/axodotdev/cargo-dist/releases
  - https://github.com/axodotdev/cargo-dist/blob/main/CHANGELOG.md
- `cargo-binstall` is now explicit that it searches release artifacts and falls back through multiple lanes before ultimately using `cargo install`, which proves that “install this Rust tool” is already a route-selection problem rather than one universal path.
  - https://github.com/cargo-bins/cargo-binstall
- `release-plz` makes release PRs, version bumps, changelog generation, registry publishing, tags, and release hosting more normal, which raises the value of a stable handoff between release automation and consumer delivery.
  - https://release-plz.dev/docs
- rustup’s own channel/install docs show that delivery already includes policy-like selection and fallback behavior for missing components rather than a single naïve “latest wins” rule.
  - https://rust-lang.github.io/rustup/concepts/channels.html
  - https://rust-lang.github.io/rustup/installation/index.html
- the 2025 State of Rust survey still says docs are the preferred canonical reference while editor/LLM mediation is rising, which increases the value of machine-readable delivery truth that support tools and assistants can import without inventing their own folklore.
  - https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Taken together, these changes say Rust is missing a durable boundary for answering:

- what release facts were imported into delivery;
- which routes and candidates were actually visible;
- why one route was selected or why fallback happened;
- what verification actually ran or was skipped;
- what was installed and who claims to own it afterward; and
- what later lifecycle/support/policy consumers may honestly import.

## Core thesis
A worthy contribution here is **not**:

- one monopoly installer,
- one Rust app store,
- one package-manager replacement,
- one binary-only worldview,
- or one “safe to install” badge that silently folds source builds, signatures, mirrors, and ownership into one verdict.

It is a contract that keeps six truths separate:

1. **release-import truth** — what producer-side release/signature/support evidence was attached;
2. **catalog / route truth** — which delivery candidates and route classes were visible;
3. **selection / fallback truth** — which route was chosen and why others were refused or only used as fallback;
4. **verification truth** — what checks passed, warned, failed, or were skipped during acquisition;
5. **installed-ownership truth** — what landed on disk and what manager/tool now claims it owns;
6. **consumer-handoff truth** — what update, uninstall, support, incident, and policy consumers may honestly import without distortion.

## Why this is distinct from nearby frontiers
### Not the same as Publisher & Source Identity Contract
**Publisher & Source Identity Contract** is upstream. It explains who may publish and what route/source identity is being claimed.
**Distribution Contract** begins when consumer-facing delivery candidates are visible and some acquisition path is selected.

### Not the same as Package Intake Gateway
**Package Intake Gateway** is about local extraction/staging/resolution/build/install authority once a package is admitted locally.
**Distribution Contract** is about consumer-facing route choice and ownership handoff across source builds, prebuilt artifacts, package-manager imports, installers, and mirrors.

### Not the same as Consumer Install Kit
**Consumer Install Kit** owns one leaf acquisition/mutation event.
**Distribution Contract** composes one or more leaf install receipts with release/signature/airgap imports and emits bounded downstream handoffs.

### Not the same as Update Continuity Kit
**Update Continuity Kit** owns later compare / plan / apply / rollback / uninstall continuity.
**Distribution Contract** stops at the initial delivery/acquisition boundary and the ownership it leaves behind.

## The contract layers
### 1) Release-import layer
This layer answers:
- which `release-pack`, signature/provenance pack, SBOM, support note, or host manifest was imported;
- which producer facts are attached versus absent;
- which imports are canonical versus lossy or third-party.

This layer must preserve that imported producer truth does **not** prove what the consumer installed.

### 2) Catalog / route layer
This layer answers:
- which route classes were visible: source build, prebuilt archive, installer, package-manager import, mirror, restricted-network source, delegated lane;
- what host/mirror/channel ordering existed;
- which target/platform matching facts applied.

This layer must preserve the difference between “could have used” and “did use”.

### 3) Selection / fallback layer
This layer answers:
- which candidate was selected;
- why fallback occurred or was refused;
- what policy shaped the choice (prebuilt-first, source-only, mirror-only, package-manager-only, exact-host preference, etc.);
- what divergence occurred between preferred and actual routes.

### 4) Verification layer
This layer answers:
- what verification was available;
- what actually ran;
- what succeeded, warned, failed, or was skipped;
- which checks were mandatory versus opportunistic.

This must preserve the difference between “artifact existed”, “artifact was signed”, and “this install verified that signature”.

### 5) Installed-ownership layer
This layer answers:
- what files/paths/binaries were mutated;
- which manager/tool claims ownership;
- what was co-located but unmanaged;
- what later uninstall/update flows are justified.

This is where Cargo/rustup shared-path ownership warnings matter.

### 6) Consumer handoff layer
This layer answers:
- what update/uninstall/support/incident/policy consumers may import;
- what lossiness remains;
- what changes should trigger review or archaeology.

## Proposed artifacts
### Core reports
- `delivery-import-report/v0`
- `delivery-catalog-report/v0`
- `delivery-selection-report/v0`
- `delivery-verification-report/v0`
- `delivery-ownership-report/v0`
- `distribution-contract-pack/v0`
- `distribution-contract-diff/v0`
- `distribution-contract-handoff/v0`

### CLI surfaces
These can start as external commands:
- `cargo distribution-contract compose`
- `cargo distribution-contract diff`
- `cargo distribution-contract handoff --to <consumer>`
- `cargo distribution-contract own`

## Ranked MVP shape
### 1. Compose one leaf install lane first
Import one real `install-pack/v0` or `install-receipt/v0` and keep leaf truth intact.

Why first: it proves that this seam is a composer/handoff layer rather than another installer.

### 2. Add route/fallback comparison second
Support side-by-side comparison of:
- source-build route,
- prebuilt route,
- mirror/host fallback route,
- package-manager or installer import lane.

Why second: route visibility is the main missing thing today.

### 3. Add ownership summaries third
Record manager identity, managed-content scope, and uninstall/update implications.

Why third: ownership is the part most likely to be silently guessed by downstream tools.

### 4. Restricted-network imports fourth
Import mirror/offline posture from `airgap-pack/v0` and preserve exact-copy versus divergent routes.

### 5. Bounded handoffs fifth
Only after the above lanes exist should the stack emit support/policy/incident/update-facing summaries.

## What the worthy contribution looks like in practice
In theory, this contribution gives the ecosystem a precise ontology for consumer delivery.
In practice, it should feel like this:

- a maintainer can answer “what route classes do we officially support for acquiring this tool?” without reading several installer READMEs;
- a support engineer can tell whether a user got a source build, a prebuilt artifact, a mirror fallback, or a delegated package-manager install;
- an update tool can import ownership and initial-route truth instead of re-guessing it from a path;
- an incident responder can diff delivery posture across hosts, mirrors, or versions;
- a policy tool can express “mirror-only”, “signed-prebuilt-only”, or “source-build-only” without becoming the installer itself.

## Strategic rank
This should be treated as the clearest next **delivery / acquisition / ownership-shaping** seam.
It belongs in the consumer-side corridor, but it is not the same thing as release automation, package identity, local package intake, or later lifecycle continuity.

Recommended placement in the ladders:
- below **Publisher & Source Identity Contract** and the broad build/debug/intake bands;
- above narrower product-lane defaults and public-lane overlays;
- explicitly adjacent to **Consumer Lifecycle Continuity Bundle**, **Consumer Install Kit**, and **Update Continuity Kit**.

## What not to build
Do not turn this into:
- a universal installer replacement,
- a universal self-updater,
- a hosted release portal that pretends to be the whole contract,
- a “signed means safe means owned” badge,
- or a one-command empire that hides route/fallback/ownership details.

The point is to make Rust software delivery **boringly legible**, not centrally controlled.
