# Design: Rust Inner Loop Contract 2026Q1

## Goal
Promote **Inner Loop Contract** as the clearest next **bundle-shaping** move beneath the archive’s existing **Build-State Evidence** and **Debuggability** stacks.

This is **not** a claim that the inner loop is now a more important broad ecosystem problem than build-state truth itself.
It is a narrower claim:

> the archive now has enough substrate, and Rust/Cargo now expose enough fresh signals, that the most buildable next composition move is a thin **session → build → debug → handoff** contract rather than another isolated stack note.

The contribution we want is not another IDE backend, local daemon, dashboard, or assistant wrapper.
It is a portable contract that keeps these truths distinct while letting them compose:
- **session truth** — which concrete iteration session is under review;
- **build truth** — what Cargo/build/cache/rebuild evidence actually says;
- **debug truth** — what diagnostics, runtime-side inspection, or debugger tuple actually ran;
- **tradeoff truth** — which target-dir, build-dir, profile, and debug-info choices were intentional;
- **handoff truth** — what issue/docs/support/CI/assistant consumers may honestly conclude.

## Why this rose now
Recent official signals line up unusually well around this seam.

### 1) The pain is still broad and ordinary, not niche
Rust’s March 20, 2026 challenges writeup says compilation performance is a universal productivity tax, async complexity remains a live pain, and ecosystem navigation still depends too much on tacit knowledge. It also explicitly recommends investing in compilation performance, better ecosystem guidance, and closing the sync/async gap. That keeps the inner loop squarely in the center of what Rust users feel day to day, rather than as an IDE-side luxury.  
https://blog.rust-lang.org/2026/03/20/rust-challenges/

### 2) The State of Rust still points to build pain plus debug pain
The 2025 State of Rust survey says resource usage (slow compile times and storage usage) is still “up there” among non-trivial productivity problems, debugging remains high on the list, online docs remain the canonical reference, and editor/LLM-mediated workflows are rising. That combination means more people now need machine-usable inner-loop evidence that can survive summarization instead of one-off local folklore.  
https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

### 3) Cargo is finally producing session-grade evidence
The Cargo build-analysis goal says Cargo plans to collect timings, rebuild reasons, and CLI arguments, and to associate records with a build identifier such as `CARGO_RUN_ID`. It also names future external-tool uses such as historical bottleneck analysis, live insights during development, and build replay for debugging and CI reproducibility.  
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html

Cargo 1.94 also says `cargo report rebuild`, `cargo report sessions`, and improved timings support are landing, while reiterating that Cargo cannot be everything to everyone and that plugins matter. That is exactly the institutional shape a thin `cargo innerloop` companion layer wants.  
https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

### 4) Cargo ↔ editor coexistence is now an official engineering problem, not just a FAQ footnote
The build-dir-layout goal says the current build cache locks too coarsely and explicitly calls out Cargo versus rust-analyzer contention, CI caching pain, fine-grained locking, and cross-workspace cache sharing as reasons to rework the build layout.  
https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html

The March 2026 call for testing the new layout says many projects still depend on unspecified build-dir details because Cargo is missing features, and it asks people to test the new layout against real tools and release processes.  
https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/

Meanwhile rust-analyzer’s own docs say you can use a separate target directory to avoid lock contention, but at the cost of duplicated build artifacts, and its FAQ says this workaround is about letting both Cargo and the IDE make progress independently.  
https://rust-analyzer.github.io/book/configuration.html  
https://rust-analyzer.github.io/book/faq.html

That is no longer just “editor setup trivia.” It is explicit **tradeoff truth**, which is exactly what the inner-loop contract should preserve.

### 5) The debugging side is finally being defined as a contract too
The 2026 debugging survey says strong Rust debugging should include multi-debugger and multi-OS support, quality visualizers, first-class async debugging, and Rust expression evaluation, and it notes that maintaining quality across debugger releases and std-layout changes is hard. That makes “debugging support” look much more like a tuple-scoped evidence problem than a vague wish for better tools.  
https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

### 6) The performance survey says the crossovers are real
The 2025 compiler-performance survey says incremental rebuilds are the most common complaint, says more than 35% of respondents consider IDE and Cargo blocking one another to be a big problem, says the default `dev` profile’s full debuginfo slows compilation and linking, and explicitly says long-term tooling should help explain which code rebuilt and why.  
https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/

That is the exact crossover zone between build-state evidence and debuggability.

## Why this is the right move **now**
The archive already had:
- `design/build-state-evidence-stack.md`
- `design/debuggability-stack.md`
- `design/feedback-loop-stack.md`
- `design/feedback-loop-pilot-program.md`
- `proposals/epic-feedback-loop-stack.md`

What it lacked was a current synthesis note saying **this composition seam has matured enough to deserve frontier attention now**.

So this note is a promotion of an already-existing candidate, not a new moonshot.
That matters because the archive is big enough that promotion discipline is more valuable than minting another adjacent seam.

## What a worthy contribution should look like in theory
A worthy inner-loop contribution should satisfy seven conditions.

### 1) One concrete session before any trends
The primary unit should be one iteration session, not an org-wide dashboard.
The contract should start from: what was the subject, what workflow ran, what build ids exist, what debug tuple ran, and what changed relative to the last meaningful comparison point.

### 2) Build facts and debug facts stay separate
Build-state packs should preserve:
- timings,
- rebuild reasons,
- cache/locking/layout posture,
- change-impact diagnosis,
- build-doctor suggestions.

Debug packs should preserve:
- stable failure identity,
- debugger tuple identity,
- runtime-side inspection identity,
- visualizer/async/expression-evaluation posture,
- repro or escalation imports.

The inner-loop layer should **link** them, not flatten them.

### 3) Tradeoffs must be first-class evidence
The contract should treat these as evidence, not embarrassing implementation details:
- shared target dir vs separate target dir,
- build-dir overrides,
- reduced debuginfo,
- special profiles,
- build-script/proc-macro workarounds,
- editor-specific override commands,
- runtime-side inspection used in place of native debugger parity.

### 4) Consumer summaries must be downstream artifacts
Issue trackers, support pages, release docs, CI logs, editor panes, and assistants should consume bounded handoff artifacts.
They should not become the source of truth.

### 5) The layer must stay plugin-shaped
Cargo is already telling us where some of this belongs: companion tooling, not Cargo core.
A thin `cargo innerloop` / `feedback-loop-pack/v0` shape is therefore a feature, not a compromise.

### 6) It must remain tuple-aware
The same project may have:
- one build tuple,
- one editor tuple,
- several debugger tuples,
- and a runtime-side inspection tool that is neither the build system nor the debugger.

The contract should preserve that multiplicity honestly.

### 7) It must be useful before perfect parity exists
Rust does not need to wait for ideal debugger support, ideal Cargo reports, or ideal async parity before gaining value here.
A good v0 should already make ordinary iteration evidence portable and reviewable.

## What a worthy contribution should look like in practice
The most credible v0 remains the existing `cargo innerloop` direction in `proposals/epic-feedback-loop-stack.md`, but this note sharpens the MVP.

### MVP shape
A strong first implementation should prove five concrete things:
1. **one session record** with subject, workflow, build ids, tuple hints, and intent class;
2. **one linked build-state import** from Cargo-native reporting surfaces;
3. **one linked debug import** from diagnostics, runtime-side inspection, or debugger-tuple evidence;
4. **one explicit tradeoff report** for target-dir/build-dir/profile/debuginfo/editor overrides;
5. **one bounded handoff** for issue/support/docs/CI/assistant consumers.

### Artifact family
Keep the current artifact family:
- `feedback-loop-brief/v0`
- `feedback-loop-session/v0`
- `feedback-loop-pack/v0`
- `feedback-loop-diff/v0`
- `feedback-loop-handoff/v0`

Do **not** absorb underlying packs into one mega-schema.

### Success test
A maintainer should be able to answer all of these from one review bundle:
- which exact loop session is under review?
- what changed, if known?
- what rebuilt and why?
- what debugger or side-channel inspection lane actually ran?
- which tradeoffs were intentional?
- what changed versus the prior session or baseline?
- what may a downstream consumer safely summarize?

If the bundle cannot answer those questions, it is still too soft.

## Why this does **not** outrank everything else
This note does **not** demote the archive’s broader ranking.

- **Build-State Evidence** remains the strongest broad/buildable epic contribution overall.
- **Adoption Navigation + reviewable defaults + receipts** remains the strongest anti-tacit-knowledge answer.
- **Debuggability** remains the clearest rising cross-cutting frontier.

The narrower claim is:
- the clearest next **bundle-shaping** move under the build/debug band is now **Inner Loop Contract**;
- and the clearest current implementation candidate for that move is still the existing **Feedback Loop Stack** / `cargo innerloop` direction.

## Nearby candidates that were not promoted instead
### Package Admission
Still one of the strongest Cargo/crates.io-facing candidates.
But it remains somewhat narrower and more publisher-policy centered than the inner loop, while the fresh evidence this week is unusually concentrated on day-to-day iteration, Cargo report surfaces, and debugging contracts.

### Workspace Environment
Still strategically high and still likely Tier A over time.
But the most current official motion is exposing build-session facts and build/debug tradeoffs, which makes the inner-loop contract the sharper composition move right now.

### Browser + Node dual-target Wasm package overlay
Still the clearest next **public-lane** candidate if the repo widens maintained defaults again.
But that is a different axis from the current build/debug bundle-shaping move.

## Anti-goals
Do not turn this into:
- a universal IDE platform,
- a local daemon that owns every build and debugger,
- a hosted DX portal,
- an “AI dev loop” wrapper,
- or a single developer-experience score.

The point is a **review boundary**, not a new empire.

## Read with
- `design/feedback-loop-stack.md`
- `design/feedback-loop-pilot-program.md`
- `proposals/epic-feedback-loop-stack.md`
- `gaps/developer-feedback-loops-build-debug-iteration-and-honest-session-handoffs.md`
- `design/build-state-evidence-stack.md`
- `design/debuggability-stack.md`
- `design/ecosystem-priority-ladder-2026.md`
- `design/epic-contribution-ladder-2026.md`
