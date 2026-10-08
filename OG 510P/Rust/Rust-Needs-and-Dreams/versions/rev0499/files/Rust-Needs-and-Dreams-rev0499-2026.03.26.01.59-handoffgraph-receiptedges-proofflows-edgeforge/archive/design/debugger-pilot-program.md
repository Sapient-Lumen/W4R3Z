# Design: Debugger pilot program (`cargo debugx`) 

## Goal
Turn the Debugger Experience Kit from a good idea into a ranked execution program that can prove real value quickly: publish honest debugger capability truth, ship reviewable visualizer artifacts, make async-inspection requirements explicit, and produce issue-attachable repro packs before the ecosystem tries to promise full debugger parity.

## Why now
The archive already argues that Rust needs a portable debugging-support substrate. What the latest signals add is a sharper execution mandate:
- The Rust debugging survey says current support varies a lot across debugger family and OS, and that a truly stellar story would require multi-debugger support, quality visualizers, first-class async debugging, and Rust expression evaluation.  
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- The 2025 State of Rust survey still lists debugging among the leading non-trivial productivity problems. It also says online docs remain canonical while LLM/editor use rises, which increases the value of attachable, machine-usable capability truth instead of folklore.  
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust already has stable debugger hooks and explicit implementation knowledge: `#[debugger_visualizer]`, toolchain wrappers like `rust-gdb` / `rust-lldb`, and compiler-dev-guide documentation on visualizer behavior, LLDB gaps, and performance hazards.  
  https://doc.rust-lang.org/reference/attributes/debugger.html  
  https://rustc-dev-guide.rust-lang.org/debuginfo/debugger-visualizers.html
- Tokio Console and `console-subscriber` prove that async inspection can be real and useful, but also prove that it currently depends on runtime-specific instrumentation, side-channel protocols, and explicit setup lore.  
  https://docs.rs/console-subscriber/latest/console_subscriber/  
  https://docs.rs/crate/tokio-console/latest

## Why this needs a pilot layer
The base Debugger Experience Kit already defines the broad artifact family (`debug-profile`, `debug-capability-report`, `viz-pack`, `async-debug-profile`, `debug-battery-report`, `debug-pack`). What it does not fully settle on its own is:
- which debugger tuples should be tested first,
- which capabilities are mandatory versus stretch goals,
- when async inspection counts as native-debug support versus side-channel support,
- when a visualizer pack is credible enough to publish,
- when expression evaluation should remain `watch` instead of being quietly implied,
- and when a pilot has proved enough to be consumed by release/support/compatibility tooling.

Without this layer, the archive risks two opposite failures:
1. **debugger-marketing theater** — projects silently claim “debugging works” after checking one tuple or one IDE path;
2. **schema theater** — rich debug schemas exist, but nobody knows which tuples, visualizers, and async lanes deserve priority now.

## Design principles
1. **Start with tuple truth, not brand claims.** The first pilots should prove support per debugger version + OS + target + toolchain tuple.
2. **Separate native and side-channel truth.** Tokio-Console-style async inspection is valuable, but it is not the same thing as native debugger stepping or expression evaluation.
3. **Visualizers are product artifacts.** A crate/library lane is only credible if the visualizer pack, coverage, compatibility bounds, and latency caveats are explicit.
4. **Regression batteries matter more than demos.** The point is not to show one happy screenshot; it is to catch breakage across debugger releases, std-layout shifts, and toolchain changes.
5. **Partial support is a valid verdict.** The pilot system must be comfortable with `partial`, `watch`, and `unsupported` outcomes.
6. **Consumers come after evidence.** Compatibility claims, release attachments, IDE integrations, and issue templates should import pilot artifacts only after the pilot earns them.

## Artifact family
### 1) `debug-pilot-brief/v0`
Explains why a debugging lane is worth piloting now:
- lane id and summary
- target user story
- why current folklore is insufficient
- tuple families involved
- likely semantic fault lines

### 2) `debug-tuple-matrix/v0`
Defines the minimum tuple coverage:
- debugger families / versions
- operating systems / targets
- toolchain channel / version posture
- wrappers / adapters used
- unsupported or deferred tuples

### 3) `debug-battery-budget/v0`
Declares what scenarios must be tested:
- std/container cases
- enum / option / result renderings
- crate visualizer scenarios
- async inspection scenarios
- expression-evaluation smoke tests
- required negative cases and flake posture

### 4) `debug-lane-profile/v0`
Specialized profile for the pilot lane:
- `native-debug`, `crate-visualizer`, `async-inspection`, `expr-eval`, or `compatibility-consumer`
- mandatory capabilities
- optional/stretch capabilities
- what must stay out of scope
- how to classify `supported` / `partial` / `watch`

### 5) `debug-readiness-scorecard/v0`
Decides whether a lane is working:
- are the tuples materially independent?
- do batteries catch real regressions?
- do capability claims stay honest?
- are visualizer / async requirements explicit enough to reuse?
- should the lane be `promote`, `pilot`, `watch`, or `defer`?

### 6) `debug-regression-pack/v0`
Bundle for regression tracking:
- before/after capability reports
- battery results
- minimized repro pointers
- transcript/log references
- suspected break source (`debugger`, `toolchain`, `std-layout`, `visualizer`, `adapter`)

### 7) `debug-pilot-pack/v0`
Bundle for publication and reuse:
- pilot brief
- tuple matrix
- battery budget
- readiness scorecard
- selected capability reports
- optional `viz-pack` / `async-debug-profile`
- support / release / issue-consumer summary

## Ranked first pilots

### 1) Std/container tuple truth lane
**Why first**
- It targets the most common everyday debugging expectation.
- It exercises the toolchain wrappers and std visualizers that Rust already ships.
- It gives the ecosystem a concrete alternative to vague “LLDB supported” prose.

**What must be explicit**
- tuple identity and versions
- std/container type families covered
- backtrace / watch / breakpoint basics
- known rendering failures and caveats
- how regressions are detected across updates

**Success bar**
A project can publish an honest tuple matrix and a battery report for common Rust types rather than only anecdotal setup instructions.

### 2) Crate visualizer release lane
**Why second**
- `#[debugger_visualizer]` makes crate-shipped debugger support a real public ergonomics surface.
- This lane tests whether visualizer support can become a releasable artifact instead of a hidden support file.

**What must be explicit**
- covered type families
- debugger families supported
- std/runtime/layout compatibility bounds
- latency / depth / performance caveats
- release attachment and CI verification posture

**Success bar**
A library can ship a `viz-pack` plus battery evidence, and downstream users can tell what was actually tested.

### 3) Async inspection lane
**Why third**
- The debugging survey explicitly calls out first-class async debugging as part of the target state.
- Tokio Console already proves that runtime-side instrumentation can surface task/resource state.
- This lane forces the archive to keep native debugging and async side-channel truth distinct.

**What must be explicit**
- runtime identity and version
- instrumentation prerequisites (`features`, env vars, unstable flags, tracing setup)
- exposed entities (tasks, resources, wait relationships, spawn locations)
- what is debugger-native versus adapter-native
- unsupported runtimes and gaps

**Success bar**
A service can publish an `async-debug-profile` that truthfully describes what can be inspected and how.

### 4) Expression-evaluation posture lane
**Why fourth**
- The debugging survey names Rust expression evaluation as part of the desired end state.
- This is exactly the kind of capability that tends to be casually implied without evidence.

**What must be explicit**
- evaluator origin (`native`, `adapter`, `none`)
- supported fragments
- unsupported constructs
- side-effect posture
- performance and stability caveats

**Expected verdict**
Likely `watch` or `partial` for a while. That is useful because it stops the archive from overclaiming parity.

### 5) Compatibility-consumer lane
**Why fifth**
- Once the earlier pilots exist, Support Envelope / Compatibility Claims can consume them.
- This proves the debugging substrate is valuable beyond debugging specialists.

**What must be explicit**
- which exported claims are suitable for release notes, support docs, or issue templates
- which facts remain advisory versus gating
- how stale claims expire

**Success bar**
Support and compatibility tools can import debugger evidence without collapsing it into one fake badge.

## Pilots to defer
These matter later, but are weaker opening bets:
- **universal debugger abstraction crates** — too likely to hide tuple differences instead of exposing them;
- **cross-runtime async-debug “standard”** — premature before the adapter truth is well mapped;
- **full Rust expression evaluators** — attractive, but too large as a first ecosystem contribution;
- **remote/cloud-debug orchestration** — valuable, but downstream of local tuple truth.

## Suggested CLI shape
- `cargo debugx pilot init`
- `cargo debugx pilot battery`
- `cargo debugx pilot diff`
- `cargo debugx pilot score`
- `cargo debugx pilot promote`
- `cargo debugx pilot watch`
- `cargo debugx pilot export`

## Phased execution
### Phase 0: scaffolding
- lock down pilot artifacts and scorecards
- define one `promote` example and one `watch` example
- keep tuple identities explicit from day one

### Phase 1: tuple truth
- ship the std/container tuple lane
- require a debugger matrix and regression battery
- make partial failures visible instead of hiding them

### Phase 2: visualizer release lane
- ship one library-backed visualizer pilot
- publish `viz-pack` and compatibility bounds
- prove release-attachment workflows are practical

### Phase 3: async inspection lane
- ship Tokio-focused async pilot first
- record instrumentation truth and side-channel boundaries explicitly
- refuse to imply native async-debug parity where it does not exist

### Phase 4: expression posture and compatibility consumers
- publish expression-eval watch/partial findings honestly
- let Support Envelope / Compatibility Claims import mature outputs

### Phase 5: expansion or refusal
- expand only if the pilots keep producing durable, regression-catching evidence
- explicitly defer lanes that remain too tuple-fragmented or too runtime-specific to standardize yet

## Archive decision
Treat Debugger Experience as a contribution that should win first by making support **honest and attachable**, not by promising a new universal debugger story. The execution anchor for that is a ranked pilot program.
