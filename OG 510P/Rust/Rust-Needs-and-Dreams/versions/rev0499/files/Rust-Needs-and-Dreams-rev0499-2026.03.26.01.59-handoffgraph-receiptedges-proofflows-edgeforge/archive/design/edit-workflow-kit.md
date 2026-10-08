
## Execution addendum (rev0447)
`design/reviewable-edit-execution-blueprint-2026Q1.md` is now the repo's primary answer to **what this kit should actually become in theory and practice**.
Read it first when the question shifts from “is an edit workflow kit a good idea?” to “what exact layer, proving lanes, and boundary rules should a worthy implementation follow?”

# Design: Edit Workflow Kit (`cargo editflow`, `edit-pack/v0`)

## Goal
Define a portable, reviewable contract for **candidate edits, selection plans, application runs, and verification evidence** across Rust edit producers:
- compiler suggestions,
- `cargo fix` / edition-fix lanes,
- lint fixes,
- rust-analyzer assists / code actions,
- structural search-replace,
- rename / extract / inline style refactors,
- and future assistant- or CI-generated edit proposals.

This should help answer:
- what edit candidates were produced?
- what subject/context were they derived against?
- which candidates conflicted or depended on each other?
- which edits were approved versus only suggested?
- what actually applied?
- what verification ran after the changes?

This is **not** another editor, another lint engine, another refactor tool, or a promise that all edits can be fully automated.
It is the missing review boundary over edit-producing systems.

## References (signals)
- `cargo fix` already applies compiler suggestions and supports edition and idiom migration modes.
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- The Edition Guide says `cargo fix --edition` may loop multiple times and that advanced cases can require partial/manual work or custom `rustfix`-based tooling.
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- Rust 1.85 / Rust 2024 guidance still treats migration as a staged workflow with follow-up checks/tests after `cargo fix`.
  https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- Cargo’s 1.90 development-cycle report says current `cargo fix` architecture is slow, applies only a subset of possible lints, and makes selection hard because it runs through a `rustc`-proxy mode with locking.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- The GSoC 2025 results say `cargo-fixit` moved control to the top-level tool, removed the locking bottleneck, and opened the door to interactive selection.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo’s 1.93 development-cycle report explicitly connects schema unification to a better `cargo fix` architecture.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The 2025 State of Rust survey says official online docs remain canonical while LLM tooling and agentic/editor workflows are rising. That makes reviewable edit governance more urgent: more candidate edits will exist, but they should not bypass normal evidence and review.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `rustc` already emits structured JSON diagnostics with suggestions and applicability metadata.
  https://doc.rust-lang.org/beta/rustc/json.html
  https://doc.rust-lang.org/beta/nightly-rustc/rustfix/diagnostics/index.html
- rust-analyzer is a major provider of code actions/assists, supports commands such as `rust-analyzer.ssr`, and exposes assist-quality configuration like term-search borrow checking.
  https://rust-analyzer.github.io/
  https://rust-analyzer.github.io/book/configuration
  https://rust-analyzer.github.io/book/other_editors.html
- rust-analyzer changelogs show concrete edit capabilities including SSR command support, apply-SSR assist, extract/inline assists, rename protections, and diagnostic fixes.
  https://rust-analyzer.github.io/thisweek/2020/07/06/changelog-32.html
  https://rust-analyzer.github.io/thisweek/2021/03/15/changelog-68.html
  https://rust-analyzer.github.io/thisweek/2024/12/16/changelog-264.html
- See also the ranked rollout in [`design/edit-governance-pilot-program.md`](./edit-governance-pilot-program.md).

## The missing seam
Rust has increasingly good edit *producers*, but weak edit *governance* and *interchange*.

That matters more now because the ecosystem is moving toward richer machine-produced edits from Cargo, IDEs, and assistants. The worthy contribution is not to crown one producer. It is to make the edit boundary reviewable enough that more producers do not simply mean more opaque working-tree mutation.

Today:
- the compiler can propose changes,
- Cargo can apply some of them,
- rust-analyzer can propose many editor-native assists,
- migrations may require ordered/manual/custom steps,
- and future tools can synthesize more suggestions,

but there is still no shared, reviewable answer to:
1. what was proposed?
2. by which producer and confidence class?
3. under which subject/context?
4. what conflicts or prerequisites existed?
5. what got selected and why?
6. what actually applied?
7. how was the result verified?

That leaves edit workflows fragmented across:
- editor sessions,
- ad hoc shell loops,
- Cargo-internal behavior,
- raw compiler JSON,
- and human memory.

## Core UX: `cargo editflow`
- `cargo editflow collect`
  - gather candidate edits from selected producers and emit `edit-candidate-report/v0`
- `cargo editflow plan`
  - select / reject / defer candidates, order them, and emit `edit-selection-plan/v0`
- `cargo editflow preview`
  - render grouped previews and conflict summaries without touching the working tree
- `cargo editflow apply`
  - apply the selected plan and emit `edit-apply-report/v0`
- `cargo editflow verify`
  - run configured checks and emit `edit-verify-report/v0`
- `cargo editflow diff --against <pack|path|git-ref>`
  - compare plans, applications, or outcomes and emit `edit-diff-report/v0`
- `cargo editflow pack`
  - bundle all artifacts into `edit-pack/v0`

The reference implementation should begin as an **adapter / planner / packer**, not as a universal rewrite engine.

## Canonical-first handoff
`cargo editflow` should assume that **producer output is not the same thing as canonical Rust truth**.

In practice:
- compiler diagnostics, Cargo selection/build context, rustdoc JSON, docs.rs inputs, and compiler-export lanes remain canonical or near-canonical evidence;
- `cargo editflow` may *reference* semantic context from [`design/semantic-context-kit.md`](./semantic-context-kit.md), but should not silently duplicate or reinterpret it;
- editor- or assistant-originated proposals should travel as weaker-authority candidates rather than as facts;
- and any move from candidate discovery to branch mutation should require an explicit `edit-selection-plan/v0`.

Design rule: **the working tree is downstream of evidence, not the source of it**.


## Artifact family

### `edit-subject/v0`
Describes the subject against which edits were produced.

Should include:
- workspace/package/member identity
- manifest + revision / snapshot pointers
- target/profile/features/cfg/toolchain/edition selection
- selected file set / module scope where relevant
- producer environment notes when relevant (e.g. editor/LSP vs CLI batch)
- source-of-truth class:
  - local workspace
  - CI run
  - editor session snapshot
  - imported pack

Design rule: **edits are only meaningful relative to an explicit subject**.
A rename proposed for one feature set or file snapshot is not automatically valid for another.

### `edit-candidate-report/v0`
Catalog of edit candidates discovered.

For each candidate record:
- candidate id
- producer identity + version
- candidate family:
  - compiler suggestion
  - lint fix
  - edition fix
  - assist/code action
  - SSR/refactor rule
  - rename/extract/inline/grouped refactor
  - assistant proposal
- affected files/ranges
- replacement hunks or abstract edit operations
- applicability / confidence class
- reason codes / triggering diagnostics when available
- prerequisite / unlock relationships
- overlap/conflict classes
- formatting/import side-effect notes where relevant

Design rule: **candidate discovery is not selection**.
This artifact must preserve the full field of possible edits.

### `edit-selection-plan/v0`
Records which candidates were chosen and why.

Should include:
- selected / rejected / deferred candidate ids
- grouping into ordered waves or phases
- conflict-resolution choices
- review policy (`manual-review-required`, `auto-apply-machine-applicable-only`, etc.)
- protected files/paths/selectors
- producer allow/deny lists
- rationale notes and waivers

Design rule: **selection is first-class**.
The ecosystem needs something better than “whatever the tool happened to auto-apply”.

### `edit-apply-report/v0`
Records what actually happened during application.

Should include:
- plan id and subject id
- pre/post snapshot ids or tree digests
- which candidates applied cleanly
- which partially applied, conflicted, or were skipped
- rewritten file inventory
- auto-format / import-organize / follow-up normalization steps
- manual intervention markers
- unchanged candidate leftovers

Design rule: **application truth must be explicit**.
A selected plan and an applied result are different facts.

### `edit-verify-report/v0`
Records the evidence used to validate the edited tree.

May include:
- `cargo check` / `cargo test` results
- feature/target/profile matrix coverage
- format / lint reruns
- edition migration checks
- API / downstream / docs checks when linked
- stale/incomplete verification markers

Design rule: **verification is not implied by successful patch application**.

### `edit-diff-report/v0`
Structured comparison between two edit plans or outcomes.

Should include:
- changed subject/context
- changed candidate sets
- changed selection policy
- changed applied files/hunks
- changed verification outcomes
- comparability class:
  - comparable
  - partially comparable
  - incomparable

Design rule: **do not fake precision across changed subjects or producers**.

### `edit-pack/v0`
Bundle containing:
- `edit-subject.json`
- `edit-candidate-report.json`
- optional `edit-selection-plan.json`
- optional `edit-apply-report.json`
- optional `edit-verify-report.json`
- optional `edit-diff-report.json`
- optional raw attachments:
  - rustc JSON diagnostics
  - cargo-fix / cargo-fixit traces
  - rust-analyzer assist/SSR receipts
  - patch previews
  - before/after file digests

## Design principles
- **Separate discovery, selection, application, and verification.** These are different truths.
- **Keep producer identity visible.** Compiler suggestions, assists, and SSR rules are not interchangeable.
- **Represent conflicts honestly.** Overlap and ordering matter.
- **Prefer reviewable groups over giant patches.** Edit batches should be phaseable.
- **Verification must be attachable.** “Tool succeeded” is not enough.
- **Do not erase editor/CLI differences.** A code action from one editor session should not masquerade as a Cargo-native fact.

## Overlap boundaries
- **Not Compile Guidance Kit:** that kit owns diagnostic/lint/help surfaces and hook metadata; Edit Workflow Kit owns candidate-edit selection/application/verification.
- **Not Lint Baseline Kit:** lint profiles, debt baselines, and finding governance stay there; this kit consumes fix candidates derived from those findings.
- **Not Migration Kit:** migration intent, staged destination planning, and broader non-source changes stay there; this kit can supply the source-edit execution layer inside a migration.
- **Not Semantic Context Kit:** semantic capture/query inputs stay there; this kit can consume semantic context when generating or validating edits.
- **Not Public API Kit:** semver/MSRV/public-dependency verdicts stay there; this kit may carry edits used to satisfy those verdicts.

## Initial adapter lanes
1. **Compiler-suggestion lane**
   - rustc JSON diagnostics + applicability
2. **Cargo fix lane**
   - edition / idiom / broken-code aware application records
3. **rust-analyzer assist lane**
   - code actions, diagnostic fixes, grouped assists
4. **SSR / structured refactor lane**
   - rule text, match scope, replacements, replay info
5. **Future assistant lane**
   - proposed edits with weaker authority and stronger review requirements

## Hard problems (explicitly scoped)
1. **Edit stability across shifting snapshots**
   - spans and AST paths can go stale quickly; v0 should preserve snapshot identity and allow “candidate stale” as a first-class outcome.
2. **Conflict modeling**
   - overlapping hunks, semantic dependency order, and auto-format side effects need honest representation.
3. **Producer heterogeneity**
   - some producers emit direct text edits, some emit structured operations, some only expose UI actions.
4. **Confidence is not binary**
   - machine-applicable compiler suggestions, borrow-checked term-search assists, and speculative assistant proposals should not be flattened together.
5. **Verification scope drift**
   - a small verified file-level change and a whole-workspace green run are different kinds of evidence.

## What the kit should provide to others
- **Maintainers:** selective, reviewable edit batches instead of opaque auto-fix runs.
- **Cargo evolution:** a schema target for future `cargo fix` architecture work.
- **IDE/editor tooling:** a durable export/review boundary for assists and refactors.
- **Migration tooling:** a source-edit execution layer that composes with broader plans.
- **Agents / bots:** bounded edit proposals that can be attached, reviewed, replayed, or rejected.

## Why this could be epic
If done well, this is not merely one more helper crate.
It becomes the shared substrate that lets Rust move from “many tools can suggest edits” to “teams can *govern* and *reuse* edit workflows”.
