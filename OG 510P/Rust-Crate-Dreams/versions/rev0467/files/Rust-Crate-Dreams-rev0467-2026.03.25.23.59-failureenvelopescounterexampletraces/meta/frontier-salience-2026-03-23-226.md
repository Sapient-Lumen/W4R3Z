# Frontier salience 226 — the strongest next repo work is demand-mapped planning for the top control-plane crates

This pass did **not** rerank the whole archive again.
The sharper question was:

> If we want this repository to become a genuinely worthy map of missing epic crates, what should we deepen next so the top ideas become buildable rather than merely clever?

## Main judgment

The strongest next repo work is not another broad append-only brainstorm.
It is a **demand-mapped planning pass** for the control-plane frontier.

That means three concrete moves:

1. map the current frontier against a very wide set of real Rust use cases,
2. turn **P-0509** into a lane-catalog product rather than an abstract crate-choice idea,
3. turn **P-0486** into a capability-stack product rather than a generic “debugging support” idea.

## Why this is the right next step

### 1. Current official Rust signals are unusually broad
The official picture is not just “backend services and compile times.”
Current goals and flagships span:

- async parity,
- building blocks and test/build tooling,
- safety-critical Rust,
- Wasm Components,
- C++ interop,
- Rust for Linux,
- spec/reference/FLS upkeep,
- and experimental compile-time / reflection work.

That means the archive should avoid thinking in one narrow cultural default.
The top missing crates must survive contact with **many different Rust worlds**.

### 2. The strongest archive proposals are still horizontal
Across that wide demand map, the same missing layers keep recurring:

- task-oriented crate choice,
- dependency transition and replacement,
- support-contract truth for targets/toolchains/debugging,
- machine-usable crate knowledge,
- concurrency/runtime semantics,
- and build/iteration visibility.

That is why the control-plane frontier still beats most new narrow ideas.

### 3. The next bottleneck is product shape, not ideation
The archive already knows what a strong missing crate sounds like.
The bottleneck is now whether the strongest lanes have:

- named task families,
- clear artifact vocabularies,
- good command surfaces,
- practical proving grounds,
- and guardrails against fake support claims.

## Practical repo-building order now

This is **not** the same as the overall ecosystem salience ranking.
It is the order most likely to turn the repo into a sharper planning instrument.

### 1. P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit
Why first:
- nearly every Rust domain needs crate choice;
- current official material still says ecosystem navigation is hard;
- crates.io/docs.rs/Cargo provide ingredients, not a durable decision packet.

What the repo should deepen next:
- task-lane templates,
- lane-specific role defaults,
- freeze/readiness criteria by lane,
- policy imports,
- and reviewable starter-set bundles.

### 2. P-0486 Debuggability Support Contract Kit
Why second:
- debugging remains a live productivity gap;
- the compiler team ran a dedicated debugging survey in 2026;
- and “debugging works” is still too fuzzy to review honestly.

What the repo should deepen next:
- capability-stack vocabulary,
- session-family distinctions,
- async-debug visibility classes,
- packaged artifact handoff expectations,
- and backend/session coverage receipts.

### 3. P-0535 Dependency Lifecycle Transition Kit
Why third:
- many domains now need an answer not just to “what should we use?” but to “how do we safely leave, fork, pin, replace, or re-resolve it later?”
- this is especially important in regulated, security-sensitive, and long-lived deployments.

### 4. P-0484 Toolchain & Target Support Contract Kit
Why fourth:
- build-std, Rust-for-Linux, Wasm Components, docs.rs target defaults, and safety-critical work all make support claims more nuanced;
- many sector proposals are really asking for better target/toolchain truth.

### 5. P-0536 Crate Knowledge Pack Kit
Why fifth:
- docs.rs is useful but constrained;
- rustdoc JSON and metadata are real substrate;
- and humans plus tools increasingly need pinned, cited, target-aware crate knowledge.

## What this implies for “worthy” crate contributions

A crate now looks increasingly worthy when it can survive these tests:

1. **cross-domain reuse** — the outputs matter in more than one Rust subculture;
2. **receiver-facing value** — the crate hands another team an artifact they can inspect later;
3. **close-truth separation** — it does not flatten adjacent support claims into one fake status word;
4. **upstream fit** — it composes with Cargo/rustc/docs.rs/crates.io rather than trying to replace them;
5. **present-day usefulness** — it is valuable even before future language/compiler goals land.

## What this pass demotes by implication

The repo should now be even more skeptical of:

- another domain wrapper with no evidence artifact,
- another crate ranking score,
- another “AI assistant for crates” shell without pinned knowledge packs,
- another sector proposal whose real missing seam is target/toolchain/debug/choice truth,
- or another broad “platform crate” that lacks a narrow artifact family.

## Sources
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
- https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://rust-lang.github.io/rust-project-goals/2025h2/relink-dont-rebuild.html
- https://rust-lang.github.io/rust-project-goals/2025h2/build-std.html
- https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- https://rust-lang.github.io/rust-project-goals/2025h2/reference-expansion.html
- https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://docs.rs/about/builds
- https://docs.rs/about/metadata
- https://docs.rs/about/rustdoc-json
