# Design: Rust ecosystem epic map (2026 Q1)

## Goal
Map the territory of what Rust is still most missing **now**, with enough structure that the archive can rank, synthesize, and sometimes eliminate candidate contributions instead of widening by habit.

This note is deliberately broader than one default card and narrower than “the future of Rust”.
It exists to answer three different questions without collapsing them into one:
1. **What is broadly most missing in Rust right now?**
2. **Which missing things are actually buildable as worthy companion-tool / library / workflow contributions?**
3. **If the archive widens its maintained public lanes again, which next lane is most justified?**

## Why this note is needed now
The official signals are now aligned enough that the archive should stop pretending all “important missing things” belong on one flat list.

Rust’s March 20, 2026 challenges post says the recurring broad problems are:
- **compilation performance / resource usage**;
- **async complexity**;
- **ecosystem navigation driven by choice paralysis and tacit knowledge**;
- and domain-specific maturity gaps, especially in **embedded** and **safety-critical** settings.
https://blog.rust-lang.org/2026/03/20/rust-challenges/

The 2025 State of Rust survey says resource usage is still among the leading non-trivial productivity problems, debugging remains high in the problem list, and online docs remain the preferred canonical reference even as editor/LLM-mediated learning grows.
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Cargo’s current work keeps reinforcing the same shape:
- `cargo report` / build-analysis work is becoming real;
- build-dir layout is being reworked specifically because too many tools and workflows depend on unstable internals;
- and workspace/config discovery is still capable of cross-project breakage.
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/

At the same time, the Rust project is explicitly investing in:
- **SBOM support**;
- **public/private dependency control**;
- **build-std / bigger-build-system integration**;
- **Wasm Components**;
- **Just Add Async**;
- and **Safety-Critical Rust**.
https://rust-lang.github.io/rust-project-goals/2026/flagships.html

The 2026 debugging survey then makes a second cross-cutting gap unusually concrete: Rust still lacks first-class debugger tuple support, async debugging clarity, and expression-evaluation support across tools and platforms.
https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

Finally, the Rust Foundation’s 2026–2028 strategy explicitly ties together **stable infrastructure**, **sustainable maintenance**, and **adoption & innovation**. That means worthy contributions should increasingly be judged not only by cleverness, but by whether they reduce friction in a way the ecosystem can actually sustain.
https://rustfoundation.org/strategic-plan/

## Ranking rule
Score a candidate against six questions:
1. **Breadth of pain** — does it reduce recurring friction for many Rust users or teams?
2. **Official pull** — do Rust/Cargo/crates.io/Foundation signals already point toward it?
3. **Artifact boundary** — can it emit reviewable machine-usable facts instead of screenshots and lore?
4. **Buildability** — can a v0 ship as a thin companion layer rather than a platform rewrite?
5. **Maintenance economics** — can it stay current without requiring a permanent curation empire?
6. **Archive leverage** — does the archive already have enough substrate that this is a synthesis move rather than a cold start?

The default move is to rank candidates higher when they win on at least **five** of those six questions.

## Tier A — broad ecosystem contributions that are most worth building

### 1. Build-State Evidence Stack
Primary archive files:
- `design/build-state-evidence-stack.md`
- `design/cargo-report-kit.md`
- `design/build-cache-kit.md`
- `design/change-impact-kit.md`
- `design/build-doctor-kit.md`
- `proposals/epic-build-state-evidence-stack.md`

Why it stays first:
- it matches the loudest broad pain in the latest survey and challenges work;
- Cargo is already generating more native analysis surfaces;
- it improves CLI, CI, editor, and large-workspace reality all at once;
- and it is one of the clearest thin-layer opportunities rather than a platform rewrite.

What the worthy contribution looks like:
- a `cargo build-state` / `build-state-pack/v0` family;
- imports native Cargo/build evidence rather than scraping terminal output;
- keeps **rebuild topology**, **contention/duplication truth**, **relink opportunities**, and **human diagnosis** separate.

### 2. Adoption Navigation Bundle + Reviewable Lane Defaults Corpus
Primary archive files:
- `design/adoption-navigation-bundle.md`
- `design/reviewable-lane-defaults-corpus.md`
- `design/lane-default-evidence-bundle.md`
- `design/adoption-decision-stack.md`

Why it stays near the top:
- the latest challenges post explicitly names **choice paralysis** and **tacit knowledge**;
- the archive’s maintained default cards are already the best concrete answer it has to that problem;
- and online docs remaining canonical while editor/LLM mediation rises makes reviewable defaults more, not less, important.

What the worthy contribution looks like:
- not a “best crates” canon;
- but a bounded, renewable corpus of project-class answers, receipts, and drift-aware lane splits.

### 3. Debuggability Stack
Primary archive files:
- `design/debuggability-stack.md`
- `design/debugger-experience-kit.md`
- `design/debugger-pilot-program.md`
- `proposals/epic-debuggability-stack.md`

Why it rises now:
- debugging is still one of the major non-trivial productivity problems;
- the 2026 survey makes the missing debugger tuple / visualizer / async-debug / expression-eval support explicit;
- and Rust now needs a portable evidence layer for debugging claims, not just one more debugger guide.

What the worthy contribution looks like:
- a thin `cargo debuggability` / `debuggability-pack/v0` layer;
- explicit **failure identity**, **runtime-correlation**, **debugger tuple**, and **repro/handoff** artifacts;
- honest `supported` / `partial` / `watch` / `unsupported` posture.

### 4. Package Admission + Supply-Chain Evidence
Primary archive files:
- `design/package-admission-stack.md`
- `design/dependency-review-stack.md`
- `design/inventory-evidence-stack.md`
- `proposals/epic-package-admission-stack.md`

Why it stays high:
- crates.io now exposes richer review inputs, including the Security tab;
- 2026 flagships keep SBOM support and dependency-surface control active;
- and the ecosystem still lacks a boring review boundary between “published package” and “downstream adoption decision”.
https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
https://rust-lang.github.io/rust-project-goals/2026/flagships.html

### 5. Toolchain Productization + Dynamic Analysis Fabric
Primary archive files:
- `design/toolchain-productization-stack.md`
- `design/sanitizer-battery-kit.md`
- `design/sanitizer-battery-lane-map.md`
- `design/safety-critical-evidence-stack.md`

Why it stays in the top band:
- 2026 goals keep build-std, SBOM, safety-critical work, and async/runtime correctness pressure active;
- the archive already has the right substrate for sanitizers, careful/std-aware toolchains, and safety-case imports;
- and the ecosystem still needs a reviewable contract above custom toolchains, sanitizers, and future BorrowSanitizer-style lanes.
https://rust-lang.github.io/rust-project-goals/2026/flagships.html
https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

### 6. Workspace Environment Bundle
Primary archive files:
- `design/workspace-environment-bundle.md`
- `design/workspace-environment-stack.md`
- `design/project-bootstrap-stack.md`

Why it stays important:
- Cargo’s own discovery/config behavior keeps proving that workspace environment truth is a real systems problem;
- it improves onboarding, CI, remote/devcontainer/Nix handoffs, and agent-safe operation;
- but it remains slightly less urgent than the top three broad frictions.

## Tier B — next under-modeled or lane-specific moves

### 7. Browser + Node dual-target Wasm package overlay
Primary archive files:
- `design/browser-node-dual-target-wasm-package-overlay.md`
- `proposals/epic-browser-node-dual-target-wasm-package-overlay.md`
- `design/browser-wasm-package-default-lane.md`

Why it matters now:
- the current browser-package card intentionally leaves this as future work;
- the `rustwasm` sunset made maintenance and tool ownership impossible to ignore;
- `wasm-bindgen` and `wasm-pack` explicitly expose different browser versus Node target modes and feature asymmetries;
- and teams keep wanting one package lane where browser and Node both matter, without actually wanting a native Node add-on.
https://blog.rust-lang.org/inside-rust/2025/07/21/sunsetting-the-rustwasm-github-org/
https://rustwasm.github.io/docs/wasm-pack/commands/build.html
https://rustwasm.github.io/docs/wasm-bindgen/reference/deployment.html
https://rustwasm.github.io/docs/wasm-bindgen/reference/js-snippets.html

Why it is not above Tier A:
- it is important, but narrower;
- and it is best approached as an overlay / next lane split, not the ecosystem’s primary missing cross-cutting control plane.

### 8. Safety-critical / embedded adoption-onramp bundle
Primary archive files:
- `design/safety-critical-evidence-stack.md`
- `design/toolchain-productization-stack.md`
- `design/ffi-boundary-kit.md`
- `design/target-readiness-stack.md`

Why it stays high but domain-scoped:
- the challenges work explicitly says embedded and safety-critical maturity gaps remain real;
- the safety-critical post calls for target-readiness checklists, dependency lifecycle patterns, safety-case-friendly async runtimes, and stronger interop guidance;
- but the right answer here is a bounded onramp and evidence layer, not one universal “safety Rust” platform.
https://blog.rust-lang.org/2026/03/20/rust-challenges/
https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

## What to explicitly not promote yet
### Raw custom Wasmtime embedder
This remains important, especially with Wasm Components rising, but it is still narrower than the browser+Node package overlay and dramatically narrower than the broad Tier A control-plane gaps.
Use it as a future lane only when the archive wants a deliberately lower-level Wasm-host card.
https://docs.rs/wasmtime/latest/wasmtime/component/index.html
https://docs.wasmtime.dev/wasip2-plugins.html

### Durable internal library
This remains useful as a real project class, but it is a weaker repo-shaping move than the current top broad epics and weaker than the next explicit public-lane split.
It should not jump the queue merely because it sounds boring and prudent.

### “Another maintained default card” by momentum alone
The defaults corpus is now large enough that widening it without a named split or named omission would reintroduce archive sprawl.
A new card should now happen only when it clearly corrects a missing lane or resolves repeated drift.

## Recommended archive consequence
1. Keep **Build-State Evidence** as the strongest broad/buildable epic contribution.
2. Keep **Adoption Navigation + reviewable defaults + receipts** as the strongest research-side / anti-tacit-knowledge answer.
3. Treat **Debuggability** as the clearest rising cross-cutting frontier that deserves renewed practical attention.
4. If widening the maintained public lanes again, prefer the **browser + Node dual-target Wasm package overlay** before **raw custom Wasmtime embedder** or **durable internal library**.
5. Keep the archive honest by separating:
   - **broad ecosystem missingness**;
   - **near-term buildability**;
   - **next public-lane candidacy**;
   - and **repo hygiene/meta work**.

## Bottom line
If the question is “what would count as a worthy or even epic Rust ecosystem contribution right now?”, the clearest answers are not one more framework or one more runtime.
They are thin, reviewable layers that:
- make build reality legible;
- reduce tacit-knowledge-driven adoption choices;
- make debugging claims testable;
- and turn supply-chain / toolchain facts into bounded artifacts instead of folklore.

The browser+Node Wasm overlay is real and deserves promotion as the next public-lane candidate.
But the bigger answer remains that ideal Rust still most needs **reviewable control planes** above fast-moving tools, not another pile of wrappers that silently become pseudo-standards.
