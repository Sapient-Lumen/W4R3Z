## Addendum (rev0465)
For questions about **what the archive's shared spine should actually ship as a worthy stage-0 contribution**, read `design/shared-spine-execution-blueprint-2026Q1.md` after this note.

Interpretation rule:
- this note still owns the **common grammar in principle**;
- the new note owns the **concrete build shape, proving grounds, validator/fixture family, and brief-versus-assistant discipline**;
- and future revisions should now stop treating “shared spine” as a slogan once they are making build-level recommendations.

# Design: Portfolio Artifact Conventions (2026 Q1)

## Goal
Turn the archive's recurring phrase **"shared artifact conventions"** into a concrete, reviewable note.

The repo now has execution blueprints for:
- **Build-State Evidence**;
- **Semantic Context**;
- **Migration/Public API**;
- **Package Intake Gateway**;
- **Adoption Navigation**;
- **Native Edge**.

That is a strength, but it creates a new risk:
**six serious seams can still decay into six incompatible mini-languages.**

This note answers a narrower but now-important question:

> if the archive's strongest multi-project answer is a portfolio of reference layers rather than one mega-tool, what common grammar should those layers share in theory and practice?

Read with:
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/strategic-territory-map-2026Q1.md`
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `design/semantic-context-execution-blueprint-2026Q1.md`
- `design/migration-public-api-execution-blueprint-2026Q1.md`
- `design/package-intake-gateway-execution-blueprint-2026Q1.md`

## Why this note is needed now
Fresh official signals keep pointing in the same direction:
- Rust's March 2026 challenges writeup says the ecosystem tax is often **choice paralysis** and **tacit knowledge**, not just missing crates.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says online docs remain canonical while editor/LLM-mediated learning is rising, which raises the value of trustworthy machine-usable imports.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The Cargo plumbing goal says Cargo's machine-facing surface is still too porcelain-oriented, that `cargo metadata` excludes feature resolution, and that Cargo work naturally decomposes into explicit phases.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo's build-analysis work is explicitly prototyping recorded build metadata and `cargo report` review commands rather than only terminal output.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo's 1.93 development-cycle note says plugins matter, says structured logging is active work, and says schema unification across Cargo outputs could improve JSON output and unblock a faster `cargo fix` architecture.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The `cargo-semver-checks` goal says cross-crate items and precise type information are still blockers, while witness compilation is the concrete fallback for stronger claims.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- docs.rs now hosts rustdoc JSON directly, but warns that `format_version` matters and historical availability is incomplete.
  https://docs.rs/about/rustdoc-json
- The libtest JSON goal exists precisely because people rely on programmatic output and felt the loss when unstable JSON was restricted.
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- StableMIR / `rustc_public` work is explicitly about publishing a semver-governed compiler-facing interface for downstream tooling.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
  https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- crates.io now has richer machine-usable route and trust signals through Trusted Publishing improvements, Trusted-Publishing-only mode, and newer security/reporting posture.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/

Taken together, those signals say the archive should stop leaving the portfolio grammar implicit.
If Rust is moving toward more machine-usable evidence surfaces, then the repo needs an explicit answer for **how multiple worthy control planes should resemble one another without collapsing into one empire**.

## Headline answer
The right answer is **not** a universal schema platform.
It is a thin, repeatable **reference-layer grammar** shared across the archive's strongest seams.

In plain terms:

> keep each seam's payload specific, but make its envelope, truth classes, lineage rules, and handoff posture familiar across the portfolio.

That gives the ecosystem two things at once:
1. **local honesty** — each seam still models its real domain; and
2. **cross-seam composability** — downstream tools do not have to relearn six incompatible trust models.

## What should be shared in theory

### 1) Shared truth-class vocabulary
Every serious portfolio artifact should distinguish at least these classes:
- **subject truth** — what exact thing is under review;
- **import truth** — what external or first-party surfaces were imported;
- **derived truth** — what bounded interpretations or diagnoses were added;
- **partiality truth** — what is missing, stale, fallback-only, or lossy;
- **handoff truth** — what later consumers may honestly import.

This should remain stronger than ordinary “metadata”.
It is the anti-folklore core of the archive.

### 2) Shared envelope, not shared payload
The portfolio should standardize the **envelope fields**, not the domain payloads.

At minimum, public packs/briefs across the portfolio should converge on:
- `pack_kind` / `schema_family`
- `subject`
- `scope`
- `capture_epoch` or equivalent time anchor
- `authority`
- `freshness`
- `partiality`
- `imports`
- `attachments`
- `lineage`
- `handoff`

A build-state pack, semantic-context pack, package-intake pack, or migration/public-api pack should each keep different inner payloads.
What should feel the same is the outer review contract.

### 3) Shared verb family
The archive's strongest seams should prefer a narrow verb family where it genuinely fits:
- **capture / import** — gather or normalize subject truth;
- **explain** — render the same evidence at human depth;
- **diff** — compare two reviewed subjects without hiding changed authority or coverage;
- **verify** — attach bounded stronger checks or witness-backed proof;
- **doctor** — emit advice that never outruns evidence;
- **handoff / export** — produce consumer-specific slices that remain weaker than the canonical pack.

Not every seam needs every verb.
But the portfolio should stop inventing a completely different lifecycle for each seam unless the subject genuinely requires it.

### 4) Shared lineage discipline
The same pack must not silently gain stronger authority as it moves through tools, assistants, CI, or docs.
So the portfolio should standardize three lineage rules:
- **imports keep provenance** — first-party or raw imports remain named and attached;
- **derivations stay separate** — summaries, diagnoses, and assistant slices are children, not overwrites;
- **stronger claims require new receipts** — diff/verify/doctor conclusions must name their evidence basis and compatibility posture.

This matters especially because Cargo structured logging, rustdoc JSON, libtest JSON, and compiler-facing APIs are all still evolving.

### 5) Shared refusal posture
A serious review layer must be allowed to say:
- unsupported;
- partial;
- fallback-only;
- stale;
- inconclusive;
- manual-review-required.

The repo should prefer these explicit weaker outcomes over another “best effort” success blob.

## What should be shared in practice

### Common public artifact spine
Without replacing seam-specific packs, the portfolio should converge on a small shared outer spine:

#### A) Canonical pack
The seam's main review artifact.
Examples already exist implicitly in the repo:
- `build-state-evidence-pack/v0`
- semantic-context pack equivalents
- package-intake pack equivalents
- migration/public-api bridge pack equivalents

The new rule is not to rename them all.
The new rule is that each canonical pack should expose the same outer honesty fields.

#### B) Brief / handoff artifact
A smaller artifact for PR review, CI, support, or assistants.
It should always point back to the canonical pack and carry explicit lossiness.

#### C) Diff artifact
A comparison artifact that says:
- what subjects were compared;
- what authority or coverage changed;
- what actually differed;
- what could not be compared honestly.

#### D) Verify receipt
A bounded stronger-check artifact.
Examples:
- witness compilation for semver/public-api;
- stronger build diagnosis checks;
- native-boundary compile or link verification;
- package-intake extraction/route validation.

#### E) Lineage / execution receipt
The minimum answer to:
- which tool or importer ran;
- which inputs it consumed;
- which outputs it created;
- whether the result is import, explanation, diff, verify, doctor, or handoff.

This is the most important hygiene addition for the repo itself because it protects future LLM and assistant interactions from laundering derived summaries into canonical truth.

## What a worthy shared contribution would look like
If a serious lab built the archive's **portfolio glue**, the worthy contribution would look like this:

1. a tiny shared envelope spec;
2. a validator / linter that checks required honesty fields;
3. a lineage-receipt and handoff-brief convention;
4. a fixture corpus showing the same grammar across at least four seams;
5. a fail-closed compatibility rule for imports whose schema/toolchain basis materially changed.

That is enough to make the portfolio feel like one family without turning it into one product.

## Recommended rollout order

### Phase 1 — envelope alignment on the core portfolio
Apply the shared grammar first to:
1. **Build-State Evidence**
2. **Semantic Context**
3. **Migration/Public API**
4. **Package Intake Gateway**

Reason:
these are already the archive's strongest multi-project answer and have the highest reuse pressure.

### Phase 2 — consumer-facing consistency
Make sure each of those four can emit:
- canonical pack
- brief/handoff
- diff artifact
- verify receipt where appropriate
- lineage receipt

Reason:
this is where CI/docs/assistant consumers either become trustworthy or start hallucinating across seams.

### Phase 3 — widen to downstream/specialist consumers
Only after the core grammar is proven should the repo align:
- **Adoption Navigation**
- **Native Edge**
- selected canonical-learning / support / incident consumers

Reason:
those seams benefit from imported truth more than they need a brand-new envelope language.

## Anti-goals
This should **not** become:
- a universal mega-schema for all Rust tooling;
- a hosted evidence registry;
- a new Cargo control plane;
- a replacement for seam-specific artifact families;
- an excuse to flatten canonical imports and assistant summaries into one output format.

The point is disciplined resemblance, not centralization.

## Relationship to the portfolio ranking
This note does **not** change the broad ladder.
It does **not** promote a new frontier.
It does **not** outrank **Build-State Evidence**.

What it does do is make the archive's best **multi-project** answer much more buildable:

> strongest one-project answer = **Build-State Evidence**
> 
> strongest multi-project answer = **Build-State Evidence + Semantic Context + Migration/Public API + Package Intake**
> 
> strongest shared repo-level meta answer = **one thin reference-layer grammar across those seams**

That is a better funder and builder answer than “build four tools and hope they line up later.”

## Repo consequence
Treat this note as **deepening + hygiene**, not promotion.

Future revisions that touch multiple execution blueprints should keep these visibly separate:
- seam-specific subject semantics;
- common envelope fields;
- lineage / execution receipts;
- consumer-slice lossiness;
- and assistant-facing derived artifacts.

If a future revision cannot say what is shared and what is seam-specific, it is probably smearing the portfolio back into folklore.
