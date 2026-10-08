# Epic Proposal: Safety Evidence Kit (`cargo safety`, `safety-pack/v0`)

## One-sentence pitch
Give Rust a portable safety-case substrate so unsafe code, cited contracts, lint posture, coverage criteria, verification claims, and waivers can travel as one reviewable artifact instead of living in bespoke binders and CI folklore.

## Deliverables
- `cargo safety` reference implementation
- Schemas:
  - `safety-subject/v0`
  - `unsafe-surface-report/v0`
  - `safety-contract-report/v0`
  - `safety-lint-report/v0`
  - `coverage-criterion-report/v0`
  - `verification-claim-report/v0`
  - `safety-case-report/v0`
  - `safety-pack/v0`
- Adapters / integrations for:
  - unsafe inventory inputs (`cargo-geiger` today, richer compiler inputs later)
  - contracts / cited safety docs
  - rustc + Clippy lint posture
  - coverage engines and criteria
  - sanitizer / Miri / proof-tool claims
  - optional trust/dependency-review attachments where relevant
- Example profiles:
  - `unsafe-library-review`
  - `ffi-heavy-review`
  - `safety-critical-release-candidate`

## Why now
- Rust’s 2026 flagship roadmap explicitly names Safety-Critical Rust and calls out MC/DC, normative unsafe documentation, safety-critical lints in Clippy, and a stable FLS cadence as key milestones.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The proposed 2026 unsafe-documentation goal says safety-critical users need authoritative unsafe documentation to build rigorous safety cases, and proposes a concrete pattern-catalog workflow over real codebases.
  https://rust-lang.github.io/rust-project-goals/2026/safe-unsafe-for-safety-critical.html
- The proposed 2026 MC/DC goal says real Rust needs compiler-integrated support for MC/DC because macro-expanded sources make external instrumentation infeasible, and that line/branch-style coverage is not enough for the intended standards.
  https://rust-lang.github.io/rust-project-goals/2026/mcdc-coverage-support.html
- Contracts are no longer purely theoretical: Rust already has an accepted standard-library contracts goal and a nightly `core::contracts` module with experimental `#[requires]` and `#[ensures]` attributes.
  https://rust-lang.github.io/rust-project-goals/2025h1/std-contracts.html
  https://doc.rust-lang.org/core/contracts/index.html
- The FLS is now part of rust-lang infrastructure and has an explicit upkeep goal, which means Rust now has a realistic normative/spec substrate that safety cases can cite rather than copy.
  https://rust-lang.github.io/rust-project-goals/2025h1/spec-fls-publish.html
  https://rust-lang.github.io/rust-project-goals/2025h2/FLS-up-to-date-capabilities.html

## Strategic value
This is a worthy contribution because it converts a messy process problem into reusable infrastructure.

It unlocks:
- better unsafe review for core libraries,
- attachable safety cases for embedded / robotics / industrial / transport / medical-adjacent projects,
- explicit differentiation between authoritative documentation and local rationale,
- criterion-aware coverage reporting instead of percentage theater,
- explainable release gates based on real evidence families,
- and a clean place for future upstream safety work to land.

The archive already has strong component kits for Coverage, Formal Verification, Sanitizers, Spec Conformance, and several unsafe-heavy surface kits.
Safety Evidence Kit is the missing **assembly layer** that turns them into a reviewable case.

## Non-goals
- Claiming a crate is universally “safe”
- Replacing proof tools, sanitizers, or coverage engines
- Hard-coding one certification regime into v0
- Flattening heterogeneous evidence into one confidence score
- Pretending every unsafe pattern already has authoritative documentation

## Shared stack posture
Treat this epic as the assembly layer for the shared **Safety-Critical Evidence Stack**:
- [`design/safety-critical-evidence-stack.md`](../design/safety-critical-evidence-stack.md)
- [`design/safety-critical-pilot-program.md`](../design/safety-critical-pilot-program.md)

That means `cargo safety` should correlate and summarize imported evidence from coverage, dynamic-analysis, and proof lanes instead of trying to absorb them into one fake “certified Rust” engine.
The ranked rollout should follow the pilot program: unsafe-heavy library review first, dynamic-analysis battery second, criterion-aware release third, proof-augmented module fourth, certification-facing release candidate fifth.

## Milestones
1. **v0 unsafe inventory + contracts**
   - define `safety-subject/v0`, `unsafe-surface-report/v0`, `safety-contract-report/v0`
   - support authoritative-vs-local citation tracking
2. **v0.2 lint + case status**
   - define `safety-lint-report/v0` and `safety-case-report/v0`
   - add explicit waivers and `PASS/WARN/FAIL/INCOMPLETE`
3. **v0.3 coverage + verification attachments**
   - define `coverage-criterion-report/v0` and `verification-claim-report/v0`
   - integrate with existing coverage and proof/sanitizer tooling
4. **v1 real-world pilots**
   - unsafe-heavy library pilot
   - safety-critical/embedded pilot
   - one profile with partial evidence to prove incompleteness stays honest

## Success criteria
- reviewers can locate unsafe obligations and the contracts that justify them,
- the artifact distinguishes normative citations from local rationale,
- coverage claims always name the actual criterion,
- proof/sanitizer/model-checking claims preserve engine identity and assumptions,
- waivers and unresolved gaps remain explicit,
- and the ecosystem gains a reusable safety-case boundary instead of more bespoke spreadsheets.
