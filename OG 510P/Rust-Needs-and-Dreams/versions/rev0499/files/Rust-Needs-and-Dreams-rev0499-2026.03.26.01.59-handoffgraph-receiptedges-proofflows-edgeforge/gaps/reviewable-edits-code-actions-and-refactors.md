# Gap: reviewable edits, code actions, and refactors

Rust has several ways to *suggest* or *apply* source edits, but it still lacks one portable, reviewable boundary for deciding **which edits should be applied, in what order, under what assumptions, and with what verification**.

Today the ecosystem already has real edit-producing lanes:
- `rustc` emits structured diagnostics with suggested replacements and applicability metadata.
- `cargo fix` applies compiler suggestions.
- edition migration workflows use `cargo fix --edition` and lint groups.
- rust-analyzer provides assists / code actions, diagnostics with fixes, rename, and structural search-and-replace (SSR).
- specialized tools and future assistants increasingly want to propose or batch related edits.

But these lanes remain fragmented. The result is that Rust still lacks a shared answer to questions like:
- what exact workspace/package/target/profile/features/toolchain subject were these edits derived against?
- which producer proposed each edit?
- is this edit a compiler suggestion, a lint fix, an edition migration, an assist, a rename, or an SSR/refactor?
- what conflicts or ordering constraints exist between candidates?
- which edits were selected versus merely available?
- what verification was run after application?
- what was skipped, partially applied, manually adjusted, or waived?

That missing seam matters because the cost of Rust maintenance is often not “can a tool suggest something?” but “can a team safely *review and replay* a nontrivial batch of edits?”

## Why this is now a real ecosystem gap
- The Cargo Book says `cargo fix` automatically takes `rustc` suggestions and applies them, and exposes modes like `--edition`, `--edition-idioms`, and `--broken-code`. That proves the core edit loop is valuable and already part of mainstream Rust workflows.
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- The Edition Guide says `cargo fix --edition` applies a lint group and may run `cargo check` multiple times until no new warnings appear. It also says some migrations need partial/manual handling or even custom tools built on `rustfix`. That is direct evidence that edit suggestion, edit selection, edit application, and migration orchestration are not the same problem.
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- The Rust 1.85 / Rust 2024 announcement says `cargo fix` can automate many necessary changes for edition migration, but the project still points users to the edition guide and follow-up checking/testing. That is evidence that automated edits are useful but not self-validating.
  https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- Cargo’s 1.90 development-cycle report says the current `cargo fix` architecture is slow, only applies a subset of possible lints, and does not make selecting which lints to fix easy, because it works as a special `rustc`-proxy mode holding a cross-process lock. That is unusually strong evidence that the ecosystem does not merely need “more fixes”; it needs a better edit substrate.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- The 2025 GSoC results say the `cargo-fixit` prototype used a different architecture where the top-level program controls what fixes get applied, removes the lock bottleneck, and opens the door to interactive selection. That is exactly the kind of architecture signal that should be captured in an archive contribution.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo’s 1.93 development-cycle report says unifying Cargo structured-report schemas with Cargo JSON output could unblock a new, faster, more flexible `cargo fix` architecture. That is direct evidence that machine-facing edit data is becoming a first-class Cargo concern.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The StableMIR publication goal says Rust wants public, semver-governed compiler-facing crates for analyzers, linters, and development environments rather than direct dependence on compiler internals. That matters here because a durable edit boundary should sit beside durable compiler-facing facts instead of depending on private driver hacks forever.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- rust-analyzer’s site and book document a broad code-action/assist ecosystem, configuration for assist quality, and command-level surfaces like `rust-analyzer.ssr`; the docs also show editor differences in how code actions are exposed. That is evidence that Rust’s edit world is already larger than compiler suggestions, but still unevenly represented.
  https://rust-analyzer.github.io/
  https://rust-analyzer.github.io/book/configuration
  https://rust-analyzer.github.io/book/other_editors.html
- rust-analyzer’s changelogs show a long-lived stream of concrete edit capabilities: SSR command support, “apply SSR” assist, extract/inline/rename/file-structure assists, diagnostic fixes, and ongoing assist API work. That is strong evidence that the missing contribution is not another single refactor tool but a reviewable interchange over heterogeneous edit producers.
  https://rust-analyzer.github.io/thisweek/2020/07/06/changelog-32.html
  https://rust-analyzer.github.io/thisweek/2021/03/15/changelog-68.html
  https://rust-analyzer.github.io/thisweek/2024/12/16/changelog-264.html

## What is still missing
Rust still lacks one portable artifact family that can represent:

### 1. Edit subject identity
A batch of edits is only meaningful relative to:
- a workspace/package selection,
- target/profile/features/cfgs,
- toolchain and edition,
- file snapshots or revision ids,
- and optionally the editor/runtime environment that produced assist-style edits.

### 2. Candidate edit provenance
A compiler suggestion, Clippy fix, edition-compatibility lint, rust-analyzer assist, SSR transform, rename, and future assistant proposal are not interchangeable.
They differ in:
- authority,
- applicability/confidence,
- selection semantics,
- expected review burden,
- and verification needs.

### 3. Conflict and ordering truth
Real edit batches can conflict or depend on ordering:
- one fix unlocks another,
- one rename invalidates later spans,
- one assist overlaps a compiler suggestion,
- one migration step depends on a manifest/config change.

The ecosystem needs a way to represent conflict classes and ordering plans without pretending all edits can be applied as one giant patch.

### 4. Selection versus application
Available edits and approved edits are different.
A good system should preserve:
- candidates discovered,
- candidates rejected,
- candidates deferred,
- candidates selected with rationale,
- and what actually applied cleanly.

### 5. Verification truth
After edits are applied, what was checked?
- `cargo check`
- `cargo test`
- target/feature matrix coverage
- formatting / lint reruns
- semantic or edition verification
- downstream/API checks

Without this, edit workflows remain half-automation and half-forgotten human trust.

## Why this would be a worthy contribution
A good edit-workflow substrate would help Rust in at least five high-leverage places:
1. **Edition migrations** become reviewable, replayable, and less folklore-driven.
2. **Lint cleanup** becomes selective and attachable instead of “run `cargo fix` and hope”.
3. **IDE/editor refactors** gain a durable export/review boundary instead of living only in one editor session.
4. **CI/review bots and assistant tools** can propose bounded edit packs without pretending they directly own the working tree.
5. **Cargo/rust-analyzer evolution** gets a shared interchange boundary instead of each new architecture inventing its own transient edit story.

## What “good” looks like
A worthy v0 contribution would define a portable family like:
- `edit-subject/v0`
- `edit-candidate-report/v0`
- `edit-selection-plan/v0`
- `edit-apply-report/v0`
- `edit-verify-report/v0`
- `edit-diff-report/v0`
- `edit-pack/v0`

Such a kit would let a team answer:
- what edits were proposed?
- by whom/what?
- under what subject and evidence?
- which were selected?
- what conflicts and orderings existed?
- what actually changed on disk?
- what verification succeeded, failed, or was skipped?

That would make Rust edit workflows much more composable and trustworthy than today’s split between ephemeral IDE actions, `cargo fix`, console logs, and ad hoc shell scripts.

See:
- `design/edit-workflow-kit.md`
- `proposals/epic-edit-workflow-kit.md`


## What should happen next
The next credible move is not a universal refactor engine. It is a **ranked pilot program**:

1. compiler-suggestion export and explicit selection;
2. `cargo fix` / edition migration waves with broken-code and verification truth;
3. rust-analyzer assist / SSR export lanes;
4. assistant proposals only as weaker-authority candidate packs;
5. CI/review-bot consumption only after the earlier lanes are working.

That pilot posture matters because current Rust signals are converging on a better machine-facing fix architecture, while the survey says canonical docs remain central even as LLM/editor workflows rise. The archive should therefore prefer **canonical-first edit governance** over “smart editor magic” or direct assistant patch application.

See also:
- `design/edit-workflow-kit.md`
- `design/edit-governance-pilot-program.md`
- `proposals/epic-edit-workflow-kit.md`
