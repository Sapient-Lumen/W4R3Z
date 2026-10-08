# Archive operator stack — source-grounded, tier-aware, and amnesia-resistant refresh workflow

This file is about **how to operate the archive itself**.
It exists so future humans and LLMs do not lose the shape of the work.

## Start here before a broad refresh

Read in this order:
1. `entries/2026-03-23-434.md`
2. `meta/epic-crate-territory-map-2026-03-23-225.md`
3. `meta/frontier-salience-2026-03-23-224.md`
4. `meta/archive-memory-anchor-2026-03-22.md`
5. `meta/llm-hygiene.md`
6. `meta/prioritization.md`

## Every pass must choose one mode first

A pass should explicitly be one of:
1. **deepen** — add artifacts, doctor checks, lane boundaries, or fixtures to an existing proposal;
2. **rerank** — change salience or territory placement using fresh sources;
3. **merge / eliminate** — reduce archive sprawl where two proposals describe the same seam;
4. **append** — add a new proposal only if it clearly beats existing frontier lanes on ecosystem leverage.

Default mode after rev0434:
- prefer **deepen**,
- then **rerank**,
- then **merge / eliminate**,
- and only lastly **append**.

## Every promoted lane must answer the same practical questions

For any lane moved upward, record:
- **why now**,
- **what changed in the evidence**,
- **what exact artifact family the crate should export**,
- **what a doctor / validator command should check**,
- **which close neighboring truths must stay separate**,
- **what would cause demotion later**.

## Required artifact shape for serious proposals

A serious crate proposal should usually define:
- one or more `*.receipt.json` artifacts for basis / authority / route truth,
- one or more `*.report.json` artifacts for gaps / ceilings / drift / outcomes,
- one `*.manifest.json` or bundle format for handoff,
- scenario fixtures showing confusing near-miss cases,
- human-readable lane boundaries,
- machine-consumable exports.

## Required repo touch-set for a meaningful archive refresh

If a broad pass changes salience or architecture, update all of these together:
- `README.md`
- `INDEX.md`
- latest `entries/...`
- `meta/prioritization.md`
- `meta/decision-log.md`
- `meta/research-ledger.md`
- `meta/llm-hygiene.md`
- `meta/archive-memory-anchor-2026-03-22.md`

Add `meta/roadmap.md` too when the next-pass order materially changes.

## Band discipline

Do not silently move ideas between these bands:
- **Band A:** control-plane epics
- **Band B:** adoption amplifiers
- **Band C:** sector labs / interop workbenches
- **Band D:** moonshots / pack-family bets

If a lane moves bands, say so explicitly and explain why.

## LLM-specific rules

### 1. No uncited “ecosystem mood” claims
If the pass relies on current Rust pain, project goals, crates.io behavior, or docs.rs behavior, cite the exact source in the entry and research ledger.

### 2. No generic “LLM-ready” language
A crate is not “LLM-ready” because docs exist.
Require material-basis, citation, answerability, refusal, and build/target/version honesty.

### 3. No prose-only promotions
A proposal cannot be promoted merely because it sounds important.
It needs a credible artifact package.

### 4. No flattening of support surfaces
Do not let docs.rs visibility, crates.io Security-tab data, popularity, one blog post, and one successful demo collapse into one fake support verdict.

### 5. Resist empty LLM tone
The March 2026 Rust challenges post includes a retraction note about an earlier LLM-written draft and explicitly records community discomfort with generic, substance-light LLM phrasing.
Treat that as a live warning: concise, specific, source-grounded prose is part of archive quality.
Source: https://blog.rust-lang.org/2026/03/20/rust-challenges/

## Anti-amnesia checklist

Before finalizing a broad refresh, ask:
1. Did the pass keep control-plane, adoption, sector, and moonshot lanes separate?
2. Did it explain what the crate would provide **other people**, not just the author?
3. Did it record concrete artifact names and doctor-check plans?
4. Did it use fresh sources where freshness matters?
5. Did it update the memory files so the next pass does not re-open settled questions?
6. Did it demote or merge anything that no longer beats the frontier?

## Promotion tests

A new proposal should usually fail promotion unless it can answer “yes” to most of these:
1. Does it beat at least one Band A lane on ecosystem-wide pain?
2. Does it export a genuinely new artifact seam?
3. Is it useful across multiple domains or organizations?
4. Is it valuable before future language/compiler work lands?
5. Would another team realistically adopt the outputs?

## Sources consulted
- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
