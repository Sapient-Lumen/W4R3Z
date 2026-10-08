# Design note: Institutional Overlay Stack (local defaults without pretending they are public truth)

## Goal
Define the missing **local-execution layer** between reusable public Rust guidance and the concrete defaults an organization, team, product line, regulated environment, or long-lived project actually wants to enforce.

This note is not a new atlas, not a new starter-template catalog, and not a secret policy engine.
It is the thin layer that says:
- which **public defaults or common ground** we import,
- which **local deltas or constraints** we add,
- which **bootstrap / environment / package-admission** consequences those deltas trigger,
- and how those local answers stay **reviewable, renewable, and visibly local**.

## This note composes with
- [`design/recommendation-posture-ladder.md`](./recommendation-posture-ladder.md)
- [`design/reviewable-lane-defaults.md`](./reviewable-lane-defaults.md)
- [`design/project-bootstrap-stack.md`](./project-bootstrap-stack.md)
- [`design/profiled-onramp-stack.md`](./profiled-onramp-stack.md)
- [`design/workspace-environment-stack.md`](./workspace-environment-stack.md)
- [`design/package-admission-stack.md`](./package-admission-stack.md)
- [`design/policy-kit.md`](./policy-kit.md)
- [`design/starter-pack-kit.md`](./starter-pack-kit.md)

## Why this seam matters now
Fresh official Rust signals keep describing the same pressure from different sides:
- Rust’s December 2025 vision work says users need better help navigating crates.io and do not have a clear place to get advice on a good “starter set” of crates, but also says simple blessing is politically risky.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- Rust’s March 20, 2026 challenges writeup says ecosystem navigation still depends too much on tacit knowledge and explicitly calls out choice paralysis.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while editor/LLM-mediated workflows are rising, which makes fuzzy local recommendation authority more dangerous and makes machine-usable local guidance more valuable.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo’s configuration model is hierarchical and merges settings from the current directory upward, while rustup overrides and `rust-toolchain.toml` already make local toolchain posture explicit. That means local environment truth is real, but still fragmented.
  https://doc.rust-lang.org/cargo/reference/config.html
  https://rust-lang.github.io/rustup/overrides.html
- Cargo 1.94 is actively discussing workspace/configuration discovery because broken parent manifests or `.cargo/config.toml` files can poison unrelated builds. That is a strong signal that “local defaults” need clearer subject boundaries than inherited folklore.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- crates.io now exposes richer inputs like Security-tab advisories, Trusted Publishing posture, SLOC, and `pubtime`, which means local policy overlays can increasingly import explicit evidence instead of relying on static allowlists and tribal memory.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- The Rust Foundation’s 2026–2028 strategy keeps Stable Infrastructure, Sustainable Maintenance, and Adoption & Innovation together, which is another signal that durable local adoption patterns matter and should not be left as undocumented private glue.
  https://rustfoundation.org/strategic-plan/

Taken together, these signals suggest that ideal Rust still needs one more control-plane seam: **an explicit local-overlay layer** that can stay local without forking or corrupting public guidance.

## The missing seam
Today Rust teams often bounce between four bad states:
1. **public candidate space only** — respectable lanes exist, but no local answer is written down;
2. **private starter/template fork** — local policy and environment reality get buried in generated repos;
3. **wiki / tribal-memory overlay** — the “real defaults” live in tickets, chat history, and oral tradition;
4. **accidental public blessing** — one local default starts leaking outward and masquerading as general Rust truth.

What is missing is a reusable middle layer:
- stronger than an unwritten local norm,
- weaker and more honest than a public ecosystem blessing,
- more reviewable than a template fork,
- and explicit enough to hand off into adoption, learning, bootstrap, workenv, and package-admission flows.

## Stack claim
A worthy contribution here is an **Institutional Overlay Stack**: a thin control-plane surface that publishes **local deltas over shared Rust defaults** without pretending those deltas are universal.

Its job is to say:
- which public lane default or common-ground import we start from;
- which local restrictions, promotions, substitutions, waivers, runtime assumptions, package-admission rules, or learning routes we add;
- which local constraints are actually evidence-backed versus merely temporary;
- and which downstream consumers may import the overlay.

This keeps **public default**, **local overlay**, and **one-off project decision** visibly separate.

## Boundary map
### 1) Public candidate space and reusable defaults
Owned by Atlas, Recommendation Posture, and Reviewable Lane Defaults.

They answer:
- which lanes are respectable,
- which lane is a reusable default for a named project class,
- which alternatives remain first-class,
- and what evidence/freshness supports that answer.

They should not silently encode one company’s registry policy, audit requirements, CI substrate, or support envelope.

### 2) Institutional overlay
Owned by this layer.

It answers:
- which shared public default(s) we import;
- what local delta we apply;
- whether that delta is about policy, environment, support horizon, runtime family, package-admission posture, or pedagogy;
- who owns the overlay;
- and when the overlay expires or must be renewed.

It should not pretend to settle one concrete project forever.

### 3) Project-specific adoption brief
Owned by Adoption Decision.

It answers:
- whether the local overlay still fits this exact project;
- what project-specific facts override both the public default and the local overlay;
- and whether the project is an exception, an upgrade candidate, or an out-of-scope case.

It should import overlays rather than rediscovering the institution’s local folklore from scratch.

### 4) Bootstrap, workspace environment, and package admission
Owned by Project Bootstrap, Starter Pack, Workspace Environment, and Package Admission.

They answer:
- what repo and starter shape is realized;
- what toolchain/config/native/service/credential posture is expected;
- and what publish/dependency/trust/policy gates are active.

They should consume the overlay, not quietly replace it or backfill its missing governance.

### 5) Profiled onramp and local learning/support routes
Owned by Profiled Onramp and Canonical Learning consumers.

They answer:
- what local training path or concept translation should be presented first;
- what local support contacts, examples, or docs sets are relevant;
- and how a Rust-new contributor inside this institution should begin.

They should consume the overlay, not become the authority source themselves.

## Artifact family
This layer should stay compact. A credible family would be:
- `overlay-subject/v0` — institution/team/product-line identity, scope, audience, and explicit non-goals
- `overlay-imports/v0` — referenced public defaults, common-ground packs, starter/workenv/admission inputs, and local-only additions
- `overlay-delta/v0` — local restrictions, promotions, substitutions, waivers, required slots, forbidden lanes, and override notes
- `overlay-governance/v0` — owners, approval path, review cadence, visibility, and exception process
- `overlay-freshness/v0` — upstream invalidation triggers, expiration budget, and required evidence to renew the overlay
- `overlay-handoff/v0` — what Adoption Decision, Profiled Onramp, Project Bootstrap, Workspace Environment, Package Admission, and Policy consumers may import
- `overlay-pack/v0` — the compact bundle for review, diffing, and distribution

Design rule: these are **local deltas over shared artifacts**, not a second hidden atlas and not a second policy engine.

## What a worthy contribution would look like in practice
A credible contribution would look like:
- `cargo overlay list`
- `cargo overlay explain <scope>`
- `cargo overlay check <scope>`
- `cargo overlay diff <scope>`
- `cargo overlay handoff <scope>`
- `cargo overlay pack <scope>`

or an equivalent companion layer that stays visibly above Cargo rather than pretending Cargo itself owns institutional policy.

The important part is not the CLI spelling.
The important part is that local defaults become:
- **import-based** instead of fork-based,
- **reviewable** instead of implicit,
- **renewable** instead of permanent folklore,
- and **bounded** instead of leaking into public Rust truth.

## Required overlay dimensions
A serious overlay should name at least most of these explicitly:
- **subject scope** — org, business unit, platform team, product line, regulated environment, foundation-maintained project, etc.
- **import base** — which public lane default, shared common ground, or starter/bootstrap/workenv input it modifies
- **constraint class** — policy, environment, package-admission, support, runtime, learning, release, or trust
- **authority/visibility** — public, partner-visible, internal, or restricted
- **override path** — what evidence is needed to deviate for one project
- **freshness budget** — cadence and invalidation triggers

Without those axes, a “local overlay” is too easy to over-read or to ignore.

## Positive properties
The contribution is worthy when it:
1. lets Rust keep public guidance thinner and more honest;
2. reduces template forks and wiki-only default drift;
3. gives institutions a bounded place to encode local policy and environment reality;
4. keeps local constraints visible enough for project exceptions and renewals;
5. gives bootstrap, workenv, and package-admission consumers a durable handoff target;
6. helps assistants/editors consume the same local overlay without inventing authority;
7. remains small enough to wrap shared public defaults rather than replace them.

## Ranked first execution lanes
### 1. Conservative internal CLI / automation overlay
Best first lane because many teams want repeatable internal-tool defaults, but the runtime and release surface stay manageable.

### 2. Conservative service / regulated-environment overlay
High leverage because it forces environment, package-admission, trust, runtime, and support deltas to stay explicit.

### 3. Existing monorepo / mixed-language component overlay
Important because many Rust adoptions are incremental and happen inside a larger pre-existing platform rather than in greenfield repos.

### 4. Rust-new team learning/onramp overlay
Useful because a local overlay is often not only package policy; it also changes what contributors should learn first and which examples/support routes they can trust.

### 5. Foundation/maintainer or long-support overlay
Strategically important because it exercises support horizon, maintenance reality, and package-admission imports without pretending every public project has the same institutional backing.

## Non-goals
- one universal org-policy schema that every team must adopt;
- a hidden internal recommendation score;
- a vault or secret-distribution system;
- a replacement for Cargo config, rustup overrides, Dev Containers, or Nix;
- another starter-template empire;
- or a way to turn one institution’s defaults into public Rust canon by repetition.

## Failure modes to resist
- **public-default capture:** letting one local overlay leak outward and masquerade as the public default;
- **template capture:** treating a starter repo or devcontainer as the overlay authority instead of a downstream realization;
- **policy bleed:** flattening package-admission or trust constraints into a supposedly neutral lane default;
- **secret dump:** turning overlay packs into serialized credentials or private infrastructure leaks;
- **fossilized fork:** never renewing the overlay when public defaults, registry signals, or toolchain reality change.

## Practical archive consequence
This seam should now sit at the top of the archive’s “local policy” band:
- **Recommendation Posture** defines that local overlays are a distinct authority level.
- **Reviewable Lane Defaults** define what shared reusable defaults can be imported.
- **Institutional Overlay Stack** defines how local deltas become explicit and renewable.
- **Adoption / Onramp / Bootstrap / Workenv / Package Admission** then consume those local overlays honestly.

In other words: the next worthy contribution is probably **not** another internal template collection or “best practices” wiki. It is a thin `cargo overlay` / `overlay-pack/v0` layer that lets local defaults stay local while still being reviewable, renewable, and composable with the rest of ideal Rust.
