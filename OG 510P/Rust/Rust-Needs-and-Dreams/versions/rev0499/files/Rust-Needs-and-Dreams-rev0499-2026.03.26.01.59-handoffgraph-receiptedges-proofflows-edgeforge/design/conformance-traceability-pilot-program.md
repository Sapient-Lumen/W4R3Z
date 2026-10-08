# Design: Conformance Traceability Stack pilot program (`traceability-pack/v0`)

## Why this needs a stack-level pilot program
The archive already has:
- a language-facing rollout in [`design/spec-conformance-pilot-program.md`](./spec-conformance-pilot-program.md),
- compiler-lane reality in [`design/acceptance-surface-kit.md`](./acceptance-surface-kit.md), and
- assurance composition in [`design/safety-critical-pilot-program.md`](./safety-critical-pilot-program.md).

What it still lacked was the **stack-level coordination layer** that proves those three lanes can meet cleanly without turning:
- `cargo conform` into a stealth certification tool,
- acceptance-diff reporting into a second spec owner,
- or safety evidence into a place where language semantics get re-authored from scratch.

Current Rust signals make that coordination more urgent than it used to be:
- RFC 3355 says a Rust specification should serve unsafe-code authors, safety-critical users, language designers, and tooling maintainers, while also being incorporated into language evolution over time.
  https://rust-lang.github.io/rfcs/3355-rust-spec.html
- The Rust Project accepted a 2025H1 goal to bring the FLS into rust-lang infrastructure, then followed it with a 2025H2 goal to build the capabilities to keep the FLS updated sustainably.
  https://rust-lang.github.io/rust-project-goals/2025h1/spec-fls-publish.html
  https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
- Rust’s 2026 flagship goals make **Safety-Critical Rust** concrete through MC/DC coverage support, normative `unsafe` documentation, safety-critical Clippy work, and a stabilized FLS release cadence.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  https://rust-lang.github.io/rust-project-goals/2026/mcdc-coverage-support.html
  https://rust-lang.github.io/rust-project-goals/2026/safe-unsafe-for-safety-critical.html
  https://rust-lang.github.io/rust-project-goals/2026/safety-critical-lints-in-clippy.html
  https://rust-lang.github.io/rust-project-goals/2026/stabilize-fls-releases.html
- The experimental language-specification goal explicitly proposes a nightly/experimental reference with instability markers, process integration, and domain-team review, which makes text authority and traceability boundaries more important, not less.
  https://rust-lang.github.io/rust-project-goals/2026/experimental-language-specification.html
- a-mir-formality explicitly describes itself as a bridge between high-level formalization and the compiler and says it should integrate with complementary models like MiniRust and the Rust specification.
  https://rust-lang.github.io/rust-project-goals/2025h2/a-mir-formality.html
- Cargo’s test docs and rustc’s coverage docs both show that execution reality already mixes libtest, doctests, and criterion-aware coverage lanes with caveats and non-trivial assumptions.
  https://doc.rust-lang.org/cargo/commands/cargo-test.html
  https://doc.rust-lang.org/beta/rustc/instrument-coverage.html

That combination argues for a thin, ranked stack pilot rather than another harness clone, a giant qualification binder, or one more language-spec mirror.

## Stack boundary
This pilot treats the following archive pieces as one execution band:
- [`design/conformance-traceability-stack.md`](./conformance-traceability-stack.md)
- [`design/spec-conformance-kit.md`](./spec-conformance-kit.md)
- [`design/spec-conformance-pilot-program.md`](./spec-conformance-pilot-program.md)
- [`design/acceptance-surface-kit.md`](./acceptance-surface-kit.md)
- [`design/safety-critical-evidence-stack.md`](./safety-critical-evidence-stack.md)
- [`design/safety-critical-pilot-program.md`](./safety-critical-pilot-program.md)

Design rule: **the pilot is about text-to-vector-to-result-to-assurance continuity first**.
Qualification wrappers, rendered dashboards, and status badges are downstream concerns and should arrive late.

## Ranked pilots

### Pilot 1 — Stable-text core-profile lane
**Who this is for:** Rust toolchain, library, and platform teams that need narrow conformance claims tied to released Rust text.

**Why first:**
- It starts from the most defensible authority surface.
- It proves that paragraph-linked evidence can exist without snapshotting giant books or pretending total coverage.

**Required artifacts**
- `spec-pack/v0`
- `conformance-vectors/v0`
- `implementation-capabilities/v0`
- `conformance-report/v0`
- `traceability-brief/v0`

**Acceptance bar**
- A reviewer can answer “which stable/FLS paragraphs were in scope, which vectors exercised them, what capability profile ran, and what remained out of scope?” without trawling test harness logs.

### Pilot 2 — Experimental-text / instability-marker lane
**Who this is for:** domain teams participating in the experimental language-specification process.

**Why second:**
- The experimental-spec process is now a live upstream experiment, not just an archive thought experiment.
- It forces the stack to separate proposed text from stable text before the archive drifts into fake authority.

**Required additions**
- text-authority classes (`stable`, `experimental`, `draft-local`)
- provenance for review/team ownership
- capability profiles that make nightly or branch requirements explicit
- `traceability-diff/v0` for text-authority transitions

**Acceptance bar**
- A team can attach vectors and results to experimental text while still making it obvious that the text is provisional and that downstream consumers must not treat it as stable conformance law.

### Pilot 3 — Acceptance-diff lane
**Who this is for:** compiler, language, and advanced-library teams dealing with solver, borrow-check, or lane-sensitive implementation reality.

**Why third:**
- This is where spec expectations meet stable/beta/nightly reality.
- It prevents acceptance quirks and workarounds from being silently mislabeled as specification truth.

**Required additions**
- lane-aware acceptance profiles
- workaround and partial-support declarations
- side-by-side conformance vs acceptance comparison
- archaeology-friendly diff reports across toolchain revisions

**Acceptance bar**
- A reviewer can distinguish “spec says X”, “stable accepts Y”, “nightly accepts Z”, and “this workaround was required” without flattening those into one verdict.

### Pilot 4 — Safety-evidence import lane
**Who this is for:** safety-heavy libraries, runtime/profile owners, and assurance consumers who need language-semantics attachments.

**Why fourth:**
- Rust’s 2026 goals now make safety evidence concrete, not aspirational.
- This proves the stack can feed coverage, `unsafe` docs, dynamic analysis, and proof lanes without making those tools redefine Rust semantics independently.

**Required additions**
- imports into safety evidence packs
- criterion-aware coverage references
- authority tracking for normative vs local rationale
- explicit `INCONCLUSIVE` / partial-support posture for under-modeled areas

**Acceptance bar**
- Safety-oriented consumers can cite one conformance subject and its acceptance notes, then add their own coverage/runtime/proof evidence without duplicating or mutating the language-semantic story.

### Pilot 5 — Release / qualification / archaeology lane
**Who this is for:** long-lived release, audit, certification, and support workflows.

**Why fifth:**
- This is strategically valuable, but only after the lower layers can stay honest.
- It tests whether the archive’s “tight and durable evidence” posture survives handoff to long-lived consumers.

**Required additions**
- `traceability-pack/v0`
- release/qualification attachment profiles
- durable subject/version identities spanning text, vectors, and outcomes
- bounded summary views that preserve authority, scope, and incompleteness

**Acceptance bar**
- A team can attach a narrow traceability bundle to a release or audit months later and still reconstruct what was actually claimed, what text and toolchain version were in scope, and what remained provisional.

## Shared pilot rules
- **Normative text, executable vectors, acceptance reality, and assurance conclusions stay separate.**
- **Experimental text never silently inherits stable authority.**
- **Profiles beat universal claims.**
- **Capability declarations are first-class.**
- **Inconclusive and out-of-scope remain explicit.**
- **Release/qualification packaging comes last.**

## Immediate archive decision
Treat [`design/conformance-traceability-stack.md`](./conformance-traceability-stack.md), [`design/conformance-traceability-pilot-program.md`](./conformance-traceability-pilot-program.md), and [`proposals/epic-conformance-traceability-stack.md`](../proposals/epic-conformance-traceability-stack.md) as one execution band.
Use [`design/spec-conformance-pilot-program.md`](./spec-conformance-pilot-program.md) for the leaf-level conformance rollout and [`design/safety-critical-pilot-program.md`](./safety-critical-pilot-program.md) for the assurance rollout beneath it.
