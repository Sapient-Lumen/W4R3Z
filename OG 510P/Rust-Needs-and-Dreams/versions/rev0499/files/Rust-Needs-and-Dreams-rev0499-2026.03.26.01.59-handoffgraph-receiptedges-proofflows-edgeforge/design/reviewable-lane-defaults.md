## Current note (rev0379)
After rev0378 made default cards real, the next missing layer became explicit:
**default evidence and renewal receipts**.

Read this note now together with:
- `design/lane-default-evidence-bundle.md`
- `design/lane-default-evidence-pilot-program.md`

The layer sequence is therefore now:
- Atlas candidate space
- reviewable lane defaults
- maintained default cards / corpus
- evidence bundle + renewal judgment
- project-specific brief
- onramp/bootstrap/overlay consumers

# Design note: Reviewable Lane Defaults

## Goal
Define the reusable layer that sits between **Atlas candidate space** and **one-off adoption briefs**.

The archive already has strong notes for:
- mapping possible lanes (`design/ecosystem-atlas-kit.md`),
- choosing a lane for one project (`design/adoption-decision-stack.md`),
- keeping recommendation authority honest (`design/recommendation-posture-ladder.md`),
- routing a learner/team into a first path (`design/profiled-onramp-stack.md`), and
- turning a decision into a starter repo and environment (`design/project-bootstrap-stack.md`).

What it still lacked was the explicit reusable layer for:
> “for this recurring project class and risk posture, what is the default Rust lane we are prepared to recommend right now, with alternatives, freshness, and bounded handoffs?”

This note exists so future revisions do not keep recomputing the same recommendation from scratch or, worse, let one project-specific brief silently harden into an ecosystem blessing.

After the archive promoted **Adoption Navigation Bundle** as the repo's ecosystem-navigation composition point, this file becomes the next concrete execution seam beneath it: the reusable-default layer between candidate space and one-off project briefs.

## Read with
- `design/ecosystem-atlas-kit.md`
- `design/adoption-navigation-bundle.md`
- `design/adoption-decision-stack.md`
- `design/recommendation-posture-ladder.md`
- `design/profiled-onramp-stack.md`
- `design/project-bootstrap-stack.md`
- `design/package-admission-stack.md`
- `design/canonical-learning-stack.md`

## Why this seam matters now
Fresh official Rust signals keep describing the same gap from different angles:
- Rust’s December 2025 vision work says users need help navigating crates.io, says there is no clear place to get advice on a good “starter set” of crates, and says simple blessing is politically risky.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- Rust’s March 20, 2026 challenges writeup says ecosystem navigation still depends too much on tacit knowledge and explicitly calls out choice paralysis.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while editor/LLM-mediated workflows are rising. That makes fuzzy recommendation authority more dangerous and makes machine-usable defaults more valuable.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- crates.io now exposes materially richer inputs for recommendation refresh and review: Security-tab advisories, Trusted Publishing posture, SLOC, and `pubtime`.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Cargo continues to say that Cargo cannot be everything to everyone and that plugins matter, which argues for a companion control-plane layer instead of forcing Cargo itself to become the full recommendation engine.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

Taken together, these signals suggest the next worthy contribution is not a global top-crates page, but a **scoped, reviewable default layer** that can be renewed, diffed, and handed off.

## The missing seam
Today Rust guidance often jumps between three states:
1. **candidate-space only** — a map of respectable lanes, but no concrete default;
2. **one-off recommendation** — a project-specific answer that is too narrow to reuse;
3. **accidental blessing** — one answer gets repeated enough that it starts masquerading as universal truth.

What is missing is a reusable middle layer:
- stronger than a candidate list,
- more reusable than one adoption brief,
- weaker and more honest than an ecosystem-wide blessing,
- and explicit enough to hand off into onramp, bootstrap, and package-admission flows.

## Stack claim
A worthy contribution here is a **Reviewable Lane Defaults** layer: a thin control-plane surface that publishes **scoped default lanes** for recurring project classes without pretending those defaults are universal.

It should operationalize the recommendation ladder like this:
- Atlas candidate sets and lane maps remain the source of possible answers.
- Reviewable lane defaults publish one reusable scoped default for a named project class.
- Adoption briefs specialize or override that default for one concrete project.
- Profiled onramps and bootstrap flows consume the chosen default and hand it off downstream.

This keeps “good reusable default here” distinct from both “mere shortlist” and “ecosystem blessing everywhere”.

## Boundary map
### 0) Adoption Navigation Bundle
Owned by the Adoption Navigation Bundle.

It answers:
- what the current project question is;
- which candidate lanes and canonical references are in scope for that question;
- which imported evidence and local-fit checks shaped the brief.

It may **import** a reusable scoped default when the project matches one, but it should not blur the default into the project-specific brief.

### 1) Atlas candidate space
Owned by the Ecosystem Atlas.

It answers:
- which serious lanes exist,
- which slots matter,
- which alternatives are respectable,
- and which common-ground seams are relevant.

It should not be forced to emit a reusable default every time.

### 2) Reviewable lane default
Owned by this layer.

It answers:
- for a named project class, what lane is the reusable starting default;
- which alternatives remain first-class;
- what assumptions about risk posture, team maturity, runtime family, support horizon, and ecosystem maturity are baked in;
- what freshness/renewal budget applies;
- and what downstream handoffs this default is allowed to trigger.

It should not claim to settle one concrete project forever.

### 3) Project-specific adoption brief
Owned by Adoption Decision.

It answers:
- whether the scoped default still fits this specific project;
- what local constraints override it;
- which alternatives moved up or down;
- and what local codebase or org overlays change the answer.

It should import a reusable default when one exists, not rewrite ecosystem folklore from scratch.

### 4) First-route and first-repo handoff
Owned by Profiled Onramp and Project Bootstrap.

They answer:
- what a matching learner/team should read first;
- what starter family should be realized;
- what local environment is expected;
- and what downstream package/support/release imports become active.

They should consume the scoped default, not quietly replace it.

### 5) Shared-common-ground and local-overlay boundaries
Owned elsewhere.

Interop Commons owns **neutral shared common ground**.
Atlas overlays / org policy own **local institutional defaults**.
Reviewable lane defaults should not counterfeit either one.

## Artifact family
This layer only needs a compact artifact family:
- `lane-default-scope/v0` — project class, domain, runtime family, support/risk posture, team-maturity assumptions, and explicit non-goals
- `lane-default-card/v0` — the chosen reusable default lane, serious alternatives, why this lane is default *here*, and when to escalate to a project-specific review
- `lane-slot-defaults/v0` — selected slot families, allowed alternates, coupling notes, and optional-vs-required boundaries
- `lane-default-evidence/v0` — imported atlas / trust / maintenance / docs / support / build-state inputs plus date/version scope
- `lane-default-freshness/v0` — renewal interval, invalidation triggers, and required checks to renew the default
- `lane-default-handoff/v0` — what Profiled Onramp, Project Bootstrap, Package Admission, and local overlays may import from this default
- `lane-default-pack/v0` — compact bundle for review, rendering, and diffing

Design rule: these are **reusable default artifacts**, not yet another general atlas or a hidden recommendation model.

## What a worthy contribution would look like in practice
A credible contribution would look like:
- `cargo lane list`
- `cargo lane explain <scope>`
- `cargo lane check <scope>`
- `cargo lane diff <scope>`
- `cargo lane handoff <scope>`
- `cargo lane pack <scope>`

or an equivalent companion tool that stays visibly above Cargo rather than pretending to be Cargo canon.

## Required scope axes
A scoped default should name at least most of these axes explicitly:
- **project class** — CLI, service, library, embedded component, internal platform component, script/automation, etc.
- **runtime family** — sync, async, browser/Wasm, embedded/no-std, etc.
- **risk/support posture** — conservative, regulated, experimental, fast-moving internal, long-horizon support, etc.
- **team maturity** — Rust-new, mixed-experience, Rust-native, domain-expert-but-Rust-new, etc.
- **environment posture** — local-first, CI-heavy, containerized, hermetic-ish, workstation-heavy, etc.
- **override threshold** — what facts should trigger a project-specific adoption review instead of simply using the reusable default.

Without those axes, a “lane default” is too easy to over-read.

## Positive properties
The contribution is worthy when it:
1. reduces repeated recommendation work for common project classes;
2. keeps the scope of each default visible and reviewable;
3. preserves credible alternatives instead of hiding them;
4. makes freshness and expiration part of the contract;
5. gives onramp/bootstrap tooling a durable handoff target;
6. stays thin enough to wrap atlas evidence instead of replacing it;
7. helps humans and assistants consume the same default pack without changing its authority.

## Ranked first execution lanes
### 1. Conservative internal CLI / automation tool
Best first lane because choice pressure is real, but runtime and platform complexity are still controlled.

### 2. Conservative HTTP/service baseline
Good second lane because it forces runtime, settings, observability, and package-admission consequences to stay visible.

### 3. Existing multi-language workspace / monorepo component
High leverage because many teams are not choosing Rust for a greenfield repo; they are choosing a Rust lane inside a larger existing system.

### 4. Script / tiny utility / repro lane
Important now because `cargo script` is becoming more real, and small proofs are often where teams first experience Rust default choices.

### 5. Safety-tilted or regulated conservative lane
Strategically important, but should follow once the reusable-default machinery is proven on less institution-heavy ground.

## Non-goals
- one global blessed-crates list;
- a hidden scoring model that emits defaults without review;
- replacing Atlas with a second curation system;
- replacing project-specific adoption briefs with generic defaults;
- collapsing scoped defaults into starter templates or into local policy overlays.

## Failure modes to resist
- **Atlas capture:** acting as if a reusable default pack is the same thing as the whole candidate space.
- **Brief capture:** letting one project-specific adoption brief silently become the reusable public default.
- **Template capture:** treating starter repos as the source of lane truth instead of downstream realizations.
- **Authority drift:** forgetting whether a claim is scoped default, shared common ground, or local institutional overlay.
- **Freshness theater:** publishing a reusable default with no renewal budget.

## Practical archive consequence
This seam should now sit between **Recommendation Posture Ladder / Atlas / Adoption Decision** and **Profiled Onramp / Project Bootstrap**.

In other words: the next worthy contribution is probably **not** another atlas, recommendation site, or starter template. It is a thin, reviewable `cargo lane` / `lane-default-pack/v0` layer that makes reusable scoped defaults possible without pretending Rust has finally solved crate guidance once and for all.

That makes this file the most practical follow-on to `design/adoption-navigation-bundle.md`: once the bundle exists, the next step is to prove the reusable-default layer it can import.
