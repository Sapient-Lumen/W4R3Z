# Frontier delivery cards — 2026-03-25

This note answers a practical question more directly than the archive usually does:

**What should the crate provide other people in a first usable release?**

The cards below are intentionally receiver-first.
Each one names:
- who gets value,
- what recurring pain is removed,
- what concrete artifact family the crate emits,
- what the first narrow release should be,
- what it refuses to do,
- and what success would look like in practice.

## 1. P-0509 — Crate Ecosystem Pathfinder & Decision-Pack Kit

### One-line promise
Turn ecosystem choice into a small, reviewable, replayable decision packet instead of a pile of tacit lore.

### Who receives value
- new Rust teams,
- staff/platform engineers defining starter stacks,
- educators picking defaults,
- security or policy teams that need reviewable crate choices.

### The recurring pain
People can search crates, read docs, and browse blog posts, but they still cannot easily produce a **portable decision artifact** for “which crates fit this task under these constraints?”

### First useful release
Ship one narrow but honest workflow:
- input: `task-profile.json`
- output: `candidate-import.report.json`, `decision-pack.report.json`, `starter-set.lock.json`, `decision.summary.md`

Support only a few named lanes at first:
- `cli_app`
- `async_http_service`
- `desktop_gui_shell`
- `embedded_no_std_baseline`

### What it should provide other people
- a frozen starter-set answer;
- the plausible alternatives that lost;
- explicit constraint handling (`no_std`, runtime policy, MSRV floor, license posture, target set);
- a recheck policy explaining when the answer must be revisited.

### What it should import, not reinvent
- crate metadata and security/advisory surfaces;
- knowledge packs from **P-0536**;
- health/support posture from existing archive lanes.

### Refusal boundary
It is **not** a universal recommender, popularity oracle, or autonomous trust engine.

### First success test
Another team should be able to check in the output, review it in code review, and explain why their chosen stack beat the runner-up without reopening ten browser tabs.

## 2. P-0536 — Crate Knowledge Pack Kit

### One-line promise
Package the crate’s visible truth into a cited, replayable review bundle that humans and tools can both consume.

### Who receives value
- support engineers,
- internal docs/tooling teams,
- assistant/retrieval systems,
- platform teams that need frozen evidence rather than live pages.

### The recurring pain
A crate’s truth is spread across docs.rs pages, rustdoc JSON, package contents, README prose, examples, and target/feature conditionals.

### First useful release
Ship a narrow pack that joins:
- `basis-lock.manifest.json`
- `review-packet.manifest.json`
- `citation-locator.receipt.json`
- `identity-fidelity.report.json`
- `build-surface.receipt.json`
- optional `notes.md`

### What it should provide other people
- a pinned basis for later review;
- a way to cite a specific visible item or claim;
- a way to say what target/feature/build recipe shaped the visible surface;
- a claim ceiling when item identity is fuzzy or target-conditioned.

### What it should import, not reinvent
- docs.rs downloads and rustdoc JSON;
- package tarball contents;
- official Cargo/docs.rs semantics;
- optional imported receipts from parity or support lanes.

### Refusal boundary
It is **not** a new docs host, a generic chat UI, or a promise that rustdoc HTML is a stable API.

### First success test
A downstream tool should be able to answer “what exactly did we look at, under what conditions, and how do we cite it again later?” without scraping live pages ad hoc.

## 3. P-0472 — Docs.rs Build Parity & Evidence Kit

### One-line promise
Make hosted-doc differences reviewable instead of surprising.

### Who receives value
- crate authors,
- docs/tooling maintainers,
- teams relying on docs.rs as their public surface,
- downstream reviewers trying to understand why local and hosted docs differ.

### The recurring pain
docs.rs uses a sandboxed nightly environment with its own target/feature/build behavior.
That is enormously useful, but “it builds on my machine” still is not the same as “it builds and appears correctly on docs.rs”.

### First useful release
Ship:
- `docsrs-preflight.receipt.json`
- `hosted-local-diff.report.json`
- `target-visibility.report.json`
- `docsrs-support-bundle.manifest.json`

### What it should provide other people
- explicit parity/non-parity between local and hosted docs;
- target/default-target differences;
- a summary of what docs.rs build conditions mattered;
- a portable support bundle for issue reports and release review.

### What it should import, not reinvent
- docs.rs build docs and download surfaces;
- local cargo/rustdoc invocation facts;
- knowledge-pack basis locks where useful.

### Refusal boundary
It is **not** a replacement for docs.rs, a doc renderer, or a generic offline-doc portal.

### First success test
A maintainer should be able to explain a docs.rs discrepancy with one diff bundle instead of a long issue thread.

## 4. P-0484 — Toolchain & Target Support Contract Kit

### One-line promise
Turn “supported on this target/toolchain” from hand-wavy text into receipts and support bundles.

### Who receives value
- crate maintainers shipping across targets,
- embedded and systems teams,
- organizations with explicit support policies,
- security/safety reviewers.

### The recurring pain
Target support, toolchain floors, component requirements, and target-specific caveats are often implicit, stale, or scattered.

### First useful release
Ship:
- `toolchain-intent.receipt.json`
- `target-support.report.json`
- `component-availability.report.json`
- `support-bundle.manifest.json`

### What it should provide other people
- explicit supported/unsupported/untested target posture;
- toolchain floor and optional-component truth;
- target-specific caveats and claim ceilings;
- a diffable support statement across releases.

### What it should import, not reinvent
- `rust-toolchain.toml`
- CI matrices
- docs.rs default-target behavior where relevant
- target-tier and official toolchain guidance

### Refusal boundary
It is **not** a cross-compilation framework, CI platform, or universal binary builder.

### First success test
A receiver should be able to tell whether “works on ARM Linux with this MSRV and these components” is a tested claim, a policy claim, or merely an aspiration.

## 5. P-0535 — Dependency Lifecycle Transition Kit

### One-line promise
Make dependency posture changes reviewable as transitions rather than silent rewrites of old decisions.

### Who receives value
- long-lived product teams,
- regulated adopters,
- orgs with offline or high-assurance profiles,
- maintainers handling advisories, abandonware risk, or replacement planning.

### The recurring pain
A crate choice is rarely permanent, but most teams do not have a clean artifact for “the original answer was acceptable then; here is why it must be revisited now.”

### First useful release
Ship:
- `trigger-intake.receipt.json`
- `decision-revalidation.report.json`
- `transition-review-packet.manifest.json`
- `replacement-readiness.report.json`

### What it should provide other people
- a durable distinction between old basis and new signal;
- a reasoned transition path when posture changes;
- replacement or internalization planning;
- a clearer story for safety-critical / long-lived adopters.

### What it should import, not reinvent
- frozen pathfinder decisions;
- security/advisory signals;
- support/health/source-parity receipts from adjacent lanes.

### Refusal boundary
It is **not** a dependency bot, vulnerability scanner, or generic package manager.

### First success test
A team should be able to say “we are not silently changing our answer; we are opening a transition review because this trigger class fired.”

## 6. P-0486 — Debuggability Support Contract Kit

### One-line promise
Export what debug support a release really provides instead of making people infer it from failure.

### Who receives value
- maintainers of deployed binaries and SDKs,
- support engineers,
- downstream integrators,
- teams operating in desktop, service, embedded, or safety-sensitive environments.

### The recurring pain
Users often do not know what symbols, pretty-printers, debug sidecars, probes, or debugger compatibility a release actually ships with until something goes wrong.

### First useful release
Ship:
- `debug-support.receipt.json`
- `symbol-sidecar.manifest.json`
- `debugger-compatibility.report.json`
- `debug-support-bundle.manifest.json`

### What it should provide other people
- explicit support posture for symbolication/debugging;
- sidecar locations and compatibility notes;
- what kinds of postmortem or live debugging are in scope;
- non-claims when the answer is “manual review only”.

### What it should import, not reinvent
- release artifacts,
- symbol files and packaging receipts,
- toolchain/target support receipts,
- existing debugger ecosystem facts where available.

### Refusal boundary
It is **not** a debugger, profiler, or crash collector.

### First success test
A downstream operator should be able to answer “what can I actually debug from this release bundle?” without guesswork.

## 7. P-0538 — Concurrency Contract Kit

### One-line promise
Make concurrency semantics exportable and comparable without pretending that one runtime or primitive family owns the whole truth.

### Who receives value
- maintainers of async/sync primitives,
- service teams,
- library authors exposing waitable surfaces,
- support engineers untangling deadlocks, starvation, and cancellation bugs.

### The recurring pain
Important concurrency semantics still live in prose and local folklore: reentrancy, fairness, cancellation safety, closure, lag, observation evidence, and progress conditions.

### First useful release
Keep the first release narrow and evidence-heavy:
- hand-author or semi-derive support bundles for a small comparison set (`std`, `tokio`, `parking_lot`);
- emit `reentrancy-scope.report.json`, `wait-cancellation.report.json`, `progress-fairness.report.json`, `execution-context-boundary.report.json`, and `concurrency-support-bundle.manifest.json`.

### What it should provide other people
- one explicit answer per semantic axis;
- one claim ceiling when the docs or tests are not strong enough;
- comparable vocabulary across primitive families.

### What it should import, not reinvent
- official docs,
- model-checking or test evidence when available,
- runtime-specific support notes,
- manually reviewed scenario packets.

### Refusal boundary
It is **not** a theorem prover, executor abstraction, or guarantee that all concurrency bugs are prevented.

### First success test
A reviewer should be able to compare two candidate primitives and see where the semantic differences really are, instead of reading three docs pages and improvising.

## Cross-card product lesson

The strongest epic crates in the archive still have the same structural shape:

1. **narrow first release**;
2. **portable artifact family**;
3. **clear refusal boundary**;
4. **import-friendly stance toward existing substrate**;
5. **explainable receiver value**;
6. **recheck/diff story**.

If a proposal cannot yet produce a convincing delivery card in this format, it is probably still a territory note rather than a build candidate.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://rust-lang.github.io/rust-project-goals/2025h1/cargo-plumbing.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://docs.rs/releases/queue
- https://www.arewewebyet.org/
- https://www.areweguiyet.com/
- https://arewegameyet.rs/
- https://www.arewelearningyet.com/
- https://github.com/rust-embedded/not-yet-awesome-embedded-rust
- https://georust.org/
- https://automerge.org/
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
- https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
