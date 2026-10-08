# Epic crate scorecard application — 2026-03-23

This note applies the archive’s own **epic-crate contribution bar** to the current leading candidates.

It is intentionally simple.
The goal is not fake precision.
The goal is to make promotion and reranking less hand-wavy.

## Scoring method

Same seven-part screen as `meta/epic-crate-contribution-bar-2026-03-23.md`:

- receiver-facing value
- portable artifact seam
- honest claim ceiling
- cross-domain leverage
- imported-substrate fit
- lovable `0.1`
- diff / review friendliness

Each category is scored `0..5`.
Maximum total: `35`.

## Reading rule

Two interpretations matter:

- **salience** — how important the crate seems for the ecosystem territory map,
- **shipability** — how realistic the next implementation pass looks.

A crate may score highly overall and still sit a little later in the practical queue if its `0.1` needs more scenario discipline or fixture work.

## Applied scores

### 1. P-0509 — Crate Ecosystem Pathfinder & Decision-Pack Kit — **34 / 35**

Why it scores this high:
- directly answers a challenge the March 2026 Rust challenges post names explicitly: users still struggle to know which crates they need, trust, or should prefer;
- has very strong receiver-facing value for teams, reviewers, and maintainers inheriting old choices;
- naturally exports decision packs, elimination receipts, and re-entry rules;
- imports substrate from crates.io, docs.rs, rustdoc JSON, crate health, and support-truth lanes without pretending to replace them.

Weakness:
- must stay honest about frozen constraints and timeboxed advice.

### 2. P-0486 — Debuggability Support Contract Kit — **34 / 35**

Why it scores this high:
- debugging remains a live official pain point and now has dedicated survey work;
- it exports support bundles and capability witnesses that other people can inspect later;
- it helps maintainers answer what debugging is *actually* supported rather than what feels plausible.

Weakness:
- very easy to oversell across OS / debugger / backend combinations unless claim ceilings stay strict.

### 3. P-0538 — Concurrency Contract Kit — **33 / 35**

Why it scores this high:
- async remains one of the clearest live Rust difficulties;
- concurrency folklore still creates repeated support, migration, and review cost across many domains;
- the crate exports compact semantic reports instead of another abstraction layer.

Weakness:
- `0.1` becomes credible only with disciplined scenario packs and carefully bounded imports.

### 4. P-0472 — Docs.rs Build Parity & Evidence Kit — **32 / 35**

Why it scores this high:
- docs.rs is explicit about sandbox limits, target behavior, metadata controls, and local/CI testing routes;
- many maintainers still need a boring answer to hosted-vs-local docs drift;
- artifacts are naturally diffable and easy to hand across teams.

Weakness:
- must refuse to claim perfect reproduction when only local preflight existed.

### 5. P-0535 — Dependency Lifecycle Transition Kit — **31 / 35**

Why it scores this high:
- safety-critical guidance explicitly calls for reusable dependency-lifecycle patterns;
- the crate helps teams manage off-ramps, re-resolution risk, and support windows;
- value travels across regulated and ordinary software alike.

Weakness:
- can dissolve into generic dependency policy unless artifacts stay concrete.

### 6. P-0489 — Cargo Build-Dir Consumer Transition Kit — **31 / 35**

Why it scores this high:
- Cargo is actively calling for ecosystem testing of the new build-dir layout;
- many tools still rely on internals because public handoff features are missing;
- artifacts map cleanly to migration adapters and dual-support plans.

Weakness:
- narrower than pathfinder/debuggability/concurrency in cross-domain reach.

### 7. P-0484 — Toolchain & Target Support Contract Kit — **30 / 35**

Why it scores this high:
- safety-critical guidance explicitly asks for target-focused readiness checklists;
- target support claims are routinely flattened today;
- outputs are clear and portable.

Weakness:
- easy to depend on imported upstream facts that drift unless freshness rules stay explicit.

### 8. P-0536 — Crate Knowledge Pack Kit — **30 / 35**

Why it scores this high:
- humans and tools both benefit from pinned, cited, target-aware answer packs;
- docs.rs rustdoc JSON and metadata now make a more useful machine layer possible;
- can materially reduce repeated support work.

Weakness:
- must avoid becoming a vague retrieval/chat wrapper.

### 9. P-0058 — Native Deps Kit — **29 / 35**

Why it scores this high:
- native dependency diagnosis is still real pain across enterprise, offline, cross-platform, and FFI-heavy work;
- Cargo `links`, `system-deps`, and `vcpkg` give real substrate;
- outputs are practical and receiver-facing.

Weakness:
- easier to overspecialize by platform or backend than the leading control-plane lanes.

### 10. P-0046 — Buildscript UX Kit — **28 / 35**

Why it scores this high:
- Cargo still documents conservative rerun behavior and hard-to-read rebuild debugging routes;
- a compact support bundle would help many users immediately;
- `0.1` is straightforward.

Weakness:
- narrower than Native Deps because it covers one seam of the broader native-build stack.

### 11. P-0537 — Compile Iteration Feedback Kit — **28 / 35**

Why it scores this high:
- compile iteration still matters, especially for GUI/live-update workflows;
- it can export useful diffable artifacts and budgets;
- build-analysis and relink-don’t-rebuild work strengthen the substrate.

Weakness:
- more workflow-specific than the higher control-plane winners.

### 12. P-0125 — Cargo SBOM Precursor Workbench Kit — **27 / 35**

Why it scores this high:
- 2026 flagships explicitly keep SBOM support in scope;
- Cargo’s unstable SBOM precursor surface is concrete enough for a workbench crate;
- outputs are naturally diffable and security-relevant.

Weakness:
- narrower day-to-day audience than pathfinder, debug, docs, and concurrency support.

## Main portfolio readout

### Strongest ecosystem-control epics

The scorecard supports keeping these at the top:
- **P-0509 Pathfinder**
- **P-0486 Debuggability**
- **P-0538 Concurrency Contract**
- **P-0472 Docs.rs Parity**
- **P-0535 Dependency Lifecycle**

### Strongest immediate implementation epics

The next likely build order is still:
- **P-0509**
- **P-0486**
- **P-0472**
- **P-0489**
- **P-0046 / P-0058**
- then **P-0538**

because those build/docs/native lanes have unusually concrete current substrate and narrower `0.1` cuts.

## Elimination / demotion rule

Until a new proposal can plausibly score in the high 20s with honest artifacts, do **not** let it outrank this cluster merely because it is newer, trendier, or easier to describe.

Narrow wrappers, chat shells, one-off adapters, and thin convenience APIs should now be treated as:
- sector ideas,
- downstream integrations,
- or follow-ons beneath the current control-plane frontier.

## Sources

- Rust challenges — https://blog.rust-lang.org/2026/03/20/rust-challenges/
- 2025 State of Rust survey results — https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust debugging survey 2026 — https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Rust in 2026 / flagships — https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Call for Testing: Build Dir Layout v2 — https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo build scripts reference — https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo FAQ — https://doc.rust-lang.org/cargo/faq.html
- docs.rs builds — https://docs.rs/about/builds
- docs.rs metadata — https://docs.rs/about/metadata
- docs.rs rustdoc JSON — https://docs.rs/about/rustdoc-json
- crates.io development update — https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- Security advisory for Cargo — https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- safety-critical Rust write-up — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
