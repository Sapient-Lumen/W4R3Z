# Gap: developer feedback loops still lack one portable build → debug → handoff boundary

## Summary
Rust now has much better raw ingredients for improving the **developer feedback loop** than it did even a year ago:
- Cargo is becoming more machine-readable about build sessions, rebuild reasons, and timings;
- build-dir layout / locking work is targeting real Cargo ↔ rust-analyzer contention and cross-workspace cache reuse;
- the build-performance survey collected explicit workflow pain around IDE latency, disk usage, and build explanation;
- the debugging survey says the community still lacks reliable multi-debugger, multi-OS, async-aware debugging support;
- and the 2025 State of Rust survey still places resource usage and debugging among the main productivity problems, while also saying online docs remain canonical and LLM tooling is rising.

What Rust still lacks is the **portable contract layer for the loop itself**.

Today, teams can often answer fragments such as:
- “Cargo rebuilt these crates,”
- “rust-analyzer was fighting `cargo check`,”
- “we moved to a separate target/build dir,”
- “the debugger only works on this tuple with these visualizers,”
- “Tokio Console helped more than LLDB here,”
- or “we filed an issue with timings, traces, and a repro.”

What they still struggle to answer cleanly is:
- what exact edit/change/build/debug **session** is under review,
- which build-state facts versus diagnosis suggestions actually came from Cargo,
- which debugger tuple or runtime-inspection lane was actually exercised,
- where build performance and debugging trade off against each other (for example via debug info or duplicated target dirs),
- which downstream docs/support/issue/assistant view may honestly summarize the result,
- and what changed between two iterations without re-reading shell history, editor state, issue comments, and CI logs.

That missing layer is not another IDE plugin, not another daemon, not another local dashboard, and not another assistant wrapper.
It is a **portable feedback-loop boundary** above build-state truth and debuggability truth.

## Why now
Current official Rust/Cargo signals make this seam more concrete than it used to be:
- the 2025 State of Rust survey says resource usage (slow compile times and storage usage) remains “up there,” debugging remains one of the main non-trivial productivity problems, and official online docs still act as the preferred canonical reference while LLM/tool-driven learning grows;
- the 2025 compiler-performance survey says build pain differs by workflow, says more than 35% of users consider IDE and Cargo blocking one another to be a big problem, and says reducing debug info can materially improve disk usage and build/link time;
- the Cargo build-analysis goal is explicitly about recording metadata across invocations, associating records with a build identifier like `CARGO_RUN_ID`, explaining rebuilds, and eventually unlocking build replay for debugging;
- the build-dir-layout goal explicitly targets fine-grained locking, rust-analyzer coexistence, target-dir GC, and cross-workspace shared caches;
- rust-analyzer’s own configuration docs and FAQ say a separate target directory can avoid build-lock contention, but only by duplicating artifacts, which means the ecosystem already lives with explicit build/debug tradeoffs that are not being carried forward as portable evidence;
- the March 2026 build-dir-layout-v2 call for testing says many projects still rely on unspecified build-dir details because Cargo lacks some missing features, which is a strong sign that the loop boundary is still too implicit;
- the 2026 debugging survey says Rust still lacks truly stellar cross-debugger support, async debugging, strong visualizers, and Rust expression evaluation across tuples;
- the Cargo 1.94 development-cycle report says `cargo report rebuild`, `cargo report sessions`, and improved timing support are landing, and also reiterates that Cargo cannot be everything to everyone and that plugins matter.

Sources:
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://rust-analyzer.github.io/book/configuration.html
- https://rust-analyzer.github.io/book/faq.html
- https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## The current seam is awkward
Today, feedback-loop truth gets improvised from incompatible ingredients:
- editor-local state,
- Cargo timings or rebuild reports,
- debug-info and profile tweaks,
- rust-analyzer FAQ workarounds,
- debugger setup instructions,
- runtime instrumentation or Tokio Console state,
- issue templates,
- and human memory about what changed between attempts.

That usually leads to five failures:
1. build facts and diagnosis suggestions get flattened into one story;
2. native debugger support and runtime-side inspection get treated as interchangeable;
3. one-off editor workarounds become fake ecosystem guidance;
4. issue/support/assistant summaries overclaim what the underlying evidence proved;
5. the same team keeps re-diagnosing the same “slow/hard to debug” loop from scratch.

## Why this matters
This gap is now important enough to treat as the clearest next **bundle-shaping** move under the build/debug band, even though it does not outrank Build-State Evidence as the archive’s broadest build-first contribution overall.

This gap matters to more than Cargo internals or IDE authors.
It matters to:
1. **application and library maintainers** — because they need honest iteration evidence, not folklore;
2. **Cargo / rust-analyzer / debugger / tracing tool authors** — because interop improves when loop sessions and handoffs are explicit;
3. **support and docs maintainers** — because build and debug advice should import bounded evidence instead of paraphrasing issue archaeology;
4. **CI and release engineers** — because build-dir changes, target-dir policy, debug-info posture, and repro handoffs all affect automation;
5. **agent/editor tooling** — because LLM-era workflow consumers need explicit session provenance and lossiness instead of inferred private state.

## What good looks like
A worthy contribution here is a thin composition layer above the **Build-State Evidence Stack** and the **Debuggability Stack**, with bounded imports from **Semantic Context** and **Edit Workflow** when they are actually available.

It should provide at least:
- `feedback-loop-brief/v0` — why this loop subject/lane exists;
- `feedback-loop-session/v0` — one concrete edit/build/run/debug session with explicit tool/workflow identity;
- `feedback-loop-pack/v0` — linked build/debug evidence with explicit caveats;
- `feedback-loop-diff/v0` — what changed between two review points or two sessions;
- `feedback-loop-handoff/v0` — bounded summaries for issues, docs, support, CI, and assistant/editor consumers.

The winning version should keep these distinctions visible:
- **changed-slice / edit truth** versus **build-state truth**,
- **build observation** versus **build diagnosis**,
- **native debugger tuple truth** versus **runtime-side inspection truth**,
- **core evidence packs** versus **thin consumer renderings**,
- and **one session’s truth** versus **cross-session trend claims**.

The bar is not a smarter dashboard.
The bar is a durable, explainable, importable evidence boundary for Rust’s feedback loop.
