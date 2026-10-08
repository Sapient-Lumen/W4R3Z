## Current stack note (rev0404)
Read this stack now as a **Safety-Critical Assurance Contract substrate**.

The archive's current claim is no longer only that safety evidence, coverage evidence, sanitizer lanes, and proof lanes belong together.
It is that they now need a named **composition boundary** above them:
- **critical-slice subject truth**,
- **authority truth**,
- **requirement-profile truth**,
- **evidence-lane import truth**,
- **waiver / residue truth**,
- and **consumer-handoff truth**.

Use `design/safety-critical-assurance-contract-2026Q1.md` when deciding whether to deepen this frontier next.
Do **not** let any one leaf — coverage, Clippy, contracts, FLS, sanitizers, or proofs — impersonate the whole assurance story.

# Design: Safety-Critical Evidence Stack (Safety Evidence + Coverage Evidence + Sanitizer Battery + Formal Verification)

## Goal
Treat **Safety Evidence Kit**, **Coverage Evidence Kit**, **Sanitizer Battery Kit**, and **Formal Verification Kit** as one shared **Safety-Critical Evidence Stack**.

The missing contribution is not another certification checklist, another one-tool verifier pitch, or another coverage badge with scarier marketing.
It is a portable, reviewable stack that keeps four truths distinct while letting them compose:
- **safety-case assembly and contract-citation truth**,
- **coverage-criterion truth**,
- **dynamic-analysis lane truth**,
- **formal-proof and assumption truth**.

That separation matters because high-assurance Rust work is not one activity:
- sometimes the hard part is **authoritative safety contracts**,
- sometimes it is **criterion-specific test evidence**,
- sometimes it is **runtime-checking coverage on the actual target lane**,
- sometimes it is **proof scope and trusted-code boundaries**,
- and often it is all of them together.

## Why this seam matters now
Current official Rust signals are unusually aligned here:
- Rust’s 2026 flagship roadmap explicitly names **Safety-Critical Rust** and lists MC/DC coverage support, normative `unsafe` documentation, safety-critical lints in Clippy, and a stable FLS release cadence as key milestones.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The Rust safety-critical adoption writeup says the central pressure in these domains is process, verification, and evidence, and that teams are strongly incentivized to isolate the highest-criticality logic into the smallest surface area possible.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The proposed MC/DC goal says MC/DC is required by standards such as DO-178C, ISO 26262, and IEC 61508, and that implementing it outside the compiler is infeasible because macro expansion makes valid post-expansion Rust sources unrealistic.
  https://rust-lang.github.io/rust-project-goals/2026/mcdc-coverage-support.html
- The proposed normative-unsafe-docs goal says the current unsafe-documentation story is insufficient for rigorous safety cases and proposes a pattern-catalog approach over real codebases.
  https://rust-lang.github.io/rust-project-goals/2026/safe-unsafe-for-safety-critical.html
- The proposed Clippy goal says safety-critical development will likely need 50 to 200 lints over one to two years, many of them useful outside safety-critical work too.
  https://rust-lang.github.io/rust-project-goals/2026/safety-critical-lints-in-clippy.html
- The FLS upkeep and release-cadence goals make the spec side much more operational than before: the FLS is explicitly treated as an enabler for safety qualification, and the plan is a predictable six-week release cadence relative to stable Rust.
  https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
  https://rust-lang.github.io/rust-project-goals/2026/stabilize-fls-releases.html
- The standard-library contracts goal and the `core::contracts` experimental module show that executable pre/postcondition surfaces are no longer purely aspirational.
  https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
  https://doc.rust-lang.org/core/contracts/index.html
- The official rustc coverage docs make criterion and tooling details explicit enough that a portable evidence layer is increasingly realistic.
  https://doc.rust-lang.org/beta/rustc/instrument-coverage.html

Taken together, ideal Rust now needs a more executable safety-critical story than “good language + some tools”.

## What each kit owns
### Safety Evidence Kit
[`design/safety-evidence-kit.md`](./safety-evidence-kit.md) owns:
- unsafe-surface inventory,
- cited safety contracts,
- lint posture,
- waivers,
- derived safety-case summaries.

Its question is:
> what obligations exist, what authority justifies them, and what broad case status can we derive?

### Coverage Evidence Kit
[`design/coverage-evidence-kit.md`](./coverage-evidence-kit.md) owns:
- declared coverage intent,
- engine/model provenance,
- coverage criteria,
- merge and gate semantics,
- comparable versus non-comparable runs.

Its question is:
> what does coverage mean here, which criterion actually ran, and how should the result be interpreted?

### Sanitizer Battery Kit
[`design/sanitizer-battery-kit.md`](./sanitizer-battery-kit.md) owns:
- dynamic-analysis lane identity,
- runtime/sysroot/instrumentation provenance,
- capability and blind-spot declarations,
- findings and waivers,
- diffable runtime-checking outputs.

Its question is:
> which runtime-checking lane ran, what could it truly observe, and what did it actually find?

### Formal Verification Kit
[`design/formal-verification-kit.md`](./formal-verification-kit.md) owns:
- proof intent,
- backend capability declarations,
- assumptions and trusted code,
- proof/counterexample outputs,
- diffable verification changes.

Its question is:
> what property was being proved, with which backend and assumptions, and what was the result?

## Shared stack thesis
A worthy contribution here should let a reviewer answer all of these without reading bespoke binders, CI YAML, and one-off spreadsheets:
1. Which safety-critical subject or slice is under review?
2. Which unsafe contracts are authoritative, local, or still unresolved?
3. Which lint/coding-standard posture applies?
4. Which coverage criterion actually counts for this lane?
5. Which runtime-checking lanes ran, with what visibility and limitations?
6. Which properties were formally proved, falsified, bounded, or unsupported?
7. Which conclusions are real evidence conclusions versus local policy conclusions?

If the stack cannot answer those seven questions, it is not yet ecosystem infrastructure.

## Recommended execution posture
The stack now needs a shared execution layer and an explicit stack-level proposal candidate, captured in:
- [`design/safety-critical-pilot-program.md`](./safety-critical-pilot-program.md)
- [`design/sanitizer-battery-pilot-program.md`](./sanitizer-battery-pilot-program.md)
- [`proposals/epic-safety-critical-evidence-stack.md`](../proposals/epic-safety-critical-evidence-stack.md)

That pilot program should prove the stack in the following order:
1. **unsafe-heavy library review lane**
2. **dynamic-analysis battery lane** (after the narrower rollout in [`design/sanitizer-battery-pilot-program.md`](./sanitizer-battery-pilot-program.md) proves lane and execution-import honesty)
3. **criterion-aware release lane**
4. **proof-augmented module lane**
5. **certification-facing release-candidate lane**

That ordering is intentional.
The archive should not jump straight to “Rust certification in a box”.
It should first prove that attachable safety evidence can stay honest in narrower, reviewable lanes.

## Design principles
1. **Normative sources and local rationale stay separate.** The stack should reward better authority without pretending all rationale is normative.
2. **Coverage criteria are not interchangeable.** Branch, decision, and MC/DC must remain explicit.
3. **Runtime checking and proof are complementary, not competing.** One does not erase the assumptions or value of the other.
4. **Unsupported and incomplete outcomes are first-class.** Especially in safety work, false certainty is worse than partial evidence.
5. **Subject slices matter.** The safety-critical blog’s decomposition lesson should carry through into artifacts, pilots, and release review.
6. **Certification wrappers come after shared evidence.** The stack should remain useful even when no formal qualification dossier is being assembled.

## What an epic contribution would look like in practice
A serious contribution here now looks like a thin `cargo safety-critical` / `safety-critical-pack/v0` layer above the underlying kits and their existing artifact families.

Concretely, it should:
- give projects one attachable evidence family instead of bespoke binders;
- preserve criterion-aware coverage and runtime/proof heterogeneity instead of flattening them;
- make FLS/Reference/std-contract citations reviewable and diffable;
- compose with Clippy, rustc coverage, sanitizer lanes, and proof tools rather than replacing them;
- and leave behind artifacts that policy, release, support, and auditing workflows can actually consume.

## Anti-goals
Do not turn this stack into:
- one fake “safety score”,
- one universal certification template,
- one winner-take-all proof backend,
- or one giant dashboard that hides evidence provenance.

The stack is a **review boundary**, not a substitute for engineering judgment or domain certification process.


See also [`proposals/epic-safety-critical-evidence-stack.md`](../proposals/epic-safety-critical-evidence-stack.md) for the proposal-layer framing of this seam as a concrete ecosystem contribution rather than only a stack note.
