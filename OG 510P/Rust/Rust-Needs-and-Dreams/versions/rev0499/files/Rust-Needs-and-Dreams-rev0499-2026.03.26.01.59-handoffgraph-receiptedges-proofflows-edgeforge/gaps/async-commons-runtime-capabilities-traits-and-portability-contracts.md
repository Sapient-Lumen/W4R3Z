# Gap: async commons are still too implicit for honest runtime portability

## What is missing
Rust still lacks a **portable, reviewable contract for async commons**.

The async problem is no longer just “Tokio is popular” or “language ergonomics are still improving.”
The official Rust challenges work published on March 20, 2026 says many users avoid async because it feels like a different programming model, and explicitly calls out the way choosing one useful library can immediately lock a project into one runtime family or another. The same post recommends both better async-language ergonomics and a more cohesive async ecosystem, including the possibility of more fundamental async library traits/functions in `std` over time. The 2025H1 async goal likewise said runtime choice and runtime interoperability remain central pain points, and the Async Book still says async Rust has compatibility constraints between runtimes and a higher maintenance burden than synchronous Rust.

That combination changes the design center. What is missing is not just another runtime, not just another compatibility shim, and not just more language work. Rust needs a **thin async-commons layer** that can describe:
- which async capabilities a library or application actually requires,
- which parts live in `core`/`std` versus `futures`-family crates versus runtime crates,
- which runtime-specific traits/types are being exposed,
- which adapters exist and what they lose,
- which seams are mature enough for neutral shared building blocks,
- and which async lanes are still waiting on language/compiler progress instead of pretending they are ready now.

Sources:
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- https://blog.rust-lang.org/2025/08/05/july-project-goals-update/
- https://rust-lang.github.io/async-book/01_getting_started/03_state_of_async_rust.html

## The current seam is awkward
Today, async portability gets improvised from a messy mixture of:
- `std::future::Future` and `Pin`/poll lore,
- `futures-core` / `futures-io` / utility-crate traits,
- runtime-specific I/O, time, task, and signal APIs,
- ad hoc compatibility adapters,
- README prose about “runtime-agnostic” support,
- and issue-thread memory about what really works outside the maintainer’s preferred executor.

That usually fails in predictable ways:
- **capability needs stay implicit** — libraries say “runtime agnostic” without naming whether they need spawning, timers, I/O, cancellation trees, task-local state, or signals;
- **neutral versus runtime-shaped surfaces blur together** — `Future` is fundamental, but much of the rest of the ecosystem lives in semi-common or runtime-specific layers;
- **adapter lossiness gets hidden** — boxing, buffering, wake/readiness semantics, cancellation differences, and local-vs-`Send` assumptions disappear behind convenience wrappers;
- **language blockers and library blockers get confused** — async traits, async dyn dispatch, generators/streams, pin ergonomics, and lending/borrowing constraints all move at different speeds;
- **downstream stacks over-own portability** — Async Lifecycle, Async Reliability, Adoption, and Productization notes each end up re-describing the same runtime-choice problem.

## Why this matters
This gap matters to:
1. **library authors** — they need to publish honest capability requirements instead of vague portability claims;
2. **runtime authors** — neutral seams make competition healthier when adapter truth is explicit;
3. **service and app teams** — they need to know when a dependency choice hard-locks runtime family or background-work model;
4. **ecosystem guidance and adoption tooling** — Atlas/Adoption cannot recommend async stacks well if the shared substrate is still folklore;
5. **language and standard-library evolution** — a reviewable async-commons layer gives Rust a better staging ground for deciding which lower-level traits/functions really deserve wider blessing later.

## What “good” looks like
A worthy contribution here is **not** a universal runtime facade, not a winner-take-all async framework, and not a fake “works on every runtime” badge.

It is a **neutral async-commons boundary** with canonical artifacts such as:
- `async-seam/v0` — what seam is under review (`io`, `spawn`, `time`, `cancellation`, `streaming`, etc.);
- `async-capability-profile/v0` — the required capabilities for a library/app lane;
- `async-common-surface/v0` — the neutral traits/types/functions that form the shared layer;
- `async-adapter-profile/v0` — how a runtime or crate maps to the shared surface, including lossiness;
- `async-vector-set/v0` — conformance and negative cases for the seam;
- `async-readiness-report/v0` — whether the seam is ready, partial, watch-only, or blocked on language/compiler work;
- `async-commons-pack/v0` — the review bundle consumed by Atlas, Async Lifecycle, and other downstream stacks.

From those artifacts, tools should be able to derive:
- runtime-portability notes for crate authors,
- compatibility statements for service/client/product stacks,
- bounded assistant-context exports,
- and sharper language/stdlib feedback about which missing pieces are real blockers.

## Why this could be epic
This is the sort of contribution that looks small but changes a lot:
- it reduces gratuitous runtime lock-in without denying real semantic differences;
- it gives async-library authors a way to be honest about requirements and adapters;
- it lets Async Lifecycle and Async Reliability import portability truth instead of re-inventing it;
- it gives Atlas / Adoption / Starter Pack work a better substrate for async stack guidance;
- and it creates a better evidence lane for future `std`/language discussions than blog-post folklore alone.

If Rust wants async to feel less like a separate sub-language and more like a first-class ecosystem capability, it needs **async commons** at least as much as it needs more point improvements.
