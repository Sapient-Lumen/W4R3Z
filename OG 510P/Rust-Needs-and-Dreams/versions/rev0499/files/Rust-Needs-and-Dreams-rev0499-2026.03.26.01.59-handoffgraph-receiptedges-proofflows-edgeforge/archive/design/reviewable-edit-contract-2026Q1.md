
## Execution addendum (rev0447)
This seam now has a direct execution answer in `design/reviewable-edit-execution-blueprint-2026Q1.md`.
Read that note first when the question is no longer only “should Rust have a reviewable edit boundary?” but “what should the worthy contribution actually ship, what proving lanes come first, and what wrong shapes should be refused?”

# Design: Reviewable Edit Contract 2026Q1

## Goal
Promote the archive's existing **Edit Workflow Kit** into an explicit frontier for **reviewable Rust code mutation**.

The missing contribution is not another one-off refactor command, another IDE-only assist family, or a license for agents to rewrite the working tree.
It is one honest boundary that keeps these layers separate:
- **subject/context truth** — what package/workspace/targets/features/toolchain/file state the edits were derived against;
- **candidate provenance truth** — whether a proposal came from `rustc`, Clippy, `cargo fix`, edition migration lints, rust-analyzer assists, SSR/refactor tools, or an assistant/bot;
- **selection/ordering truth** — which candidate edits were chosen, deferred, or rejected, and in what order they should apply;
- **application truth** — what actually changed on disk and what conflicted, drifted, or was partially applied;
- **verification truth** — what checks were rerun and what remained unverified; and
- **consumer handoff truth** — what CI, code review, editors, release workflows, or assistants may conclude from the result.

That is the frontier the archive had already been circling in `design/edit-workflow-kit.md`.
This note promotes it into an explicit repo-shaping answer.

## Why this is the right frontier now
Current official Rust signals line up unusually well around this seam.

- The Cargo Book makes `cargo fix` a mainstream workflow and says it automatically applies `rustc` suggestions, but only for the code that `cargo check` actually sees; features and target-specific code require additional runs.
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- The Edition Guide says `cargo fix --edition` may need multiple passes, can require `--broken-code`, cannot fully fix macros, generated code, or doctests, and sometimes needs editor quick-fixes or a custom `rustfix`-based tool.
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Cargo's 1.90 development-cycle report says the current `cargo fix` architecture is slow, only applies a subset of lints, and is hard to make selective or interactive because it uses a `rustc`-proxy loop with a cross-process lock.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- The GSoC 2025 `cargo-fixit` prototype shows a different design is feasible: put the top-level program in control of which fixes apply, remove the lock bottleneck, and open the door to interactive selection.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo's 1.93 development-cycle report says schema unification between structured reports and Cargo JSON output could unblock a faster, more flexible future `cargo fix` architecture.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The StableMIR publication goal says Rust wants semver-governed public compiler-facing crates so analyzers, linters, and development environments can stop depending directly on compiler internals. That is exactly the kind of upstream posture a durable edit boundary wants to sit beside.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- The 2025 State of Rust survey says online docs remain the canonical reference while editors with agentic support are rising. That is a strong reason to prefer a governed edit boundary over direct assistant mutation.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Why this is strategically worthy
This contribution would unlock several recurring pain points at once.

### 1. Edition migration becomes reviewable instead of folkloric
Rust already has automated migration tooling, but the Edition Guide is explicit that migrations can be partial, configuration-specific, and sometimes manual. A reviewable edit contract would let a team attach an ordered migration plan and verification receipt instead of reconstructing what happened from shell history.

### 2. Lint cleanup becomes selective instead of opaque
`cargo fix` is useful precisely because `rustc` already knows how to suggest many fixes. But the current architecture still blurs candidate discovery, selection, and application. A reviewable contract would let maintainers say “apply only the machine-applicable candidates from these lints for this target/feature slice” without pretending every suggested change is equally trustworthy.

### 3. IDE refactors can leave the editor honestly
Rust IDE workflows increasingly include rename, quick-fix, and structural refactor actions, but those edits often stop being legible once they leave the editor session. A portable edit pack would let editor-native actions participate in normal review and CI workflows without pretending the editor itself is the system of record.

### 4. Agent/bot proposals can be downgraded into bounded candidates
The survey signal does not justify letting assistants mutate code directly. It does justify making their proposals attachable as weaker-authority edit candidates. That is strategically valuable both for the Rust ecosystem and for this archive's own meta-hygiene.

### 5. Cargo and public compiler-tooling work get a shared downstream handoff
A semver-governed compiler-facing API (`rustc_public` / StableMIR direction), faster fix architecture (`cargo-fixit` direction), and richer Cargo structured outputs all become more valuable if they can hand results into one reviewable edit layer instead of each inventing its own patch story.

## What the contribution should look like in theory
The theory should stay deliberately thin.
A good v0 is not “a universal Rust refactoring platform.”
It is a contract family with explicit confidence and verification boundaries.

### Proposed artifact spine
- `edit-subject/v0`
- `edit-candidate-report/v0`
- `edit-selection-plan/v0`
- `edit-apply-report/v0`
- `edit-verify-report/v0`
- `edit-diff-report/v0`
- `edit-pack/v0`

### Layering rule
The contribution should compose **next to** these existing archive seams, not subsume them:
- **Semantic Context Kit** provides canonical machine-usable subject/context and imported compiler/docs facts.
- **Compiler Extensibility Stack** provides attachment lanes and result-family discipline for compiler-adjacent tools.
- **Lint Governance Stack** owns lint policy, findings, and debt.
- **Migration Kit** owns destination-aware change plans.
- **Reviewable Edit Contract** owns the execution/review boundary for actual code mutation.

## What the contribution should look like in practice
A serious implementation would likely look like a thin companion tool and adapter family, not a monolith:
- `cargo editflow collect` — capture candidates from compiler/Cargo producer lanes;
- `cargo editflow plan` — select, order, and explain chosen candidates;
- `cargo editflow apply` — apply a bounded plan and emit receipts;
- `cargo editflow verify` — rerun scoped checks and attach explicit incompleteness;
- `cargo editflow pack` — produce a redacted review artifact for CI / PR / issue attachment.

Adapters should be ranked, not all built at once:
1. compiler suggestions / `cargo fix` lane;
2. edition migration lane;
3. rust-analyzer assist / rename / SSR export lane where possible;
4. assistant proposal lane only as weaker-authority candidate packs;
5. CI / review-bot import lane after the earlier ones work.

## Non-goals
- another one-true refactoring DSL;
- direct assistant ownership of the working tree;
- declaring successful application equivalent to correctness;
- flattening compiler suggestions, editor assists, and assistant proposals into one confidence class;
- replacing Cargo, rust-analyzer, `rustfix`, or future public compiler APIs.

## Ranking and repo consequence
This promotion does **not** rewrite the archive's broad ladder.
It does **not** outrank Build-State Evidence, Adoption Navigation, or Debuggability.
It does **not** replace the current Cargo-facing frontier work on workspace environment, build interop, or artifact handoff.

What it does do is make one under-promoted seam explicit:
**the clearest next mutation/review/handoff-shaping move is now Reviewable Edit Contract, read through the existing Edit Workflow Kit.**

That gives the archive a better answer to a question that is only getting more central:
How should Rust let humans, CI, editors, and agents propose and review changes **without** smearing compiler truth, tool authority, and verification into one opaque patch event?
