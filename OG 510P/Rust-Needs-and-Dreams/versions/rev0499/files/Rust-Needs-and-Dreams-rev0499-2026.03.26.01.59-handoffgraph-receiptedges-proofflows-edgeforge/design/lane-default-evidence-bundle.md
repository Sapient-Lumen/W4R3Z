## Current note (rev0380)
The evidence bundle is now instantiated as a first readable receipt corpus under `evidence/` and modeled explicitly in `design/lane-default-renewal-receipts.md`.

That means the bundle should now be interpreted as:
- evidence classes in principle,
- plus current receipts in practice,
- plus later diff/index/schema work only after the receipt workflow feels normal.

# Design: Lane Default Evidence Bundle

## Goal
Turn the lane-default corpus from a set of good cards into a set of **renewable, reviewable claims**.

The archive now has:
- `design/reviewable-lane-defaults.md` for the layer;
- `design/lane-default-evaluation-framework.md` for the rubric;
- `design/reviewable-lane-defaults-corpus.md` for the corpus discipline; and
- `defaults/` for actual default cards.

What it still lacked was the explicit **evidence bundle** that makes a default defensible without re-running the whole research project by hand.

This note defines that missing layer.
It sits beneath the corpus and above the underlying signal sources.

Read with:
- `design/reviewable-lane-defaults.md`
- `design/lane-default-evaluation-framework.md`
- `design/reviewable-lane-defaults-corpus.md`
- `design/adoption-navigation-bundle.md`
- `design/package-admission-stack.md`
- `design/maintenance-reality-stack.md`
- `design/compatibility-claims-stack.md`
- `meta/LANE_DEFAULT_CORPUS_PROTOCOL.md`

## Why this seam matters now
Fresh official Rust and Cargo signals now make the missing layer obvious:
- Rust’s March 20, 2026 challenges post says ecosystem navigation depends too much on **choice paralysis** and **tacit knowledge**, and that domain maturity is uneven.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while LLM/tool-mediated learning and agentic editors are rising.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- crates.io’s January 2026 update added more reviewable signals: Security tab, Trusted Publishing only mode, SLOC, source links, and `pubtime`.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- The crates.io malicious-crate notification-policy update says blog-post churn is often **noise rather than signal**, while RustSec advisories remain the durable notification lane.
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Cargo’s unstable/reference surface now exposes useful temporal and supply-chain inputs such as `public-dependency`, SBOM precursor files, and `--publish-time` lockfile generation.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- The `cargo-semver-checks` merge path makes explicit that API-compatibility evidence is becoming part of Cargo’s publication story rather than an external afterthought.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- The safety-critical Rust writeup says higher-assurance users need reusable dependency-lifecycle patterns, safety-case-friendly async expectations, and auditable interop boundaries.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The maintainer-fund and maintenance posts say maintenance is continuous “keep the lights on” work rather than a one-time delivery event, so a renewable default needs maintenance posture imports instead of popularity vibes.
  https://blog.rust-lang.org/inside-rust/2026/01/12/what-is-maintenance-anyway/

Taken together, these signals say the next worthy move is not a larger corpus alone.
It is a thin **lane-evidence bundle** so default cards can cite canon, registry evidence, compatibility/API evidence, support-envelope reality, and freshness posture in one portable package.

## The missing problem
Right now, the archive can publish a respectable default card, but renewal still risks looking like:
- re-reading official posts,
- sampling crates.io / docs.rs manually,
- remembering past decisions from lore,
- and rewriting a justification paragraph from scratch.

That is not good enough for a maintained public corpus.

If the archive wants defaults that assistants, platform teams, and humans can all import without laundering opinion into authority, it needs an explicit evidence layer.

## Bundle members
### 1) Canon import
Owns the maintainer-authored or official sources that explain the lane itself.
This includes project docs, guides, books, and official Cargo/Rust docs.

Question:
> what canon should a reviewer read first before trusting any derived recommendation?

### 2) Registry / supply-chain import
Owns the package-level evidence that should be checked when a lane names external crates:
- Security-tab advisories;
- Trusted Publishing posture;
- source links;
- SLOC / rough size cues;
- version timing / `pubtime`;
- and any relevant malicious-package or policy signals.

Question:
> what public registry evidence should affect whether this lane remains publishable as a default?

### 3) API / compatibility import
Owns evidence about what a package promises and whether it can evolve safely:
- public/private dependency posture;
- semver-check posture;
- SBOM precursor or inventory export capability when relevant;
- and compatibility/support-envelope facts when the lane depends on specific targets or ABIs.

Question:
> what public API and compatibility evidence matters for trusting this lane over time?

### 4) Maintenance / stewardship import
Owns maintenance reality that should not be guessed from popularity:
- explicit maintenance/support notes;
- observed stewardship posture when available;
- succession/fund/support facts when material;
- and visible evidence that the lane is still being carried responsibly.

Question:
> is the default leaning on living infrastructure or on a gradually abandoned success story?

### 5) Support-envelope import
Owns platform/runtime/target/host expectations:
- runtime lock-in;
- target assumptions;
- documented support boundaries;
- FFI/ABI boundary constraints;
- debugging or operations caveats;
- and any safety-tilted or regulated evidence requirements.

Question:
> where does this default actually hold, and where does it over-claim?

### 6) Freshness / replay import
Owns the time dimension:
- when the evidence was checked;
- whether temporal replay inputs exist (`pubtime`, `--publish-time`, lockfile posture);
- what changed since the last renewal;
- and when the lane should be re-reviewed.

Question:
> is this default current, stale, or only temporarily acceptable?

## Core artifact family
### 1. `lane-evidence-query/v0`
The bounded question being asked:
- project class or default-card subject
- target risk/support posture
- review date
- review owner
- explicit scope and non-goals

### 2. `canon-import-set/v0`
The maintainer-authored reading surface:
- primary docs/guides/books
- official Cargo/Rust references
- derived-vs-canonical markers
- stale/reference warnings

### 3. `registry-evidence-report/v0`
Registry and supply-chain inputs:
- advisories
- publishing posture
- source/docs reachability
- size and timing signals
- unresolved signal gaps

### 4. `api-compat-report/v0`
Public API and dependency posture:
- public/private dependency facts
- semver-check posture
- SBOM/inventory capability notes
- compatibility/support claims where relevant

### 5. `support-envelope-report/v0`
Target/runtime/boundary facts:
- supported target and host assumptions
- runtime or framework lock-in
- FFI / interop posture
- operational caveats
- explicit unsupported zones

### 6. `maintenance-import-brief/v0`
Maintainer/stewardship posture:
- declared support/lifecycle notes
- obvious maintenance reality signals
- escalation to support-routing or continuity stacks when needed
- explicit unknowns

### 7. `lane-renewal-brief/v0`
The judgment for the default card:
- keep
- narrow
- demote to project-specific only
- replace
- or add as new card

### 8. `lane-evidence-diff/v0`
What changed since the previous review:
- canon drift
- registry drift
- API/support drift
- maintenance drift
- final recommendation drift

### 9. `lane-evidence-pack/v0`
The attachable bundle linking all of the above.

## Reference UX
A thin companion tool could expose:
- `cargo lane-evidence canon <scope>`
- `cargo lane-evidence registry <scope>`
- `cargo lane-evidence api <scope>`
- `cargo lane-evidence support <scope>`
- `cargo lane-evidence maintenance <scope>`
- `cargo lane-evidence renew <scope>`
- `cargo lane-evidence diff <scope>`
- `cargo lane-evidence pack <scope>`

The point is not to own every signal source.
The point is to make default renewal attachable and reviewable.

## Theory of change
The crucial move is to keep these truths separate:
- what canon says;
- what the registry and supply-chain surfaces say;
- what compatibility and API evidence says;
- what maintenance and support posture say;
- what the time dimension says;
- and what the default card is therefore allowed to claim.

Without that separation, the corpus will drift into one of four failures:
1. **prose-only defaults** that cannot be renewed safely;
2. **crate-score theater** that hides real tradeoffs;
3. **assistant-only authority** where the bundle cannot be audited; or
4. **org-local overlays** that silently become ecosystem guidance.

## First execution lanes
Rank the first proof points as:
1. renew `defaults/conservative-internal-cli-2026Q1.md` using an explicit evidence bundle;
2. renew `defaults/conservative-http-service-2026Q1.md` with support-envelope and registry imports visible;
3. add `defaults/script-repro-tiny-utility-2026Q1.md` because cargo-script has strong official momentum and a naturally bounded scope;
4. only then attempt a public **safety-tilted** default, because that lane needs stronger evidence imports than the first three.

## MVP boundary
A worthy MVP should prove exactly five things:
1. import canon without turning derived commentary into the source of truth;
2. import registry signals without pretending they are a final verdict;
3. import support/compatibility facts without flattening them into generic badges;
4. emit a renewal judgment that explains what changed;
5. make a future assistant or platform team able to quote the same evidence pack instead of re-inventing the answer.

## Non-goals
Do **not** turn this into:
- a universal crate leaderboard;
- an opaque recommendation score;
- a permanent central curation bureaucracy;
- a replacement for package admission, maintenance reality, or compatibility claims;
- or an always-on crawler that pretends freshness can be inferred without human review.

## Why this is a worthy contribution
This is worthy because it attacks the real bottleneck after the corpus exists:
**renewal discipline**.

A good default card is helpful once.
A renewable default card with a portable evidence pack becomes infrastructure.
