# Design: Feedback Loop pilot program (`cargo innerloop pilot`, `feedback-loop-pack/v0`)

## Why this needs a pilot program
The archive already has two strong ingredients:
- [`design/build-state-evidence-stack.md`](./build-state-evidence-stack.md)
- [`design/debuggability-stack.md`](./debuggability-stack.md)

What it still lacked was the ranked execution layer that says **how these become one credible ecosystem contribution instead of two adjacent frontier stacks**.

Current Rust/Cargo signals make the timing unusually good:
- resource usage and debugging remain top productivity complaints;
- Cargo is finally giving build sessions, rebuild reasons, and timing history machine-readable shape;
- build-dir layout and locking work are making Cargo ↔ rust-analyzer coexistence a first-class engineering problem instead of a mere FAQ workaround;
- debugging support is being re-interrogated at the ecosystem level through an official survey;
- and Cargo keeps explicitly signaling that companion plugins are the right place for some higher-level tooling contracts.

That combination suggests a practical rollout: start from explicit session identity, then prove editor/build coexistence, then prove build→debug handoff, and only after that widen toward issue/support/assistant consumers.

## References (signals)
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- 2025 compiler-performance survey:
  https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- Cargo build-analysis goal:
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- Build-dir-layout goal:
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- Build-dir-layout-v2 testing call:
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Debugging survey 2026:
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Cargo 1.94 development cycle:
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/

## Design principles
1. **Start from one concrete session.** “Developer experience trends” can come later.
2. **Import before summarizing.** Build-state and debug packs should remain visible instead of being absorbed.
3. **Prefer everyday loop pain first.** Editor contention, rebuild churn, debug-info tradeoffs, and tuple-specific debugger gaps beat grand platform ambitions.
4. **Keep consumer lanes late and explicit.** Support pages and assistants should widen only after the core evidence boundary works.
5. **Do not pretend Cargo internals are stable.** The pilot may import unstable report surfaces honestly.

## Shared pilot artifacts
### `feedback-loop-brief/v0`
A short declaration of why a loop lane is being piloted.

Should record:
- pilot id
- lane family (`session-identity`, `editor-cli`, `build-debug-handoff`, `consumer-summary`, `assistant-consumer`)
- subject kind (`workspace`, `package`, `binary`, `service`, `tool`)
- intended tool tuple (Cargo/toolchain/editor/debugger/runtime-inspection family)
- intended consumers and success bar

### `feedback-loop-session/v0`
One concrete loop session.

Should record:
- stable session id
- selected workflow (`check`, `build`, `test`, `clippy`, `run`, `debug`, `profile`)
- build/session ids such as `CARGO_RUN_ID` where available
- target/profile/debug-info posture
- target-dir / build-dir policy
- optional change-slice or edit-application import
- optional semantic-context import
- user intent class (`iterate`, `triage`, `repro`, `support`, `ci-debug`)

### Core imports from existing stacks
- `build-state-pack/v0`
- `impact-pack/v0`
- `build-doctor-pack/v0`
- `diagnostic-pack/v0`
- `obs-pack/v0`
- `debug-pack/v0`
- `debuggability-pack/v0`
- optional `change-slice/v0`, `edit-application-report/v0`, `semctx-pack/v0`
- optional replay / incident / test attachments

### `feedback-loop-pack/v0`
Portable bundle for one pilot lane.

Should contain:
- the pilot brief
- one or more loop sessions
- linked build/debug evidence
- explicit tradeoff markers
- consumer-facing caveats and unresolved gaps

Design rule: **this pack is a composition envelope, not a mega-schema that absorbs the underlying stacks.**

## Ranked rollout

### Pilot 1 — Session identity lane
Start with the smallest credible claim.

Artifacts:
- `feedback-loop-brief/v0`
- `feedback-loop-session/v0`
- pointers to raw Cargo/build/debug session IDs where available

Success bar:
- a team can name and diff one real build/debug session without relying on shell history or issue-thread prose;
- build/run/debug tuple assumptions are explicit;
- missing change provenance is rendered honestly.

### Pilot 2 — Editor / CLI coexistence lane
The first practical pain lane.

Artifacts:
- session record
- `build-state-pack/v0`
- `impact-pack/v0`
- `build-doctor-pack/v0`

Success bar:
- shared-vs-separated build-dir / target-dir posture is explicit;
- lock contention, duplication, and policy tradeoffs can be explained honestly;
- the result can import Cargo report surfaces without pretending they are already stable forever.

### Pilot 3 — Build → debugger handoff lane
Link iteration evidence to actual debugging evidence.

Artifacts:
- session record
- build-state evidence imports
- `diagnostic-pack/v0`
- `debug-pack/v0` or `debuggability-pack/v0`
- optional `obs-pack/v0`

Success bar:
- a slow or failed iteration can move from build evidence into tuple-aware debugger or runtime-inspection evidence without issue archaeology;
- native debugger support versus side-channel inspection remains explicit;
- debug-info or profile tradeoffs remain part of the record.

### Pilot 4 — Issue / support / docs consumer lane
Only after core evidence is stable, test bounded consumer summaries.

Artifacts:
- feedback-loop pack
- one or more `feedback-loop-handoff/v0` summaries

Consumers:
- issue templates
- support pages
- migration notes
- release/debuggability notes

Success bar:
- consumer summaries do not overclaim;
- they preserve whether claims came from build evidence, debug evidence, or imported change context.

### Pilot 5 — Assistant/editor consumer lane
Widen only after the human-facing lane works.

Artifacts:
- feedback-loop pack
- assistant/editor-specific handoff summary
- explicit lossiness markers

Success bar:
- an assistant or editor can consume loop evidence without pretending to know hidden local state;
- session provenance, imported evidence, and uncertainty survive summarization.

## What should count as success overall
The stack is working when:
- one loop session is identifiable and reviewable,
- Cargo/build evidence and debugger/diagnostic evidence can be linked without flattening,
- target-dir / build-dir / debug-info tradeoffs are visible rather than rediscovered,
- issue/support/docs consumers can import bounded summaries,
- and assistant/editor tooling can consume the result without becoming the source of truth.

## Failure modes to avoid
- starting from a giant IDE platform;
- flattening build facts and debug facts into one score;
- treating runtime-side inspection as native debugger parity;
- hiding unstable Cargo report dependencies behind fake stability claims;
- widening to assistant workflows before the human-readable evidence boundary is stable.

## Immediate archive instruction
Treat this file plus [`design/feedback-loop-stack.md`](./feedback-loop-stack.md) as the shared execution layer above Build-State Evidence Stack and Debuggability Stack.

The next credible feedback-loop move is now a ranked stack program:
1. session identity,
2. editor / CLI coexistence,
3. build → debugger handoff,
4. issue / support / docs consumers,
5. assistant/editor consumers.
