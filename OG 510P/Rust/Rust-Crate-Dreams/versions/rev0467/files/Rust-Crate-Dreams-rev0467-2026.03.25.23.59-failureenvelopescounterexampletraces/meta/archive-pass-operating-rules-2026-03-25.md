# Archive pass operating rules — 2026-03-25

This note is for future human and LLM passes over the archive.

The purpose is simple:
**future revisions should keep making the repo more buildable, not only more eloquent.**

## 1. Every pass must declare its mode

At the top of a new entry, say which of these is happening:

- **deepen** — make an existing proposal more buildable;
- **rerank** — change salience or build order;
- **append** — add new territory or a new proposal;
- **eliminate** — demote, merge, or kill a proposal;
- **hygiene** — improve archive memory, templates, or review discipline.

A pass may do more than one thing, but it must say which dominates.

## 2. Every pass must leave at least one practical artifact behind

A pass is weaker if it only adds narrative.
Prefer to leave at least one of:
- a product plan,
- a lane-boundary note,
- a schema,
- a scenario,
- a delivery card,
- a comparison matrix,
- a template,
- or an operating checklist.

## 3. Keep “need” separate from “buildability now”

Do not rank only by pain.
Do not rank only by convenience.
When a pass changes the frontier, ask:

1. Did the lane become more needed?
2. Did the lane become more buildable?
3. Which one changed, exactly?

## 4. Do not promote another umbrella just because a domain is important

Before promoting a new domain lane, ask:

- is the missing thing a **decision seam**?
- an **evidence/conformance seam**?
- a **transition seam**?
- a **support/debug/build truth seam**?
- a **boundary / interoperability seam**?

If the answer is still “the whole domain needs help”, that is not yet specific enough.

## 5. Force receiver value early

Before a proposal is treated as build-ready, be able to answer:

- who receives value?
- what recurring pain disappears?
- what concrete artifact do they receive?
- what is the first useful release?
- what does the crate refuse to do?

If the answer is vague, the lane is not ready for promotion.

## 6. Keep contrary evidence alive

Every pass should preserve at least one reason **not** to overclaim.
Examples:
- docs.rs is useful, but hosted docs are not the whole truth;
- security/advisory surfaces are useful, but they do not solve task fit;
- ecosystem maturity in a domain does not imply a new umbrella crate is missing;
- a runtime’s docs may still be weaker than a semantic contract would like.

## 7. Touch the repo’s memory spine when direction changes

If a pass materially changes build order, worthy-bar, or archive workflow, update:

- `README.md`
- `INDEX.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/archive-memory-anchor-2026-03-22.md`

If the pass changes how future archive work should behave, also touch:
- `meta/llm-hygiene.md`

## 8. Prefer “freezeable fronts” over endless watchlists

The archive is strongest when it can say:
- this is the front door,
- this is the next ring,
- this is the research watchlist,
- and this is what not to inflate again.

A pass is weaker when it widens the watchlist without tightening a buildable front.

## 9. Prefer imported substrate over invented substrate

When current official Rust work exposes new surfaces, prefer building on top of them.

Examples:
- Cargo plumbing / report surfaces,
- docs.rs rustdoc JSON and download behavior,
- crates.io security/advisory surfaces,
- target and toolchain truth,
- public API / semver substrate.

Do not invent a fantasy system if the official ecosystem just exposed a narrower real one.

## 10. Use templates for repeatability

Before inventing a new document style, check whether a template can carry it.
As of this pass, future updates should strongly consider:
- `templates/frontier-delivery-card.template.md`
- `templates/archive-pass-checklist.template.md`

## 11. Pass completion checklist

A strong pass can usually answer “yes” to all of these:

- Did we learn something new from current sources?
- Did we avoid inflating another mega-lane?
- Did we either deepen or eliminate something concrete?
- Did we improve how another person could build the crate?
- Did we update the memory spine?
- Did we leave behind at least one reusable artifact or template?

## 12. Failure modes to watch for

- ranking churn without new evidence
- adding sectors without narrowing seams
- confusing “interesting” with “missing”
- forgetting prior eliminations
- narrating tooling substrate as if it already solved user workflows
- shipping archive changes that only an author, not a new reader, can decode

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
