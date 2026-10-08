# Design: Compile Guidance Pilot Program (`cargo guidance pilot`, `guidance-pilot-pack/v0`)

## Goal
Make the **Compile Guidance Kit** real by starting with a ranked, reviewable pilot program instead of trying to standardize every future compile-time UX or compiler-extension surface at once.

The archive already argues that developer-facing compile-time guidance deserves first-class artifacts. The missing execution layer is now more practical:
- which guidance surfaces should go first,
- which of them already have stable enough ids or examples to export cleanly,
- how to keep user-facing guidance distinct from hook authority and extension power,
- and which consumers justify the work immediately.

A worthy contribution here is not another proc-macro helper, lint pack, or compile-fail snapshot harness.
It is a disciplined rollout plan that proves Rust can publish **portable guidance truth** for a few high-value lanes before widening the schema surface.

## References (signals)
- Rust’s vision work explicitly recommends doubling down on extensibility and says crates need better diagnostics and guidance plus the ability to integrate at more stages of compilation.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The 2025 State of Rust survey says online documentation remains the canonical reference while editor/agentic tooling is rising. That strengthens the need for explicit, machine-usable guidance surfaces instead of screenshots, folklore, or private editor state.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Stable Rust now includes `#[diagnostic::do_not_recommend]`, and the Reference documents both `#[diagnostic::on_unimplemented]` and `#[diagnostic::do_not_recommend]` as real language-supported guidance hooks.
  https://doc.rust-lang.org/beta/releases.html
  https://doc.rust-lang.org/reference/attributes/diagnostics.html
- The 2026 flagships explicitly include establishing safety-critical lints in Clippy, which raises the importance of reviewable lint surfaces and their governance posture.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- StableMIR publication is explicitly about enabling external analysis and tooling without depending directly on compiler internals.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- Cargo experimentation with multiple build scripts / delegated build steps is evidence that extension-hook structure is becoming more explicit, not less.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- `trybuild` is direct proof that compile-fail guidance is already treated as a testable product surface in the ecosystem.
  https://docs.rs/trybuild

## Why this needs its own design layer
The Compile Guidance Kit already defines the base artifact family: guidance surface, diagnostic catalog, lint catalog, hook profile, example catalog, check report, and pack.

What it did **not** yet answer clearly enough is:
- which guidance lanes deserve to be standardized first,
- where Rust already has stable ids or conventions versus where only examples exist,
- which consumer classes should drive the design first,
- how hook-authority truth should be imported without being collapsed into user-facing guidance,
- and when a guidance pilot should be considered successful.

Without that layer, compile-guidance work risks two bad outcomes:
1. **catalog drift without adoption** — lots of ids and manifests, little real checking or consumption;
2. **snapshot theater** — teams publish stderr files or screenshots, but nothing becomes portable enough for CI, docs, or editor consumers to reuse.

## Design principles
1. **Pilot guidance surfaces, not “supportiveness” in the abstract.** Start from concrete guidance loops with known hooks, ids, or golden examples.
2. **Prefer surfaces with existing written semantics.** If the language, reference docs, or widespread tooling already define the lane, standardization has a better chance.
3. **Keep guidance separate from hook authority.** Capability and determinism truth should be imported from compile-time authority layers, not flattened into wording catalogs.
4. **Examples count as evidence, not embarrassment.** Compile-fail and UI examples are first-class artifacts, not temporary scaffolding to be hidden later.
5. **Consumers must be explicit.** A pilot is stronger when it clearly serves crate docs, CI, editor overlays, safety reviewers, or migration tooling.
6. **Do not overclaim wording stability.** Stable ids, best-effort wording, span expectations, and example-only contracts must remain distinct.
7. **Graduation requires a real consumer.** A pilot is not successful just because it exports JSON; something downstream has to use it.

## Artifact family
### 1. `guidance-pilot-brief/v0`
Why this guidance lane is being piloted.

Should record:
- pilot id and summary
- guidance family (`trait-diagnostic`, `proc-macro-ui`, `lint-catalog`, `hook-profile`, `editor/ci-consumer`)
- why the lane matters now
- why it is tractable now
- intended consumers and action paths

### 2. `guidance-stability-profile/v0`
The expected stability posture for one pilot.

Should record:
- stable ids or prefixes when they exist
- wording promises (`stable-id`, `best-effort-wording`, `example-only`, `internal`)
- span / help / fix-it expectations
- normalization rules for examples
- what may drift without constituting a compatibility break

Design rule: **do not smuggle stability promises into prose**.
If the pilot depends on them, make them artifacts.

### 3. `guidance-consumer-profile/v0`
The downstream consumer map for a pilot.

Should record:
- who can consume the result (`crate-docs`, `ci`, `editor`, `safety-review`, `migration-tool`, `policy-tool`)
- whether the consumer needs ids, examples, fix posture, hook profile, or all of them
- which facts are canonical versus derived renderings
- whether the consumer is human-only, tool-only, or mixed

Design rule: **guidance without a consumer is only metadata**.
The pilot should show how exported guidance can improve a real workflow.

### 4. `guidance-pilot-scorecard/v0`
Decides whether the pilot works.

Should ask:
- did the pilot preserve the difference between ids, wording, examples, and hooks honestly?
- did it produce a reusable export/check path, not just one hand-written example?
- did a real consumer use it?
- did it avoid turning hook authority into a hidden footnote?
- did it make guidance drift easier to see intentionally?
- does widening the pilot still look justified?

### 5. `guidance-pilot-pack/v0`
Bundle for review and reuse:
- pilot brief
- stability profile
- consumer profile
- associated guidance artifacts
- current scorecard
- references and rendered summaries

## Ranked first pilots

### 1) Trait-diagnostic pilot
**Why first**
- Rust already has language-supported diagnostic attributes and documented semantics for them.
- This is the clearest existing lane where crate-authored guidance is becoming first-class.
- It proves the kit can model stable ids and bounded wording promises without requiring custom compiler extensions.

**Core artifacts**
- `guidance-surface`
- `diagnostic-catalog`
- `guidance-stability-profile`
- `guidance-check-report`
- `guidance-pilot-scorecard`

**Primary consumers**
- crate docs and crate maintainers
- CI checking for accidental guidance drift
- editor/doc overlays that want stable ids and help links

### 2) Proc-macro UI / compile-fail pilot
**Why second**
- Proc-macros are one of the places where Rust most needs better supportive interfaces.
- `trybuild` already proves compile-fail examples are a real workflow.
- This pilot shows how example catalogs can become portable without pretending proc-macro wording is always perfectly stable.

**Core artifacts**
- `guidance-example-catalog`
- `diagnostic-catalog`
- `guidance-stability-profile`
- `guidance-check-report`
- imported `pipeline-hook-profile`

**Primary consumers**
- macro maintainers
- CI and release review
- future editor or docs renderers for macro DSL guidance

### 3) Lint-catalog pilot
**Why third**
- The 2026 flagships explicitly strengthen the case for safety-critical lints in Clippy.
- This pilot proves the kit can represent lint identity, grouping, profile posture, and standards mappings without collapsing everything into one severity scalar.
- It is also a strong place to test governance-oriented consumers.

**Core artifacts**
- `lint-catalog`
- `guidance-surface`
- `guidance-consumer-profile`
- `guidance-check-report`
- `guidance-pilot-scorecard`

**Primary consumers**
- CI and policy tooling
- safety or migration reviewers
- editor integrations that need lint-family metadata

### 4) Hook-profile pilot (build / delegated-build / StableMIR-based analyzer)
**Why fourth**
- Rust’s vision work and Cargo experimentation both say deeper compilation-workflow integration matters.
- This pilot proves guidance can point to honest hook posture instead of treating extension machinery as magic.
- It is the best place to show how hook truth should be imported, not duplicated.

**Core artifacts**
- `pipeline-hook-profile`
- imported capability/determinism facts where available
- `guidance-consumer-profile`
- `guidance-check-report`
- `guidance-pilot-scorecard`

**Primary consumers**
- CI and review tooling
- caching / governance discussions
- advanced-domain users evaluating extension assumptions

### 5) CI / editor consumption pilot
**Why fifth**
- The survey says docs remain canonical while editor/agentic tooling is rising.
- This pilot proves the pack can be consumed outside the originating crate without turning generated overlays into the source of truth.
- It keeps the archive honest about consumer boundaries.

**Core artifacts**
- `guidance-pack`
- `guidance-consumer-profile`
- rendered export examples for CI and editor use
- `guidance-pilot-scorecard`

**Primary consumers**
- editors and IDEs
- CI/reporting surfaces
- docs sites that want to surface stable guidance ids and examples

## What should wait
Do **not** start with a universal compiler-extension manifest, a single global lint registry, or a one-size-fits-all severity standard.
Those are downstream views at best, and they would pressure the kit toward flattening diagnostics, examples, lints, and hook authority before the artifact boundaries are proven.

Also avoid pretending every proc-macro or analyzer hook must publish stable wording promises immediately.
The point of the first pilots is to prove shared structure where Rust already has enough semantics to be honest.

## Success bar
A compile-guidance pilot should be considered successful when it can show all of the following:
1. a guidance lane with stable-enough semantics to export honestly;
2. at least one rerunnable export/check path;
3. a declared stability profile for ids, wording, and examples;
4. a consumer profile showing who uses the output;
5. at least one real downstream consumer (docs, CI, editor, policy, or review tooling);
6. no hidden collapse of hook authority into “guidance works”.

## Why this is an ecosystem contribution
Rust’s current signals are unusually aligned: official vision work is calling for better supportive guidance from crates and deeper workflow integration, diagnostic attributes are now partly stable reality, safety-critical lint work is on the roadmap, compile-fail testing is already mainstream practice, and tool-facing consumers are multiplying.

That makes compile guidance no longer just a library-author nicety. It is becoming an **ecosystem substrate** problem: how to turn supportive compile-time behavior into bounded, portable truth that docs, CI, editors, and reviewers can consume without scraping stderr or reading macro internals.

A good Compile Guidance Pilot Program would be a strong “ideal Rust meets practical Rust” contribution because it would scale one of Rust’s biggest strengths — supportive tooling — beyond rustc proper.
