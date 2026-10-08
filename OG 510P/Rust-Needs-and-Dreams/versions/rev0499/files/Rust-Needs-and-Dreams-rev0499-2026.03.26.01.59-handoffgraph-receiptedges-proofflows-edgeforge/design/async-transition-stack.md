# Design note: Async Transition Stack (close the sync→async chasm without pretending async is one lane)

## Goal
Define the missing **transition layer** between “this project/team can still stay mostly sync Rust” and “this project now needs an explicit async lane with the right runtime, lifecycle, reliability, debugging, and learning consequences”.

This note is not a new runtime, not a new framework, and not a new tutorial empire.
It is the thin layer that says:
- what **sync baseline** we are starting from,
- what **trigger or boundary** is actually forcing async,
- which **async common surfaces and runtime commitments** are now in play,
- which **lifecycle / reliability / debugging** consequences that creates,
- and how the result stays **reviewable, teachable, and reversible enough** to compare against staying sync.

## This note composes with
- [`design/profiled-onramp-stack.md`](./profiled-onramp-stack.md)
- [`design/async-commons-kit.md`](./async-commons-kit.md)
- [`design/async-lifecycle-kit.md`](./async-lifecycle-kit.md)
- [`design/async-reliability-stack.md`](./async-reliability-stack.md)
- [`design/feedback-loop-stack.md`](./feedback-loop-stack.md)
- [`design/debuggability-stack.md`](./debuggability-stack.md)
- [`design/canonical-learning-stack.md`](./canonical-learning-stack.md)
- [`design/project-bootstrap-stack.md`](./project-bootstrap-stack.md)
- [`design/service-productization-stack.md`](./service-productization-stack.md)

## Why this seam matters now
Fresh official Rust signals keep describing the same gap from different sides:
- Rust’s March 20, 2026 challenges writeup says async is still a major pain point, says many developers avoid it, describes it as feeling like a different programming model, and explicitly ties the pain to ecosystem fragmentation and early runtime lock-in.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
- The 2026 Rust Project Goals page keeps **Just Add Async** as an active flagship theme and says patterns that work in sync Rust should work in async Rust. Its 2026 milestones still include return type notation, `async fn in dyn Trait`, immobile types / guaranteed destructors, and ergonomic ref-counting — strong evidence that the transition boundary is still live rather than solved.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The earlier async flagship goal says the long-term target is an async experience that is as expressive, reliable, and productive as sync Rust; it also says users still face runtime-choice stress, hard-to-reverse commitments, and interop trouble across runtimes.
  https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- The 2026 debugging survey says first-class async debugging is still a desired-but-not-yet-finished capability, alongside debugger visualizers, cross-debugger support, and Rust expression evaluation.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The 2025 compiler-performance survey results say workflows differ materially, editor/Cargo contention is a real blocker for more than 35% of respondents, and dev-profile debug info often trades iteration speed against debugging posture. Async-heavy service and GUI users are among the cohorts hit hardest by iteration friction.
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- The 2025 State of Rust survey says online docs remain the preferred canonical reference while editor/LLM-mediated workflows are rising, which increases the value of machine-usable async route artifacts and raises the cost of folklore-driven “just use runtime X” advice.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Taken together, these signals suggest that ideal Rust still needs one more execution seam: **a reviewable async-transition layer** that keeps sync baseline, runtime commitment, lifecycle risk, debug posture, and learning handoff visibly separate.

## The missing seam
Today teams often bounce between four bad states:
1. **stay-sync by inertia** — async is avoided even when concurrency, latency, or I/O shape is already forcing it;
2. **jump-to-runtime folklore** — the answer becomes “just use runtime X” with no explicit trigger, boundary, or reversibility analysis;
3. **tutorial capture** — the async answer is inferred from whatever tutorial/framework a team happened to read first;
4. **productization capture** — service/runtime/debug/ops conclusions get decided implicitly by an early runtime choice instead of being reviewed as part of the transition.

What is missing is a reusable middle layer:
- stronger than vague warnings that async is hard,
- weaker and more honest than pretending there is one universal async lane,
- more reviewable than runtime folklore,
- and explicit enough to hand off into learning, bootstrap, workenv, debugging, and service/productization flows.

## Stack claim
A worthy contribution here is an **Async Transition Stack**: a thin control-plane surface that publishes **reviewable sync→async route decisions** without pretending that async Rust is one settled substrate.

Its job is to say:
- what the project is doing today without async;
- what exact trigger is forcing the boundary crossing now;
- which async common surfaces and runtime family are actually required;
- which lifecycle / cancellation / background-work / observability / debugger consequences follow;
- which canonical learning artifacts should be read first;
- and when staying sync, isolating async behind a boundary, or going all-in async remain serious alternatives.

This keeps **sync baseline**, **async boundary reason**, **runtime-family commitment**, **reliability/debug posture**, and **downstream productization** visibly separate.

## Boundary map
### 1) Profile and trigger framing
Owned by Profiled Onramp plus this layer.

It answers:
- what background/domain profile this team has;
- what sync baseline or current architecture exists;
- what concrete pressure is forcing async now (throughput, fan-out I/O, UI responsiveness, protocol requirements, async-only dependency, etc.);
- and whether the right answer might still be “stay sync” or “contain async behind one edge”.

It should not silently skip from “we heard async is common here” to “you now need a full async stack”.

### 2) Async common surfaces and runtime commitment
Owned by Async Commons.

It answers:
- which async capabilities are actually needed;
- what neutral shared async vocabulary exists;
- what runtime family commitments are real;
- and which adapters or portability stories remain partial.

This layer should not decide the whole migration story by itself.

### 3) Lifecycle and reliability consequences
Owned by Async Lifecycle and Async Reliability.

It answers:
- what cancellation, shutdown, task ownership, timeout, retry, stream, and background-work implications follow from the chosen async route;
- what sharp edges remain;
- and what evidence can support reliability claims.

This layer should not be replaced by framework defaults or runtime marketing.

### 4) Debugging and iteration consequences
Owned by Feedback Loop and Debuggability.

It answers:
- what build/debug loop changes the async route imposes;
- what debugger-tuple, runtime-inspection, and async-visibility posture is actually available;
- and which iteration-profile tradeoffs (debug info, target/build-dir posture, hot-reload or alternative linker tactics) remain explicit.

This layer should not be buried under “developer experience” vibes.

### 5) Canonical learning and bootstrap handoff
Owned by Canonical Learning, Profiled Onramp, and Project Bootstrap.

It answers:
- what to read first after choosing an async route;
- what examples or compare/contrast materials are canonical;
- and what starter/bootstrap/environment consequence follows from the route.

It should consume the transition decision, not improvise it from scratch.

### 6) Service/productization consequences
Owned by Service Productization and downstream stacks.

It answers:
- what runtime/settings/observability/support posture becomes active once the async route is accepted.

It should remain downstream, not the hidden authority source for why async was chosen.

## Artifact family
This layer should stay compact. A credible family would be:
- `async-transition-question/v0` — subject, current sync baseline, forcing function, latency/throughput/reliability constraints, and explicit non-goals
- `async-boundary-report/v0` — where async begins and ends, what remains sync, and what boundary styles are under consideration
- `async-route-brief/v0` — recommended route (`stay-sync`, `boundary-only`, `scoped-async`, `async-first`), runtime-family posture, major caveats, and alternatives
- `async-transition-evidence/v0` — imported async-commons, lifecycle, reliability, debug, learning, and build/iteration inputs
- `async-transition-freshness/v0` — renewal interval, roadmap triggers, and what new official/ecosystem evidence could change the answer
- `async-transition-handoff/v0` — what Canonical Learning, Project Bootstrap, Workspace Environment, Service Productization, and local overlays may import
- `async-route-pack/v0` — compact bundle for review, diffing, and rendering

Design rule: these are **transition artifacts**, not a second runtime catalog and not a disguised framework starter.

## What a worthy contribution would look like in practice
A credible contribution would look like:
- `cargo asyncroute explain <scope>`
- `cargo asyncroute compare <scope>`
- `cargo asyncroute check <scope>`
- `cargo asyncroute diff <scope>`
- `cargo asyncroute handoff <scope>`
- `cargo asyncroute pack <scope>`

or an equivalent companion layer that stays visibly above Cargo/runtime/framework choices rather than pretending it is the async runtime itself.

The important part is not the CLI spelling.
The important part is that async route decisions become:
- **trigger-based** instead of vibe-based,
- **reviewable** instead of tutorial-driven,
- **bounded** instead of silently infecting the whole architecture,
- and **renewable** instead of freezing the first runtime choice forever.

## Required async-transition dimensions
A serious transition note should name at least most of these explicitly:
- **current baseline** — sync service, sync CLI, existing threaded system, callback/event-loop integration, mixed-language host, etc.
- **forcing function** — concurrency profile, I/O multiplexing, protocol/client requirement, async-only dependency, UI responsiveness, background task fan-out, etc.
- **route class** — stay sync, isolate async behind one edge, scoped async subsystem, async-first architecture
- **runtime-family posture** — neutral/future-only, runtime-specific, multi-runtime target, embedded/no-std executor, async-agnostic but adapter-heavy, etc.
- **lifecycle risk** — cancellation, shutdown, retry, backpressure, stream termination, detached task ownership
- **debug/iteration posture** — debugger support, runtime-side inspection, debug-info profile, editor/Cargo contention, expected inner-loop cost
- **learning route** — canonical compare/contrast docs, domain examples, async-specific “chasm” warnings, and starter/bootstrap consequences
- **reversal threshold** — what facts would justify staying sync longer, narrowing the async boundary, or switching route class later

Without those axes, an async recommendation is too easy to over-read.

## Positive properties
The contribution is worthy when it:
1. reduces the sync→async “chasm of sadness” without claiming async is solved;
2. makes runtime lock-in and adapter lossiness explicit before the project hardens around them;
3. keeps lifecycle and cancellation consequences visible instead of hiding them under framework defaults;
4. gives debugging and inner-loop tradeoffs equal weight with API elegance;
5. points teams toward canonical learning artifacts rather than replacing them with folklore;
6. preserves serious alternatives like “stay sync” or “contain async at the edge”;
7. gives downstream bootstrap/workenv/service stacks a durable handoff target.

## Ranked first execution lanes
### 1. Existing sync service hitting I/O concurrency limits
Best first lane because the transition pressure is real but the current baseline is still legible.

### 2. Rust-new backend team choosing between sync and async from day one
High leverage because this is where runtime lock-in and tutorial capture usually happen.

### 3. GUI/client application needing responsiveness but not full async-everywhere architecture
Important because the official challenges post explicitly says GUI developers are punished by iteration cost and long feedback loops.

### 4. Mixed sync/async library boundary
Strategically important because it forces trait/object/runtime-interop consequences to stay explicit instead of leaking.

### 5. Embedded or special-environment async route
Valuable, but should follow once the transition machinery is proven on more common lanes.

## Non-goals
- one universal async runtime recommendation;
- replacing Async Commons, Async Lifecycle, or Async Reliability with one mega-schema;
- a hidden score that emits “best async stack” answers;
- framework-first starter templates that bury the transition reasoning;
- pretending async debugging parity already exists.

## Failure modes to resist
- **runtime capture:** letting one runtime choice silently define the whole async story.
- **framework capture:** letting a service/web/framework tutorial become the async route authority.
- **lifecycle erasure:** skipping cancellation/shutdown/background-work consequences because the demo looked good.
- **debug erasure:** acting as if stepping, inspection, and iteration costs do not matter once a runtime is chosen.
- **sync erasure:** forgetting that staying sync or containing async behind one edge can still be the better answer.

## Practical archive consequence
This seam should now sit beside **Profiled Onramp**, above **Async Commons / Async Lifecycle / Async Reliability**, and in bounded contact with **Feedback Loop / Debuggability / Project Bootstrap / Service Productization**.

In other words: the next worthy contribution is probably **not** another runtime wrapper, “best async framework” page, or generic tutorial path. It is a thin, reviewable `cargo asyncroute` / `async-route-pack/v0` layer that helps Rust teams cross the sync→async boundary honestly.
