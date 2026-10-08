# Frontier salience refresh — 2026-03-23 (203)

This note exists to keep the archive broad while avoiding proposal spam.

## Main judgment

After another current-source sweep, the archive still looks strongest when it prioritizes **receiver-facing support contracts** for common Rust pain, not another wave of generic engines, dashboards, or portals.

The top frontier should therefore remain:

1. **P-0537 Compile Iteration Feedback Kit**
2. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit**
3. **P-0535 Dependency Lifecycle Transition Kit**
4. **P-0536 Crate Knowledge Pack Kit**
5. **P-0538 Concurrency Contract Kit**

## Broad territory map

### Tier A — cross-cutting, still under-served, worthy of “epic” treatment

These still look like the best places to spend repo energy because they cut across many domains and help other people make or review decisions.

1. **Compile iteration / local feedback**
   - GUI, web, desktop, tools, and services all pay this tax.
   - The missing value is not a prettier watcher or yet another linker wrapper.
   - The missing value is a support contract for **reload surface**, **patch eligibility**, **restart ceiling**, and **budget truth**.

2. **Ecosystem navigation / starter-set choice**
   - Nearly every new Rust team still has to learn crate choice through tacit knowledge.
   - The missing value is a decision packet for **candidate basis**, **support visibility**, **reviewed starter sets**, and **revisit triggers**.

3. **Dependency lifecycle / transition planning**
   - Teams still lack a portable bundle for “this dependency is central, this seam exists, this replacement is realistic, revisit here.”
   - The missing value is a transition-support layer, not another popularity score.

4. **Crate knowledge / machine-facing docs handoff**
   - The ecosystem has docs, rustdoc JSON, docs.rs, and examples, but still lacks a compact, provenance-aware bundle for support/search/assistant consumers.
   - The missing value is **material basis**, **query support**, **claim traces**, and **refusal zones**.

5. **Concurrency semantics**
   - Async and concurrency remain expert pain.
   - The missing value is a portable support contract for **reentrancy**, **progress/fairness**, **wait cancellation**, and **execution-context ceilings**.

### Tier B — strong but one notch narrower or more adjacent

These are still worthy, but they are slightly more specialized or depend more on adjacent-lane imports.

- **P-0524 Crate Example Surface Pack Kit**
- **P-0489 Cargo Build-Dir Consumer Transition Kit**
- **P-0486 Debuggability Support Contract Kit**
- **P-0121 FFI Boundary Conformance Kit**
- **P-0125 Cargo SBOM Precursor Workbench Kit**
- **P-0011 Crate Health Contract Kit**

### Tier C — often useful, but easy to overproduce

Prefer deepening existing lanes before adding more here.

- generic dashboards,
- generic “best crate” rankers,
- dev server wrappers,
- docs portals,
- benchmark recorders without portable receipts,
- and “one tool to unify everything” products.

## What the archive should actively deprioritize

Do not spend the next pass on:

1. another score-only ranking crate,
2. another generic docs UI,
3. another framework-specific hot-reload story that exports no portable receipts,
4. another lock / channel / runtime wrapper that avoids naming its claim ceiling,
5. or another shipkit unless the missing value really escapes the existing contract lanes.

## Why the top five still win

They still outperform narrower ideas on the same three tests:

1. **cross-domain leverage** — they help many Rust teams, not only one vertical;
2. **receiver-facing value** — they produce something another person can review later;
3. **substrate readiness** — the ecosystem already has enough raw material to make the crate practical now.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- https://dioxuslabs.com/learn/0.7/essentials/ui/hotreload/
- https://dioxuslabs.com/learn/0.7/tutorial/rsx/
- https://v2.tauri.app/reference/cli/
- https://book.leptos.dev/interlude_styling.html
- https://doc.rust-lang.org/cargo/commands/cargo-info.html
- https://doc.rust-lang.org/cargo/commands/cargo-search.html
- https://docs.rs/about/metadata
- https://docs.rs/about/builds
