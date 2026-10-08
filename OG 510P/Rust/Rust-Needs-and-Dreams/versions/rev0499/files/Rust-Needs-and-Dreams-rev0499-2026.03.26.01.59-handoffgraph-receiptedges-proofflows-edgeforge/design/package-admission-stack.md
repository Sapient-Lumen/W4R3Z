# Design: Package Admission Stack (Publish Set + Dependency Control + Public API + SBOM Evidence + Trust Signals + Policy)

## Goal
Treat **Publish Set Kit**, **Dependency Control Stack**, **Public API Kit**, **SBOM Evidence Kit**, **Trust Signals Kit**, and **Policy Kit** as one shared **Package Admission Stack** for registry-facing package publication.

The missing contribution is **not** another advisory scanner, another crate score, another release GitHub Action, or another registry-only warning UI.
It is a portable, reviewable stack that keeps these truths distinct while letting them compose at the moment a package becomes durable ecosystem surface area:
- **publish-set truth** — which package(s) were selected, what payload was packaged, what checks were waived or passed, what authority/registry path was used, and what upload/index receipt existed;
- **graph-control truth** — what versions, sources, features, and publish-time / unification choices actually shaped the package review;
- **exposure truth** — what the package publicly exposes, which dependencies became part of that public contract, and what changed semantically;
- **inventory truth** — which components and scopes were present, how we know, and what export lossiness remains;
- **trust-signal truth** — what publisher, freshness, name-risk, audit/import, and scope facts were visible;
- **decision truth** — what policy rule set, waivers, and explicit decision report admitted or blocked the package;
- **handoff truth** — what was decided at package publication versus what still belongs to broader release, binary, support, or incident consumers.

That separation matters because the Rust ecosystem now has real supply-chain motion, but the decisive review boundary is still fragmented:
- Cargo can tell more about dependency choice and feature posture.
- Public/private dependencies make API exposure more explicit.
- SBOM precursor work makes package/build inventory more realistic.
- crates.io is publishing stronger trust-relevant signals.
- Cargo / crates.io publishing remains a durable act.
- Policy tooling still has to stitch all of that together from bespoke local glue.

## Why this seam matters now
Current official Rust/Cargo/crates.io signals are unusually aligned here:
- Rust’s 2026 flagship themes keep **Secure your supply chain** active, with milestones around stabilizing **public/private dependencies** and **SBOM support**.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The public/private dependencies goal exists specifically to help users catch accidental implementation-detail exposure and help tooling identify what constitutes an API.
  https://rust-lang.github.io/rust-project-goals/2025h1/pub-priv.html
- Cargo 1.94 still lists **stabilize public/private dependencies** as open work and keeps **Cargo SBOM Fragment** in planning, which is a strong sign that the package-admission boundary is still forming rather than settled.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo’s unstable feature surface now exposes `public-dependency` and `sbom`, which means package-admission-relevant facts are increasingly becoming explicit machine-facing seams.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo package` documents manifest normalization, packaged `Cargo.lock`, inclusion of `.cargo_vcs_info.json`, and an unstable machine-readable `--message-format json` for `--list`; it also says the VCS snapshot is only best-effort and not verified provenance.
  https://doc.rust-lang.org/cargo/commands/cargo-package.html
- `cargo publish` documents workspace-aware package selection, registry targeting, `--dry-run`, `--no-verify`, and polling for package appearance in the index.
  https://doc.rust-lang.org/cargo/commands/cargo-publish.html
- The 2025H2 `cargo-semver-checks` goal explicitly aims at integrating SemVer review into the `cargo publish` workflow, which means package admission increasingly depends on publish-time evidence and waivers rather than only preflight folklore.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- crates.io’s January 2026 development update added a Security tab, stronger Trusted Publishing controls, blocked risky GitHub triggers, and the `pubtime` field in the index, which means the registry itself is surfacing more admission-relevant facts.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo publishing is durable and the Cargo Book explicitly recommends thinking about the full release process rather than treating `cargo publish` as a bare upload step.
  https://doc.rust-lang.org/cargo/reference/publishing.html

Taken together, these signals say ideal Rust needs a **package-admission execution layer** above publish-set facts and other raw evidence, but below broader release/distribution orchestration.

## What each layer owns
### Publish Set Kit
[`design/publish-set-kit.md`](./publish-set-kit.md) owns:
- selected publish subject truth, including workspace/default-member/package-selection posture;
- packaged payload truth, including normalized manifests and file listing behavior;
- package-level check / waiver truth around packaging and upload;
- authority-path and registry-path truth;
- upload and index receipt truth.

Its question is:
> what package set and packaged payload were actually under review for publication, and what publication-path facts are already known?

### Dependency Control Stack
[`design/dependency-control-stack.md`](./dependency-control-stack.md) owns:
- chosen versions, sources, overrides, and conflicts,
- feature / optional-dependency activation,
- unification posture,
- publish-time / upgrade / MSRV-sensitive selection posture,
- public/private boundary handoff inputs.

Its question is:
> given the selected publish subject, what dependency graph and activation posture did this package review actually admit?

### Public API Kit
[`design/public-api-kit.md`](./public-api-kit.md) owns:
- public surface export,
- declared-vs-inferred exposure drift,
- semver reason codes,
- witness-based compatibility evidence,
- MSRV verification for the API boundary.

Its question is:
> what public contract did this package publish, and how did it change?

### SBOM Evidence Kit
[`design/sbom-evidence-kit.md`](./sbom-evidence-kit.md) owns:
- inventory capture lanes,
- scope-aware component graphs,
- artifact linkage when available,
- format projections and lossiness,
- inventory diffs and attachment packs.

Its question is:
> what components were present, in what scope, and how do we know?

### Trust Signals Kit
[`design/trust-signals-kit.md`](./trust-signals-kit.md) owns:
- publisher / issuer posture,
- freshness / cooldown facts,
- build/proc-macro split-scope trust views,
- name-risk / typosquat / lifecycle / audit imports,
- explainable reports and trust packs.

Its question is:
> what credibility and risk-relevant signals were visible at admission time?

### Policy Kit
[`design/policy-kit.md`](./policy-kit.md) owns:
- rule catalogs,
- waivers,
- explainable decisions,
- `INCONCLUSIVE` posture,
- diffs across admission decisions.

Its question is:
> given the imported evidence, what decision did we actually make, under which rules and waivers?

## What the stack should make possible
A reviewer should be able to answer all of these from one linked package-admission bundle, without reconstructing the story from terminal logs, raw SBOM XML, ad hoc CI, and registry folklore:
1. Which package set and packaged payload were actually under admission review?
2. Which graph and features did those package(s) actually publish against?
3. Which dependencies became part of the public contract, intentionally or accidentally?
4. Which components and scopes are inventoried, and which parts are inferred or lossy?
5. Which publisher / freshness / name-risk / audit signals were visible at decision time?
6. Which rules and waivers admitted or blocked the package?
7. Which claims end at package publication, and which still require later release / binary / support / incident evidence?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## What the stack should export
A serious package-admission layer should not stop at “we ran five tools.”
It should be able to emit a small family of reviewable artifacts:
- `package-subject/v0` — which crate/package/version/registry/publish posture is under review, imported from or linked to `publish-pack/v0`;
- `package-graph-report/v0` — chosen versions, sources, features, public/private posture, and lock or publish-time notes;
- `package-exposure-report/v0` — imported public-API evidence and declared-vs-inferred exposure drift;
- `package-admission-brief/v0` — the linked human-review bundle connecting graph, exposure, inventory, trust, and policy evidence;
- `package-release-handoff/v0` — the bounded statement of what later release/distribution layers still need to prove;
- `package-admission-pack/v0` — the checksummed bundle or pointer set linking the above artifacts and their imported attachments.

That artifact family is intentionally small.
The goal is not to invent a second registry schema.
The goal is to make package admission portable enough that Cargo-adjacent tools, registries, policy engines, downstream packagers, and assistants can all talk about the same admitted package without silently changing the subject.

## Execution documents
Treat this design note, [`design/package-admission-pilot-program.md`](./package-admission-pilot-program.md), and [`proposals/epic-package-admission-stack.md`](../proposals/epic-package-admission-stack.md) as one execution band.
This file defines the boundary, the pilot program defines rollout order, and the epic proposal defines what a worthy ecosystem contribution would look like in product form.

## Stack boundary relative to Release Truth
This stack must stay clearly distinct from the broader **Release Truth Stack**.

Package admission is about:
- the `.crate` package and registry-facing act,
- attached API / inventory / trust / policy evidence,
- and the decision to admit or hold that package.

Release truth is broader:
- binary artifacts,
- installers,
- signatures,
- provenance,
- rebuild evidence,
- mirrors,
- and multi-channel distribution.

The package-admission stack should feed release truth later, but it must **not** silently pretend that a reviewed package upload settles binary-install, signed-release, support-envelope, or incident-response truth.

## Recommended execution posture
The stack now needs a shared execution layer, captured in:
- [`design/package-admission-pilot-program.md`](./package-admission-pilot-program.md)

That pilot program should prove the stack in the following order:
1. **single-crate publish-review gate**
2. **workspace publish-group lane**
3. **proc-macro / build-lane admission lane**
4. **package-to-release handoff lane**
5. **thin registry / downstream consumer lane**

That ordering is intentional.
The archive should not jump straight to a universal registry score, giant package-risk dashboard, or one monopoly `cargo publish` replacement.
It should first prove that ordinary Rust packages can carry enough structured admission evidence to make publish decisions reviewable and reusable.

## Design principles
1. **Imported facts before verdicts.** Graph, exposure, inventory, and trust signals should be portable before they are judged.
2. **Package scope before release sprawl.** Keep registry package admission distinct from binary release and installer truth.
3. **Public contract and dependency graph are related but not identical.** Public API and dependency control must compose without collapsing into one surface.
4. **Trust is not policy.** Trust reports feed policy; they do not silently become the verdict layer.
5. **Inventory is not exposure.** A package can contain more than it publicly exposes; a public dependency can matter more than a merely present private one.
6. **Waivers stay visible.** The point is to make overrides reviewable, not impossible.
7. **Thin consumers later.** Registry views, downstream review UIs, and assistant summaries should be consumers of the stack, not alternate sources of truth.

## What an epic contribution would look like in practice
A serious contribution here would:
- reuse Cargo-native graph, feature, public/private, and SBOM seams rather than forking them;
- let maintainers attach API / inventory / trust / policy evidence to publish review without custom CI archaeology;
- give crates.io-facing or downstream tools a stable import boundary instead of bespoke rescans;
- make proc-macro/build-lane risk and cooldown posture explicit early rather than after an incident;
- and preserve honest package-to-release handoffs so later binary or installer truth can compose cleanly.

## Anti-goals
Do not turn this stack into:
- one fake crate-trust number,
- one universal “safe to publish” badge,
- one registry moderation replacement,
- one cargo-vet clone,
- one release-orchestration umbrella that swallows binary/signature/rebuild truth,
- or one giant supply-chain dashboard that hides package-level uncertainty.

The stack is a **review boundary**, not a replacement ecosystem bureaucracy.
