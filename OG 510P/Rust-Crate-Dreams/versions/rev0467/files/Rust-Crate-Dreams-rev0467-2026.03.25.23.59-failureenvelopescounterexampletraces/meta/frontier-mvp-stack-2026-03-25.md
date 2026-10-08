# Frontier MVP stack — 2026-03-25

This note turns the current frontier into concrete `0.1`-style build plans.

The question here is not just “what is important?”
It is:

**if we started building now, what should the crate look like in theory and practice?**

The stack below is intentionally receiver-first and artifact-first.

---

## 1. P-0509 — Crate Ecosystem Pathfinder & Decision-Pack Kit

### Core promise
Turn crate choice into a replayable decision packet rather than a browser-tab ritual.

### First release scope
Support only a few named lanes:
- `cli_app`
- `async_http_service`
- `desktop_gui_shell`
- `embedded_no_std_baseline`

### Library shape
- `profiles` — task/profile parsing and validation
- `candidates` — candidate set assembly from imported evidence
- `evaluation` — constraint handling and comparison logic
- `pack` — emit reviewable outputs
- `recheck` — trigger/open-review helpers

### CLI shape
- `pathfinder init-profile`
- `pathfinder import-candidates`
- `pathfinder evaluate`
- `pathfinder freeze`
- `pathfinder summarize`

### Expected outputs
- `task-profile.json`
- `candidate-import.report.json`
- `decision-pack.report.json`
- `starter-set.lock.json`
- `decision.summary.md`

### Imports
- crates.io trust/security posture
- docs.rs and package knowledge packs from **P-0536**
- optional target/support imports from **P-0484**
- optional lifecycle/recheck imports from **P-0535**

### Test corpus
At minimum:
- CLI stack where `clap` / `argh` / `bpaf` or equivalent shape the choice
- async HTTP service stack where runtime/runtime-policy matters
- GUI shell stack where docs/build/target support claims are uneven
- embedded baseline where `no_std` and target constraints dominate

### Explicit non-goals
- universal recommendations
- popularity oracle
- automatic trust verdicts
- a general package search engine

### What other people get
A team should be able to check in the packet and say:
“this stack won for this task, under these constraints, on this evidence basis, and here is when we must revisit it.”

---

## 2. P-0536 — Crate Knowledge Pack Kit

### Core promise
Freeze a crate’s visible basis into a cited review bundle.

### First release scope
Focus on one package version at a time, default target first, with optional additional target notes.

### Library shape
- `package_basis` — package tarball / manifest / packaged-state intake
- `docs_basis` — docs.rs downloads, rustdoc JSON, and hosted-surface notes
- `identity` — item identity and citation locators
- `bundle` — emit review packet / lock files
- `surface` — build/target/feature notes

### CLI shape
- `knowledge-pack capture`
- `knowledge-pack cite`
- `knowledge-pack verify`
- `knowledge-pack bundle`

### Expected outputs
- `basis-lock.manifest.json`
- `review-packet.manifest.json`
- `citation-locator.receipt.json`
- `identity-fidelity.report.json`
- `build-surface.receipt.json`

### Imports
- docs.rs build rules, downloads, and rustdoc JSON
- packaged crate contents
- Cargo metadata where appropriate

### Test corpus
- crate with docs.rs-only metadata differences
- crate with target-conditioned docs surface
- crate whose rustdoc JSON format/version caveat matters
- crate whose downloaded docs archive has offline caveats

### Explicit non-goals
- docs hosting replacement
- general-purpose search index
- stable parsing promise over every historical rustdoc JSON variant in `0.1`

### What other people get
A support engineer, reviewer, or assistant should be able to say exactly what was looked at and cite it again later.

---

## 3. P-0472 — Docs.rs Build Parity & Evidence Kit

### Core promise
Make hosted docs surprises reviewable before they hit users.

### First release scope
Compare local docs-rs-style builds against hosted docs expectations for a single crate release.

### Library shape
- `preflight` — local docs.rs-style build runner
- `diff` — hosted/local surface comparison
- `targets` — default-target and visibility reporting
- `bundle` — portable issue/support bundle

### CLI shape
- `docsrs-parity preflight`
- `docsrs-parity diff`
- `docsrs-parity explain`
- `docsrs-parity bundle`

### Expected outputs
- `docsrs-preflight.receipt.json`
- `hosted-local-diff.report.json`
- `target-visibility.report.json`
- `docsrs-support-bundle.manifest.json`

### Imports
- docs.rs build conditions
- docs.rs target defaults and metadata
- local `cargo docs-rs` or equivalent reproduction route
- optional basis lock from **P-0536**

### Test corpus
- crate that builds locally but fails or differs on docs.rs
- crate affected by default-target changes
- crate with workspace dependency/docs surface differences

### Explicit non-goals
- generic documentation build orchestrator
- full offline docs viewer
- a universal rustdoc frontend

### What other people get
A maintainer should get one bundle that explains why the hosted surface differed.

---

## 4. P-0484 — Toolchain & Target Support Contract Kit

### Core promise
Export what support is tested, intended, or unknown across targets and toolchains.

### First release scope
One repository or release at a time, with a bounded target set.

### Library shape
- `intent` — ingest support declarations and CI expectations
- `evidence` — CI/toolchain/component results
- `classification` — supported / untested / unsupported / conditional
- `bundle` — emit support packet

### CLI shape
- `support-contract ingest`
- `support-contract evaluate`
- `support-contract diff`
- `support-contract bundle`

### Expected outputs
- `toolchain-intent.receipt.json`
- `target-support.report.json`
- `component-availability.report.json`
- `support-bundle.manifest.json`

### Imports
- CI matrices
- `rust-toolchain.toml`
- docs.rs target notes
- official platform/target policy references where appropriate

### Test corpus
- crate with declared MSRV but uneven CI reality
- crate with docs.rs target success but missing runtime support
- Rust-for-Linux or embedded-like target caveat cases
- mixed Apple/Linux ARM and x86 support transitions

### Explicit non-goals
- full CI service replacement
- cross-compilation toolchain manager
- binary build/distribution service

### What other people get
A release or platform owner should be able to distinguish aspiration from tested support.

---

## 5. P-0535 — Dependency Lifecycle Transition Kit

### Core promise
Make changed dependency posture reviewable without rewriting history.

### First release scope
Open one transition packet off one trigger class.

### Library shape
- `triggers` — advisory / trust / build / policy trigger intake
- `revalidation` — old basis versus new signal
- `replacement` — bounded replacement/internalization planning
- `transition` — emit review packet

### CLI shape
- `lifecycle intake`
- `lifecycle revalidate`
- `lifecycle plan-replacement`
- `lifecycle bundle`

### Expected outputs
- `trigger-intake.receipt.json`
- `decision-revalidation.report.json`
- `replacement-readiness.report.json`
- `transition-review-packet.manifest.json`

### Imports
- pathfinder decision packets
- knowledge-pack basis locks
- crates.io/RustSec trust signals
- support/source-parity receipts from adjacent lanes

### Test corpus
- advisory opened on a previously accepted dependency
- trusted-publishing posture changes without immediate breakage
- safety-critical profile needing internalization planning
- source-parity or public-boundary signal opening review

### Explicit non-goals
- dependency bot
- vulnerability scanner replacement
- package manager

### What other people get
A team should be able to say why the answer was reopened and what transition path is under review.

---

## 6. P-0486 — Debuggability Support Contract Kit

### Core promise
Export actual debug-support posture as a durable release artifact.

### First release scope
Single binary/library release, bounded debugger/OS matrix, clear async claim ceiling.

### Library shape
- `symbols` — symbol and sidecar inventory
- `compat` — debugger/version/OS notes
- `support` — classify supported workflows
- `bundle` — emit debug support packet

### CLI shape
- `debug-contract capture`
- `debug-contract classify`
- `debug-contract diff`
- `debug-contract bundle`

### Expected outputs
- `debug-support.receipt.json`
- `symbol-sidecar.manifest.json`
- `debugger-compatibility.report.json`
- `debug-support-bundle.manifest.json`

### Imports
- package/release artifacts
- build settings and symbol generation facts
- optional target/toolchain and knowledge-pack imports
- explicit debugger/version matrices

### Test corpus
- stripped vs unstripped release artifacts
- async stack with limited debugger capability
- cross-platform mismatch across GDB/LLDB/CDB-like families
- postmortem-only support case

### Explicit non-goals
- complete debugger implementation
- full async semantic debugger
- support for every debugger on day one

### What other people get
Operators and support teams should know what they can actually do before the incident happens.

---

## Shared MVP guardrails

Across the stack:
1. prefer imported real substrate over invented substrate;
2. emit machine-readable artifacts first and prose summaries second;
3. keep refusal boundaries explicit;
4. keep one bounded scenario corpus per crate;
5. and design `0.1` so another team could actually pilot it.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://blog.rust-lang.org/2025/10/16/docsrs-changed-default-targets/
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-semver-checks.html
- https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- https://rust-lang.github.io/rust-project-goals/2025h1/rfl.html
- https://rust-lang.github.io/rust-project-goals/2025h1/seamless-rust-cpp.html
- https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
