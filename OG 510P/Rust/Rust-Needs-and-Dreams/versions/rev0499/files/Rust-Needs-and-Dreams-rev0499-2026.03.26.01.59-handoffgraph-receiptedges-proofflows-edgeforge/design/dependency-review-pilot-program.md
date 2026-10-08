# Design: Dependency Review pilot program (`cargo dep-review pilot`, `dependency-review-pack/v0`)

## Why this needs a pilot program
The archive already has strong ingredients for supply-chain and dependency review:
- [`design/trust-decision-stack.md`](./trust-decision-stack.md)
- [`design/runtime-capability-kit.md`](./runtime-capability-kit.md)
- [`design/sbom-evidence-kit.md`](./sbom-evidence-kit.md)
- [`design/dependency-control-stack.md`](./dependency-control-stack.md)

What it still lacked was the ranked execution layer that says **how dependency intake and upgrade review become one credible ecosystem contribution instead of several adjacent security and metadata lanes**.

Current ecosystem signals make the timing unusually good:
- crates.io now exposes more trust and publisher posture directly;
- routine malware removals are expected to produce RustSec advisories;
- `cargo vet` has mature low-friction differential-review and import workflows;
- Cargo Scan has now published an effect-focused review argument with empirical workload numbers;
- capability analysis in Rust is moving from prototype to practical security tooling;
- binary-attached dependency inventories are no longer hypothetical.

That combination suggests a practical rollout: start with lockfile and version-bump review, then attach dangerous-code review, then attach capability review, then tie the result to artifacts and binaries, and only after that widen to PR/release/policy/assistant consumers.

## References (signals)
- crates.io development update:
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- crates.io malicious-crate policy update:
  https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- Cargo Vet docs:
  https://mozilla.github.io/cargo-vet/how-it-works.html
  https://mozilla.github.io/cargo-vet/performing-audits.html
- Cargo Scan paper:
  https://arxiv.org/html/2602.06466v1
- Rust Foundation / Alpha-Omega security update:
  https://rustfoundation.org/media/strengthening-rust-security-with-alpha-omega-a-progress-update/
- `cargo-capslock` and FOSDEM 2026 talk:
  https://github.com/ksuzuki/cargo-capslock
  https://fosdem.org/2026/schedule/event/QGCFDA-using_capslock_analysis_to_develop_seccomp_filters_for_rust_and_other_services/
- `cargo-auditable`:
  https://docs.rs/crate/cargo-auditable/latest

## Pilot order
### 1) Lockfile / version-bump review lane
**Goal:** make one dependency addition or upgrade reviewable without pretending effect/capability coverage is already complete.

Produce:
- `dependency-review-brief/v0`
- `dependency-review-subject/v0`
- imported dependency-control / trust-decision attachments
- `dependency-review-handoff/v0` for PR review

Questions this lane must answer:
- what changed?
- what trust/advisory/publisher facts apply?
- what remains unreviewed or exempted?
- what is the bounded PR conclusion?

### 2) Effect-attached review lane
**Goal:** attach dangerous-code review rather than only advisories and publisher facts.

Produce:
- imported effect-audit files or effect-review attachments
- effect summary inside `dependency-review-pack/v0`
- explicit `unknown` / `not-run` / `partial` markers where analysis coverage is incomplete

Questions this lane must answer:
- what effects were found?
- which were locally safe, unsafe, or caller-checked?
- which crates or upgrade diffs dominate human review burden?
- what review still depends on application calling context?

### 3) Capability-attached review lane
**Goal:** attach least-privilege posture without pretending capability inference is the same as effect review.

Produce:
- imported `cap-inference-report` / `cap-check-report` / candidate-enforcement attachments where available
- capability delta summary inside `dependency-review-pack/v0`
- bounded notes on inference blind spots and declaration gaps

Questions this lane must answer:
- what new powers appear implied by the dependency change?
- does declared authority differ from inferred authority?
- what enforcement candidate or sandbox delta follows?
- what remains hypothetical rather than deployed?

### 4) Artifact / binary attachment lane
**Goal:** tie reviewable dependency subjects to shipped binaries or release artifacts.

Produce:
- imported inventory or `cargo-auditable` attachments
- artifact linkage section inside `dependency-review-pack/v0`
- `dependency-review-diff/v0` across releases or binaries where possible

Questions this lane must answer:
- what built artifact corresponds to the reviewed subject?
- what was observed directly from Cargo versus recovered from a binary?
- what fidelity or lossiness caveats apply?
- what changed in the shipped dependency set?

### 5) PR / release / policy / assistant consumer lane
**Goal:** prove that thin consumers can import the stack honestly.

Produce:
- `dependency-review-handoff/v0` variants for `<pr|security|release|policy|assistant>`
- explicit lossiness / freshness / uncertainty markers
- schema verification and import checks

Questions this lane must answer:
- what may this consumer conclude?
- what may it not conclude?
- what imported facts were omitted for brevity?
- what follow-up review remains required?

## Candidate tool posture
A worthy pilot should look like a thin companion tool, for example:
- `cargo dep-review init`
- `cargo dep-review diff`
- `cargo dep-review import-trust`
- `cargo dep-review import-effects`
- `cargo dep-review import-capabilities`
- `cargo dep-review attach-binary`
- `cargo dep-review handoff --to <pr|security|release|policy|assistant>`
- `cargo dep-review verify-pack <path>`

This should stay a **thin composition layer**.
It should not replace Cargo, crates.io, RustSec, Cargo Vet, Cargo Scan, Capslock, or SBOM/inventory tooling.

## What `dependency-review-pack/v0` should contain
- `manifest.json`
- `dependency-review-brief.json`
- one or more `dependency-review-subject.json`
- imported trust-decision pointers or attachments
- imported effect-review pointers or attachments
- optional capability-analysis pointers or attachments
- optional inventory / binary-linkage pointers or attachments
- optional `dependency-review-diff.json`
- one or more `dependency-review-handoff.json` summaries
- checksums, provenance, freshness, uncertainty, and generator identity

## Design principles
- **Review the subject, not the ecosystem in general.**
- **Trust facts, effect facts, capability facts, and artifact facts must remain visibly distinct.**
- **Unknowns are first-class.** `not-run`, `partial`, and `inconclusive` states are successes if honest.
- **Local decisions stay importable and diffable.**
- **Consumers import bounded summaries.**
- **Companion-tool posture stays honest.** A plugin/pack layer is already a success.

## Early implementation order
1. lockfile / version-bump review lane
2. effect-attached review lane
3. capability-attached review lane
4. artifact / binary attachment lane
5. PR / release / policy / assistant consumer lane

That order follows the real review pressure in the ecosystem: first make one upgrade review legible, then make dangerous-code and least-privilege posture attachable, then bind it to shipped artifacts, then make downstream summaries honest.

## Non-goals
- a universal security portal;
- a mandatory approval service;
- a crate-score leaderboard;
- a replacement for `cargo vet` or Cargo Scan;
- an assistant that improvises hidden review logic.

## Success bar
This becomes worthy when a maintainer or downstream consumer can answer:
- what dependency subject changed;
- what trust/advisory facts and local decisions apply;
- what dangerous effects and caller-context obligations exist;
- what powers the code seems to need if executed;
- what artifact or binary linkage exists;
- what changed versus the prior reviewed point;
- and what this specific consumer may safely summarize,

without scraping crates.io tabs, issue comments, ad hoc audit notes, or release archaeology.

## Read this with
- `design/dependency-review-stack.md`
- `design/trust-decision-stack.md`
- `design/runtime-capability-kit.md`
- `design/sbom-evidence-kit.md`
- `design/dependency-control-stack.md`
