# Design: Compile-Time Capabilities Kit (`cargo ct`, `ct-pack/v0`)

## Goal
Turn compile-time execution into a **reviewable, portable, policyable boundary** by defining:
- a reference CLI (`cargo ct`),
- a canonical inventory format for compile-time execution units (`ct-unit-manifest/v0`),
- a portable description of how each unit runs (`ct-execution-lane/v0`),
- a declared authority surface (`ct-capability-profile/v0`),
- an explicit input and invalidation surface (`ct-input-surface/v0`),
- observed-execution evidence (`ct-observation-report/v0`),
- determinism and cacheability findings (`ct-determinism-report/v0`),
- diff and policy artifacts (`ct-diff-report/v0`, `ct-policy/v0`, `ct-waiver/v0`),
- a named profile catalog and profile-fit layer (`ct-profile-catalog/v0`, `ct-profile-fit-report/v0`),
- and a release / CI attachment format (`ct-pack/v0`).

This is not merely “sandbox build scripts”. The point is to give Cargo, CI, policy tools, trust tools, cache systems, and human reviewers **one shared vocabulary** for compile-time authority.

## References (signals)
- Procedural macros have the same security concerns as build scripts: https://doc.rust-lang.org/reference/procedural-macros.html
- Proc-macro crates are always compiled for the host toolchain target: https://doc.rust-lang.org/reference/linkage.html
- Build-script inputs, `OUT_DIR`, `rerun-if-*`, `links`, and build-script overrides: https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Cargo environment-variable surface: https://doc.rust-lang.org/cargo/reference/environment-variables.html
- Cargo profile build overrides for build-time crates: https://doc.rust-lang.org/cargo/reference/profiles.html
- Explore sandboxed build scripts: https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
- WebAssembly for procedural macros: https://github.com/rust-lang/compiler-team/issues/876
- Declarative macro improvements to reduce proc-macro demand: https://rust-lang.github.io/rust-project-goals/2025h1/macro-improvements.html
- User-wide build cache and idempotence inputs: https://rust-lang.github.io/rust-project-goals/2024h2/user-wide-cache.html
- Compiler performance survey: reducing build scripts / proc-macros can improve build performance: https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Cargo 1.94 dev-cycle reporting work: https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Core UX: `cargo ct`
- `cargo ct inventory`
  - enumerate all compile-time units in the selected workspace or package
  - emit `ct-unit-manifest/v0`
- `cargo ct plan`
  - resolve execution lanes and expected capability profiles
  - emit `ct-execution-lane/v0` and `ct-capability-profile/v0`
- `cargo ct check`
  - execute under the selected backend / policy and emit observation + determinism reports
- `cargo ct diff --against <pack|ref|artifact>`
  - compare declarations, lanes, observations, and determinism findings against a baseline
- `cargo ct profiles`
  - emit the built-in `ct-profile-catalog/v0`
- `cargo ct fit --profile <name>`
  - compare a subject against a named compile-time profile and emit `ct-profile-fit-report/v0`
- `cargo ct policy-check`
  - apply `ct-policy/v0` and emit stable reason codes
- `cargo ct pack`
  - bundle artifacts into `ct-pack/v0`
- `cargo ct verify-pack <path>`
  - verify schema versions, tool identities, digests, and attachment references
- `cargo ct explain <reason-code>`
  - decode why a result is pass / warn / fail / waived / unsupported

## Artifacts
### `ct-unit-manifest/v0`
Canonical inventory of compile-time execution units:
- package/crate identity, version, source, workspace membership
- unit kind:
  - `build-script`
  - `proc-macro`
  - `links-override`
  - `declared-no-run` (future lane for declarative replacements)
- host triple, target triple(s), profile, feature/cfg selection
- build-dependency graph slice relevant to the unit
- `package.links` identity where relevant
- whether the unit is always-run, change-detected, or overridden

Design rule: inventory is separate from permissions and separate from observations.

### `ct-execution-lane/v0`
How the unit is expected to execute:
- lane class:
  - `native-build-script`
  - `native-proc-macro`
  - `wasm-proc-macro`
  - `links-metadata-override`
  - `external-sandbox-wrapper`
- backend/runtime identity and version
- host/target posture
- whether execution is local, remote-execution-ready, or not portable
- whether the lane is experimental / unstable / upstream / third-party

Design rule: “what kind of thing this is” and “how it runs” are related but not identical truths.

### `ct-capability-profile/v0`
Declared authority for a compile-time unit:
- filesystem read scopes
- filesystem write scopes
- env-var read scopes
- process-spawn scopes
- network access scopes
- time/clock/randomness posture
- native-library probe posture
- toolchain / metadata read posture
- declared outputs (`OUT_DIR`, emitted directives, metadata keys)
- declaration source (crate-authored, workspace policy, inferred default)

Design rule: declarations should be narrow, path- or name-scoped where possible, and source-labeled.

### `ct-input-surface/v0`
What should be treated as an input or invalidation trigger:
- files and directories declared by `rerun-if-changed`
- environment variables declared by `rerun-if-env-changed` or otherwise used
- source/package metadata inputs
- system-library / pkg-config / compiler-probe inputs
- host and target assumptions
- whether the input surface is explicit, partial, or unknown

This artifact exists because permissions and inputs are not the same thing. A build script may be allowed to read a file but still fail to declare it as a rebuild input.

### `ct-observation-report/v0`
Observed execution evidence:
- actual file reads/writes (scoped / redacted as needed)
- environment variables read
- processes spawned
- network attempts / successes / denials
- emitted Cargo directives / metadata
- outputs created under `OUT_DIR`
- backend-enforcement notes and unsupported blind spots
- stable reason codes such as:
  - `CT:OBSERVED-UNDECLARED-ENV`
  - `CT:OBSERVED-NETWORK`
  - `CT:OUT-DIR-ESCAPE-ATTEMPT`
  - `CT:PROCESS-SPAWN-OUTSIDE-POLICY`

### `ct-determinism-report/v0`
Findings about reproducibility, idempotence, and cacheability:
- whether the unit is deterministic, conditionally deterministic, or not yet known
- undeclared inputs discovered from observation
- host-only or target-sensitive behavior
- use of clocks, random sources, or network
- build-script invalidation quality (`rerun-if-*` posture, broad package scans, unknown inputs)
- whether the unit is eligible for stricter caching / remote execution / repro verification under current evidence
- reason codes such as:
  - `CT:INPUT-SURFACE-INCOMPLETE`
  - `CT:HOST-TARGET-LANE-DRIFT`
  - `CT:NONDETERMINISTIC-INPUT`
  - `CT:CACHEABILITY-UNKNOWN`

### `ct-diff-report/v0`
Comparison artifact for review:
- added / removed / changed compile-time units
- lane changes (native → wasm, executed → overridden, etc.)
- capability drift
- input-surface drift
- observation drift
- determinism verdict drift
- new waivers or removed waivers

### `ct-policy/v0`
Org or project policy:
- allowed lane classes
- default-deny or default-allow posture by unit kind
- special rules for proc-macros vs build scripts
- network/process restrictions
- approval requirements for waivers
- allowed blind spots / unsupported lanes
- fail/warn/review handling for each reason code class

### `ct-waiver/v0`
Explicit exceptions:
- subject and scope
- reason / owner / approver
- time window / expiry
- bounded capabilities granted
- whether the waiver is temporary migration debt, permanent platform need, or emergency unblock

### `ct-profile-catalog/v0`
A named catalog of compile-time governance profiles.

Each profile records:
- intended unit kinds and lane classes
- required declaration quality
- required observation coverage
- determinism / cacheability expectations
- allowed waiver classes
- whether the profile is primarily about observation, narrowing, isolation, replacement, or migration

The initial built-in ladder should align with [`design/compile-time-profile-ladder.md`](./compile-time-profile-ladder.md):
- `ambient-observed`
- `declared-native`
- `narrow-native`
- `portable-sandbox`
- `declared-no-run`
- `language-first`

### `ct-profile-fit-report/v0`
A report comparing one workspace / package / unit against one or more named profiles.

It should record:
- subject identity
- requested profile
- current fit (`meets`, `meets-with-waivers`, `does-not-meet`, `unknown`)
- blocking reason codes
- evidence used (declarations, observations, determinism, replacement reports, migration hints)
- recommended next move:
  - narrow authority
  - improve declarations
  - replace imperative steps
  - reduce proc-macro demand
  - migrate toward language-first compile-time lanes

Design rule: profile-fit is transition evidence, not a compliance verdict by itself.

### `ct-pack/v0`
Bundle for CI, trust, and release workflows:
- `manifest.json`
- `ct-unit-manifest.json`
- `ct-execution-lane.json`
- `ct-capability-profile.json`
- `ct-input-surface.json`
- `ct-observation-report.json` (optional)
- `ct-determinism-report.json` (optional)
- `ct-diff-report.json` (optional)
- `ct-policy.json` (optional)
- `ct-waiver.json` (optional)
- `ct-profile-catalog.json` (optional)
- `ct-profile-fit-report.json` (optional)
- checksums / provenance / schema versions
- optional attachment refs for sandbox logs, redacted traces, or imported Cargo reports

## Design principles
- **Compile-time authority is its own boundary.** Do not bury it inside generic supply-chain or runtime-permission tooling.
- **Execution lane matters.** Native proc-macro, wasm proc-macro, build script, and declarative override are not interchangeable.
- **Declared, observed, and deterministic truths stay separate.** A crate can declare one thing, do another, and still have incomplete invalidation logic.
- **Overrides are first-class, not hacks.** Replacing a `links` build script with declared metadata is a distinct lane that should get positive support.
- **Transition-friendly.** As language features or declarative macros eliminate some proc-macro/build-script use cases, the kit should record that migration rather than pretending all compile-time code remains equally necessary.
- **Profiles over false binaries.** The ecosystem needs named ladders such as observe → declare → narrow → sandbox → replace / migrate, not just “safe” versus “unsafe”.
- **Policyable without log scraping.** Stable reason codes and compact packs matter more than a flashy UI.

## What the kit should provide to others
- **Security / platform teams:** one evidence boundary for compile-time code execution in dependency graphs.
- **Crate authors:** a way to declare what their build surface actually needs and prove when it stays within bounds.
- **Cargo and cache work:** explicit idempotence and input-surface facts instead of guesses.
- **Trust / policy tools:** explainable compile-time evidence to consume, rather than treating all build dependencies the same.
- **Reviewers:** a clear answer to “what ran at compile time, under what authority, and could we have avoided running it?”

## Integration points
- **Policy Kit** for org-wide allow/deny decisions.
- **Trust Signals Kit** for exposing compile-time authority posture as one signal class.
- **Build Cache Kit** for determining when compile-time units are eligible for broader cache reuse.
- **Repro Build Kit** for consuming determinism findings and packs.
- **Macro Workflow Kit** for inventory/debug/cost surfaces above the authority boundary.
- **Compile-Time Profile Ladder** for named graduation targets and blocker semantics.
- **Build Extension Kit** for cases where declarative build extensions can replace arbitrary execution.
- **Native Dependency Kit** for structured `-sys` discovery and provider-lock flows.
- **Release Pipeline Kit** when projects want to attach compile-time authority evidence to releases.

## Hard problems (explicitly scoped)
1. **`-sys` reality and native probing**
   - many legitimate build scripts need to probe host libraries or toolchains; the kit must model that honestly instead of pretending all probes are bad.
2. **Sandbox backend portability**
   - OS sandboxes, external wrappers, and wasm runtimes will differ in what they can observe or enforce.
3. **Proc-macro ergonomics and debugging**
   - isolated execution is good, but the kit should not pretend that debugging and performance costs vanish.
4. **Host vs target confusion**
   - proc-macros are host artifacts; builds may target something else entirely.
5. **Partial evidence**
   - some lanes will have blind spots; the format must say so explicitly.
6. **Migration burden**
   - crates will need paths from today’s ambient authority to narrower declarations or declarative replacements.

## Overlap boundaries
- **Not Runtime Capability Kit:** that kit governs application/runtime authority after the program starts; this kit governs compile-time execution.
- **Not Macro Workflow Kit:** macro inventory, expansion, debugging, and migration planning remain separate from permissioning and determinism evidence.
- **Not Build Extension Kit:** declarative build extensions reduce the need for arbitrary execution; Compile-Time Capabilities Kit governs the execution that still exists.
- **Not Trust Signals Kit:** trust tooling consumes compile-time evidence, but does not define its schema.
- **Not one “safe build” badge:** the ecosystem needs lane, capability, observation, determinism, and waiver truth kept distinct.

## Evaluation plan
Pilot on three project classes:
1. a pure-Rust workspace with proc-macro-heavy derives,
2. a `-sys` crate that probes and links native libraries,
3. an enterprise workspace that wants deny-network and narrow-env defaults in CI.

Success bar:
- maintainers can inventory compile-time units without bespoke scripts,
- CI can diff compile-time authority drift between revisions,
- policy can gate on stable reason codes,
- deterministic / cacheable lanes become explicit,
- and reviewers can distinguish “executed natively”, “executed in wasm”, and “not executed because metadata override supplied” without reading tribal lore.

## Role in the Compile-Time Surface pilot program
This kit should now be treated as the **authority anchor** inside [`design/compile-time-surface-pilot-program.md`](./compile-time-surface-pilot-program.md).
Its job is not to absorb macro debugging, declarative replacement, or script sharing. Its job is to make compile-time execution reviewable enough that those adjacent layers can compose on top of it without rebuilding hidden trust logic.
