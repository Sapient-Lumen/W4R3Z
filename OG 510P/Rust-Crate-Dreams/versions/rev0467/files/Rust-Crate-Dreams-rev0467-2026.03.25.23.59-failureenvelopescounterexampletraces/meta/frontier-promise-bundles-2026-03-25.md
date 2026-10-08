# Frontier promise bundles — 2026-03-25

This note sharpens the current frontier without changing its broad ranking.

The archive already knew that worthy crates should emit artifacts, survive drift, and export runnable operating models.
This pass adds the missing product lens:

**What compact promise bundle should a worthy crate hand another team?**

That sharper missing layer is the **promise bundle** (also describable as a support envelope).

## Definition

A promise bundle is the smallest honest combination of:

- repeated downstream question;
- imported official and local evidence surfaces;
- machine-readable packet family;
- human-readable offer summary;
- named support/service level;
- recheck trigger vocabulary;
- transition or escalation path;
- scenario corpus;
- and non-claim boundary.

Without that bundle, a crate may still produce useful data.
It is not yet a strong receiver-facing ecosystem contribution.

## Why this got stronger now

Because the official ecosystem is increasingly machine-usable:

- crates.io now surfaces Trusted Publishing posture, SLOC, and `pubtime`;
- docs.rs exposes build recipe facts, metadata knobs, downloadable archives, and rustdoc JSON;
- Cargo goal work keeps moving toward build analysis, build-dir units, semver checks, and clearer API-boundary tooling;
- StableMIR continues to strengthen the idea of stable tool-building substrate;
- verifiable mirroring and public/private dependency work both reinforce the need for honest support envelopes rather than hand-wavy trust stories.

The missing value is no longer only “collect more facts”.
It is “turn those facts into a compact promise another team can review, accept, and rerun later.”

## The current top lanes as promise bundles

### 1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
What it should provide other people:
- a receiver-scoped crate choice packet;
- comparison receipts tied to task and policy profile;
- a frozen decision summary;
- explicit follow-up triggers that reopen the choice.

First useful promise bundle:
- `task-profile.json`
- `candidate-import.json`
- `decision-pack.json`
- `decision-summary.md`
- `recheck-ticket.json`

Service level:
- **decision-ready recommendation under named evidence floor**.

Non-claim boundary:
- not universal “best crate” truth;
- not final certification of support across all targets or organizations.

### 2. **P-0536 Crate Knowledge Pack Kit**
What it should provide other people:
- a replayable witness basis behind a recommendation or support claim;
- target-aware citations and locator discipline;
- build/doc visibility caveats that survive handoff.

First useful promise bundle:
- `basis-lock.manifest.json`
- `citation-locator.json`
- `build-surface.report.json`
- `knowledge-summary.md`

Service level:
- **pinned witness bundle for later review and re-materialization**.

Non-claim boundary:
- not task-fit judgment by itself;
- not proof that hosted docs equal local or supported reality.

### 3. **P-0472 + P-0484 Docs/Target Support Envelope**
What it should provide other people:
- hosted-doc recipe truth;
- target/toolchain/component support ceilings;
- compact wording for “supported”, “builds”, “cross-compiled”, “documented”, and “unknown”.

First useful promise bundle:
- `docsrs-preflight.report.json`
- `hosted-local-diff.report.json`
- `target-support.report.json`
- `support-ceiling.note.md`

Service level:
- **support envelope grounded in build/doc/target reality**.

Non-claim boundary:
- not “works everywhere”;
- not policy approval;
- not debugger, certification, or runtime guarantees.

### 4. **minimal P-0535 Dependency Lifecycle Transition Kit**
What it should provide other people:
- a compact answer to what changed since the last frozen packet;
- a keep/pin/exception/migrate/replace route;
- a continuity story another maintainer can inherit.

First useful promise bundle:
- `trigger-intake.receipt.json`
- `decision-revalidation.report.json`
- `transition-plan.json`
- `continuity-summary.md`

Service level:
- **named recheck and transition posture after change**.

Non-claim boundary:
- not automatic maintenance correctness;
- not silent upgrades from “observed” to “approved”.

### 5. **P-0486 Debuggability Support Contract Kit**
What it should provide other people:
- debugger/OS/version/async support ceilings;
- known-good and known-bad debugging lanes;
- a compact statement of what support maintainers can actually offer.

First useful promise bundle:
- `debug-support.report.json`
- `debug-scenario.receipt.json`
- `debug-support-summary.md`

Service level:
- **bounded debugger support envelope**.

Non-claim boundary:
- not blanket “debuggable on platform X” wording without a corpus.

## Cross-domain reading

The broad domain scan still matters.
But it now matters mostly as a way to test whether the same bundle shape helps many receivers:

- web teams want crate-choice and support clarity, not another backend umbrella;
- GUI teams want visual-iteration and platform-support truth, not vague “GUI solved” claims;
- game teams want platform/build/tooling support envelopes;
- IDE/editor integrators want stable capability packets;
- geospatial teams want target/data-format and maintenance truth;
- local-first builders want sync/storage/offline claim ceilings;
- embedded and kernel teams want no-std / target / toolchain / std-rebuild truth;
- safety-critical teams want sharply bounded evidence and non-claim language.

That keeps the frontier mostly cross-cutting.

## Immediate build slice

The best next practical move is to materialize one compact offer stack:

1. **Pathfinder** produces a decision offer.
2. **Knowledge Pack** freezes the witness basis.
3. **Docs/target imports** define the support envelope.
4. **Lifecycle** reopens the offer on named triggers.
5. **Debug** layers on only after the prior four are honest.

## Worthiness rule

A proposed crate should not be called “epic” here unless it can hand another team:

- one compact promise bundle;
- one believable service level;
- one rerun path;
- one refusal boundary;
- and one scenario corpus that prevents support theater.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-semver-checks.html
- https://rust-lang.github.io/rust-project-goals/2025h2/pub-priv.html
- https://rust-lang.github.io/rust-project-goals/2025h1/verification-and-mirroring.html
- https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- https://rust-lang.github.io/rust-project-goals/2025h1/open-namespaces.html
