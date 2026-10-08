
## Execution addendum (rev0447)
This epic is now anchored by `design/reviewable-edit-execution-blueprint-2026Q1.md`.
Interpret the proposal as a downstream implementation path for that blueprint rather than as permission to widen into a universal refactor platform, editor monopoly, or assistant-autonomy story.

# Epic Proposal: Edit Workflow Kit (`cargo editflow`)

## One-sentence pitch
Create one portable, reviewable edit-workflow boundary for Rust: capture heterogeneous edit candidates, plan which to apply, record what actually changed, and attach verification evidence so compiler fixes, assists, refactors, and migration edits stop living in ephemeral tool-specific loops. Read this now as the archive's practical **reviewable edit contract** proposal.

## Deliverables
- `cargo-editflow` reference implementation
- Schemas:
  - `edit-subject/v0`
  - `edit-candidate-report/v0`
  - `edit-selection-plan/v0`
  - `edit-apply-report/v0`
  - `edit-verify-report/v0`
  - `edit-diff-report/v0`
  - `edit-pack/v0`
- Adapters:
  - rustc JSON diagnostic suggestions
  - `cargo fix` / edition-fix lanes
  - rust-analyzer assists / diagnostic fixes / SSR receipts where exportable
  - future assistant/bot edit proposals
- Docs:
  - edit-candidate provenance guide
  - conflict/ordering model guide
  - verification scope guide
  - editor-vs-CLI provenance guide
  - redaction/path-scrubbing guidance for attachable packs

## Why now (signals)
- The Cargo Book and Edition Guide already make automated edit application part of normal Rust workflows.
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Cargo’s 1.90 development-cycle report says current `cargo fix` architecture is slow, limited, and poor at selective application.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- The GSoC 2025 `cargo-fixit` prototype shows a more interactive, top-level-controlled architecture is feasible.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo’s 1.93 report explicitly says schema work could unblock a faster, more flexible `cargo fix` future.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The StableMIR publication goal says Rust wants semver-governed public compiler-facing crates for analyzers, linters, and development environments instead of direct dependence on compiler internals.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- rust-analyzer already offers a wide and growing surface of assists, SSR, renames, and diagnostic fixes, but those remain weakly attachable outside editor sessions.
  https://rust-analyzer.github.io/
  https://rust-analyzer.github.io/book/configuration
  https://rust-analyzer.github.io/thisweek/2020/07/06/changelog-32.html
  https://rust-analyzer.github.io/thisweek/2021/03/15/changelog-68.html
  https://rust-analyzer.github.io/thisweek/2024/12/16/changelog-264.html
- The 2025 State of Rust survey says official online docs remain canonical while LLM tooling and agentic/editor workflows are rising. That is a strong sign that the ecosystem needs a governed edit boundary, not just more edit producers.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Non-goals
- Replacing rustc, Cargo, rust-analyzer, or `rustfix`
- Guaranteeing that all edits can be auto-applied
- Defining one universal refactor language for all Rust tools
- Folding migration planning, lint policy, and semantic analysis into one schema
- Pretending that successful patch application implies correctness

## Strategic value
This kit is high leverage because it sits beneath many other useful Rust workflows:
- edition migrations,
- lint cleanup,
- API/semver remediation,
- IDE-assisted refactors,
- CI/review bots,
- and future assistant-driven maintenance.

It gives all of them the same missing boundary:
**candidate → selection → application → verification**.

The archive should now treat this as a ranked rollout problem, not a monolithic tool dream. See [`design/edit-governance-pilot-program.md`](../design/edit-governance-pilot-program.md).

That is the missing complement to Semantic Context Kit. One provides honest machine-usable context; the other provides honest machine-usable edit execution and review.

## Initial pilots
1. **Compiler suggestion / lint pilot**
   - collect compiler- and lint-originated candidates first, preserving applicability/provenance and proving explicit selection before application.
2. **Edition migration pilot**
   - model ordered migration waves, partial target/feature runs, `--broken-code`, and follow-up verification instead of relying on one opaque `cargo fix --edition` run.
3. **Editor-assist export pilot**
   - export a bounded rust-analyzer assist / SSR / rename batch into an attachable review pack.
4. **Assistant-proposal pilot**
   - allow assistant-originated changes only as weaker-authority reviewable candidates, after the earlier canonical-first lanes are already working.

## Milestones
1. **v0 candidate capture**
   - publish `edit-subject` + `edit-candidate-report`
   - support rustc/cargo-fix producer lane first
2. **v0.2 selection + apply**
   - add ordered selection plans and applied-result reporting
3. **v0.3 verification**
   - add verification reports with configurable scope and explicit incompleteness
4. **v1 multi-producer composition**
   - support at least three materially different producers (compiler suggestions, Cargo fix, rust-analyzer or equivalent editor/refactor lane)

## What success looks like
- A maintainer can attach an `edit-pack/v0` to a PR or issue and reviewers can see what was proposed, what was selected, and what was verified.
- Cargo can evolve `cargo fix` architecture without inventing a one-off private interchange.
- Editor-native refactors can leave the editor and enter normal review/CI workflows.
- Migration and lint workflows can stop treating applied edits as inseparable from hidden tool behavior.

## Archive fit
This epic fills a real hole between existing archive threads:
- **Compile Guidance Kit** owns diagnostics, lint catalogs, and hook surfaces.
- **Lint Baseline Kit** owns lint policy, debt baselines, and finding normalization.
- **Migration Kit** owns destination-aware change plans.
- **Semantic Context Kit** owns the cross-crate data plane many edit producers depend on.

But none of those owns the portable, reviewable *execution layer* for edit candidates themselves.
That is the missing substrate this epic is meant to supply.
