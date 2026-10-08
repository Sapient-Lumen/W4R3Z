# Design: Portfolio Reference Specimens (2026 Q1)

## Goal
Turn the archive's shared-grammar and consumer-routing ideas into a **small, reviewable specimen corpus**.

The repo now has strong cross-cutting notes for:
- artifact conventions;
- execution sequencing;
- proposal triage;
- pilot evaluation;
- evidence renewal;
- and consumer routing.

What it still lacked was one practical answer to a narrower but important question:

> if the archive already knows what honest packs, briefs, diffs, verify receipts, and lineage receipts should *mean*, what tiny corpus should future tools, validators, and LLM edits look at so they stop re-inventing those shapes from scratch?

This note answers **reference specimens / conformance examples**, not frontier promotion.

Read with:
- `design/portfolio-artifact-conventions-2026Q1.md`
- `design/portfolio-consumer-routing-2026Q1.md`
- `design/portfolio-evidence-renewal-2026Q1.md`
- `design/portfolio-pilot-evaluation-2026Q1.md`
- `meta/SPECIMEN_CORPUS_PROTOCOL.md`
- `specimens/README.md`

## Why this note is needed now
Fresh Rust signals keep pushing toward more machine-usable surfaces, but they also keep reminding us that those surfaces evolve.
That is exactly when a specimen corpus becomes more valuable than another prose-only guideline.

- Rust's March 2026 challenges writeup says the ecosystem tax is often **choice paralysis** and **tacit knowledge**, not merely lack of crates.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2025 State of Rust survey says online docs remain canonical while editor/LLM-mediated learning is rising.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo's plumbing goal says Cargo is still too porcelain-oriented for many advanced workflows.
  https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- Cargo's build-analysis goal is explicitly about recorded build metadata, review commands, and external tooling.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Cargo's January 2026 development-cycle note says structured logging and schema unification across Cargo outputs are active work.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The libtest JSON goal exists because people had come to rely on programmatic output.
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- docs.rs now hosts rustdoc JSON directly, but warns that `format_version` matters and that historical coverage is incomplete.
  https://docs.rs/about/rustdoc-json
- crates.io keeps widening route/trust signals through Trusted Publishing controls and newer security posture.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/

Taken together, those signals say the repo should not stop at “have a shared grammar”.
It should also maintain a **small concrete corpus** that teaches humans and tools what that grammar looks like when it is honest.

## Headline answer
The right answer is **not** a giant golden-data empire.
It is a tiny, deliberately maintained **reference-specimen corpus**.

In plain terms:

> keep seam payloads specific, but publish a handful of minimal examples that show the shared envelope, partiality posture, routing limits, verify posture, and lineage discipline across the strongest seams.

That corpus should be:
- **small** enough to maintain by hand;
- **diverse** enough to cover canonical pack, routed brief, diff, verify receipt, and lineage receipt;
- **explicitly partial** where the seam would be partial in real life;
- and **versioned** enough to survive schema drift without pretending nothing changed.

## What the specimen corpus should prove
A good specimen corpus should prove five things at once.

### 1) Shared grammar is real, not implied
The archive already says serious seams should share outer honesty fields.
A specimen corpus proves that claim concretely.

Every specimen should make the shared spine visible:
- `schema_family`
- `specimen_role`
- `seam`
- `subject`
- `scope`
- `authority`
- `freshness`
- `partiality`
- `imports`
- `attachments`
- `lineage`
- `handoff`

The specimen corpus should *not* force identical payload sections across seams.
It should only prove the common envelope and honesty posture.

### 2) Consumer routing is testable
The repo now has routing theory.
Specimens let future maintainers test whether a brief is still visibly weaker than the canonical pack.

A good routed-brief specimen should show:
- what truths were preserved;
- what was intentionally omitted;
- which decisions the brief is allowed to drive;
- and when the consumer must escalate back to the canonical pack.

### 3) Partiality and refusal are first-class
Specimens should not be all-happy-path examples.
At least some should demonstrate:
- stale or format-sensitive imports;
- unsupported checks;
- fallback-only states;
- manual-review-required posture;
- and inconclusive comparisons.

This matters because most archive drift happens when examples silently assume success.

### 4) Lineage survives summarization
The repo already says derivations are children, not overwrites.
A lineage specimen should show that a routed view or verify receipt still points back to:
- original imports;
- canonical pack identity;
- derived child identity;
- and compatibility posture.

That is especially important for LLM-facing or CI-facing consumers.

### 5) Compatibility review has something concrete to inspect
When envelope fields, routing rules, or verify posture change, a specimen corpus gives maintainers something to diff other than prose.
This is the real reason to create it now.

## What should be in the first corpus
The first corpus should stay small and centered on the archive's strongest portfolio answer.

### Required first specimens
1. **Build-State canonical pack specimen**
   - proves the broad one-project winner's envelope.
2. **Semantic Context canonical pack specimen**
   - proves the hidden multiplier's envelope and parser/freshness caveats.
3. **Build-State diff specimen**
   - proves that comparisons preserve changed authority, changed coverage, and changed outcomes.
4. **Migration/Public API verify receipt specimen**
   - proves that stronger claims are attached as bounded receipts, not smuggled into the pack body.
5. **Package Intake routed brief specimen**
   - proves lossiness budgets and escalation posture for operational consumers.
6. **Generic lineage receipt specimen**
   - proves import/derive/export ancestry for future validators, CI, and assistants.

That is enough to teach the family resemblance without pretending the whole repo has already converged.

## What a worthy contribution would look like in theory
If someone were building the archive's cross-cutting glue for real, the worthy contribution would look like:

1. a **tiny specimen corpus** across the strongest seams;
2. a **conformance linter** that checks required honesty fields and forbidden silent lossiness;
3. a **compatibility review rule** that says when envelope or routing changes require specimen refresh;
4. a **consumer-routing check** that fails if a routed brief claims stronger authority than the canonical pack permits;
5. and a **human-readable README** that lets maintainers, reviewers, and assistants learn the grammar from a dozen files instead of a thousand paragraphs.

That is buildable.
It is also more honest than skipping straight to a mega-schema or giant fixture registry.

## What it should look like in practice
A practical first implementation should create a directory like:
- `specimens/portfolio-envelope-v0/`

That directory should contain:
- one short README;
- a handful of JSON examples;
- stable specimen names;
- and a protocol naming when to widen, refresh, or replace specimens.

The specimens should be:
- **illustrative**, not executable source of truth;
- **thin**, not full production dumps;
- **reviewable in diff form**;
- and **mirrored into the archive copy** just like other canonical files.

## Non-goals
This note is **not** asking for:
- a universal schema empire;
- thousands of golden files;
- frozen never-changing output shapes;
- or a fake promise that one validator can own every seam payload.

The goal is much smaller:
**teach and guard the shared honesty grammar with a tiny corpus that can actually be kept current.**

## Recommended archive move
Treat this as a **deepening + hygiene** addition.
Do **not** promote a new frontier.
Do **not** change the broad ladder.

Instead:
- keep **Build-State Evidence** as the strongest one-project answer overall;
- keep **Native Edge Contract** as the active specialist frontier;
- keep **Adoption Navigation Contract** as the strongest anti-tacit-knowledge answer;
- keep **Package Intake Gateway** as the most underappreciated operational seam;
- keep **Semantic Context Contract** as the hidden multiplier;
- and add one canonical answer for **what minimal specimen corpus future tools and LLM edits should follow when they need concrete examples of honest packs, briefs, diffs, verify receipts, and lineage receipts**.

## Immediate repo consequence
The repo should now maintain:
- `design/portfolio-reference-specimens-2026Q1.md`
- `meta/SPECIMEN_CORPUS_PROTOCOL.md`
- `specimens/README.md`
- and the first `specimens/portfolio-envelope-v0/*.example.json` files

as the canonical answer for **what shared examples should exist before we trust future validators, assistants, or glue tooling to “just know” the archive's artifact grammar**.
