# Design: Safety-Critical Pilot Program (`cargo safety pilot`, `cargo cov pilot`, `cargo sanitize pilot`, `cargo verify pilot`, `safety-critical-pilot-pack/v0`)

## Goal
Make the archive treat **Safety Evidence Kit**, **Coverage Evidence Kit**, **Sanitizer Battery Kit**, and **Formal Verification Kit** as one shared **Safety-Critical Evidence Stack** without collapsing them into one mega-tool.

The missing contribution is not merely “more assurance tooling”.
It is a disciplined rollout that proves Rust projects can publish **portable safety-critical evidence** for a few concrete lanes before widening the claim.

## References (signals)
- Rust’s 2026 flagship roadmap explicitly names Safety-Critical Rust and lists MC/DC coverage support, normative `unsafe` documentation, safety-critical lints in Clippy, and FLS release cadence as key milestones.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The Rust safety-critical adoption writeup says evidence demands increase with criticality and creates a strong incentive to isolate the highest-criticality logic into the smallest surface area possible.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
- The MC/DC goal says MC/DC is required by several major functional-safety standards and that a sustainable compiler-integrated implementation is the viable path.
  https://rust-lang.github.io/rust-project-goals/2026/mcdc-coverage-support.html
- The normative-unsafe-docs goal says current unsafe documentation is insufficiently authoritative for rigorous safety cases and proposes a real-world pattern-catalog process.
  https://rust-lang.github.io/rust-project-goals/2026/safe-unsafe-for-safety-critical.html
- The Clippy goal says the expected lint volume is large enough that Rust needs a sustainable home for safety-critical lint work.
  https://rust-lang.github.io/rust-project-goals/2026/safety-critical-lints-in-clippy.html
- The FLS upkeep and release-cadence goals make specification upkeep a live operational dependency rather than a distant aspiration.
  https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html
  https://rust-lang.github.io/rust-project-goals/2026/stabilize-fls-releases.html
- The standard-library contracts goal and the experimental `core::contracts` module show that contract surfaces are becoming importable compiler-facing data.
  https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
  https://doc.rust-lang.org/core/contracts/index.html
- The rustc coverage docs already define the official instrumentation-based flow, which makes criterion-aware coverage artifacts a practical input instead of a thought experiment.
  https://doc.rust-lang.org/beta/rustc/instrument-coverage.html

## Why this needs its own design layer
The archive already had strong safety-related kits, but it still lacked the stack-level product direction needed to keep them honest together.

Without a shared pilot program, this seam is vulnerable to three bad outcomes:
1. **certification theater** — a huge claim with no lane discipline;
2. **artifact flattening** — coverage, sanitizers, proofs, and contracts all collapsed into one fake assurance number;
3. **premature qualification posture** — pretending Rust projects need a universal dossier format before the underlying evidence lanes are stable.

A worthy contribution here should prove a smaller and stronger claim:
> Rust projects can attach enough structured evidence that humans and tools can distinguish contract truth, criterion truth, runtime-checking truth, and proof truth for scoped high-assurance lanes.

## Design principles
1. **Pilot slices, not whole products.** Start with the smallest critical surface that matters.
2. **Keep evidence families distinct.** Safety-case summary, coverage result, dynamic-analysis lane, and proof result must not overwrite one another.
3. **Normative authority beats local prose, but local prose stays visible.** Missing authority should remain legible instead of being papered over.
4. **Treat partial support as normal.** `INCOMPLETE`, `PARTIAL`, `UNSUPPORTED`, and `INCONCLUSIVE` are expected outcomes in early pilots.
5. **Prefer real consumers.** A pilot graduates only if some release/review/support/policy workflow can actually consume it.
6. **Do not make MC/DC the entry price for everything.** Rust should prove simpler assurance lanes first while leaving a place for criterion-sensitive growth.

## Artifact family

### 1. `safety-pilot-brief/v0`
Why the lane is being piloted.

Should record:
- pilot id and summary
- subject family (`unsafe-library`, `dynamic-battery`, `criterion-release`, `proof-module`, `release-candidate`)
- why this lane matters now
- intended consumers
- why the lane is tractable now

### 2. `critical-slice-profile/v0`
The scoped subject under review.

Should record:
- workspace/package/module/binary identity
- features/target/profile/configuration id
- declared criticality or assurance tags
- included and excluded components
- decomposition rationale
- whether the slice is illustrative, gating, or qualification-oriented

Design rule: a pilot should make its scope boundary explicit.

### 3. `safety-import-profile/v0`
The allowed evidence mix for a pilot.

Should record:
- imported evidence families (`safety-pack`, `coverage-pack`, `sanitize-pack`, `verify-pack`, `support-pack`, `spec-pack`)
- freshness and comparability rules
- criterion requirements
- accepted authority classes
- missing-evidence behavior
- whether evidence is canonical, advisory, or watch-only

### 4. `assurance-waiver-budget/v0`
The explicit exception model for a lane.

Should record:
- what may be waived
- who may waive it
- expiry and review rules
- whether waivers downgrade status or only annotate
- which evidence families may never be waived away entirely

### 5. `safety-consumer-handoff/v0`
How a pilot result is consumed.

Should record:
- consumer class (`unsafe-review`, `release-review`, `safety-review`, `support-review`, `policy-review`)
- required human approvals
- what the consumer may conclude
- what the consumer must not conclude
- local assumptions layered on top

### 6. `safety-pilot-scorecard/v0`
Decides whether the pilot works.

Should ask:
- did the pilot preserve scope truth?
- did it keep authority classes explicit?
- did it distinguish criterion, runtime, and proof evidence honestly?
- did at least one real workflow consume it?
- did it make waivers easier to review rather than easier to hide?
- does widening the pilot still look justified?

### 7. `safety-critical-pilot-pack/v0`
Bundle for review and reuse:
- pilot brief
- critical slice profile
- safety import profile
- assurance waiver budget
- safety consumer handoff
- linked or embedded packs from the underlying kits
- current scorecard
- rendered summaries and references

## Ranked first pilots

### 1) Unsafe-heavy library review lane
**Why first**
- The normative-unsafe-docs goal is explicitly about recurring `unsafe` patterns in real codebases.
- This is the narrowest lane that still tests unsafe inventory, cited authority, lint posture, and partial/incomplete states.
- It exercises the safety-case substrate before demanding deep target or certification claims.

**Core artifacts**
- `safety-pack/v0`
- local lint posture and waiver budget
- optional `coverage-pack/v0` with ordinary line/region coverage only
- consumer handoff for library review / release review

**Primary consumers**
- maintainers of unsafe-heavy libraries
- reviewers of low-level utility crates
- teams trying to replace bespoke unsafe-review docs

### 2) Dynamic-analysis battery lane
**Why second**
- Runtime checking is valuable even before proof or certification posture matures.
- This lane proves that dynamic-analysis heterogeneity can remain honest inside a shared safety story.
- It is also where many unsafe-heavy crates can get immediate value.

**Core artifacts**
- `sanitize-pack/v0`
- linked `safety-pack/v0`
- capability and blind-spot declarations
- waiver budget for suppressed or unsupported findings

**Primary consumers**
- unsafe-heavy crate teams
- mixed Rust/C/C++ projects
- internal safety reviewers who need more than “Miri passed”

### 3) Criterion-aware release lane
**Why third**
- The MC/DC goal is explicitly active, but upstream support is still not the entry-level assumption for all users.
- This pilot should therefore support ordinary coverage criteria now while preserving an honest slot for decision/MC/DC lanes as they become sustainable.
- It proves the archive can talk about safety coverage without flattening criteria.

**Core artifacts**
- `coverage-pack/v0`
- explicit criterion requirements
- subject-specific exclusions and comparability notes
- linked `safety-pack/v0`

**Primary consumers**
- CI/release reviewers
- teams with stricter testing evidence requirements
- early safety-critical adopters who need explicit criterion semantics

### 4) Proof-augmented module lane
**Why fourth**
- By this stage the stack should be strong enough to attach proof results to a narrowly scoped critical module or property set.
- This lane should import the already-hardened outputs from [`design/formal-verification-pilot-program.md`](./formal-verification-pilot-program.md) rather than re-solving proof/report interoperability inside the safety bundle.
- This proves that proof artifacts can plug into the broader case without becoming the whole case.

**Core artifacts**
- `verify-pack/v0`
- linked `safety-pack/v0`
- explicit assumptions/trusted-code declarations
- optional dynamic-analysis and coverage attachments for the same slice

**Primary consumers**
- teams verifying a concentrated critical module
- reviewers comparing proof-backed versus test-backed claims
- release workflows that need stronger evidence for one narrow surface

### 5) Certification-facing release-candidate lane
**Why fifth**
- Only after the narrower pilots work should the stack widen toward release-candidate and qualification-friendly packaging.
- This lane composes FLS/spec references, support-envelope posture, release identity, and underlying evidence packs without pretending to automate certification itself.

**Core artifacts**
- linked `safety-pack`, `coverage-pack`, `sanitize-pack`, `verify-pack`
- optional `support-pack/v0`, release evidence, and spec references
- consumer handoff for safety-review / release-review / audit-prep workflows

**Primary consumers**
- organizations assembling higher-assurance release reviews
- downstream integrators
- audit and qualification preparation teams

## Graduation rules
A pilot should graduate only when:
1. at least one real consumer uses it;
2. scope boundaries stay explicit;
3. unsupported/partial states remain visible;
4. authority classes remain reviewable;
5. widening the claim still looks justified.

If those are not met, the right outcome is to keep the pilot narrow or split it further.

## Why this is a worthy contribution
Rust already has meaningful safety ingredients.
What it lacks is the **pilot discipline** that turns those ingredients into reusable high-assurance infrastructure.
A good safety-critical pilot program would let the ecosystem learn from real review lanes without pretending every project needs or can satisfy the strongest assurance posture on day one.


Treat [`design/safety-critical-evidence-stack.md`](./safety-critical-evidence-stack.md), this pilot program, and [`proposals/epic-safety-critical-evidence-stack.md`](../proposals/epic-safety-critical-evidence-stack.md) as one execution band.
