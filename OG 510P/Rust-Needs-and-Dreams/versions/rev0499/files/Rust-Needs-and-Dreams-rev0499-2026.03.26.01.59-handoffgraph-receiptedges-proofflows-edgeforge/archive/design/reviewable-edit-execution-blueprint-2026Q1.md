# Design: Reviewable Edit execution blueprint (2026 Q1)

## Goal
Turn the archive's repeatedly promoted **reviewable Rust mutation / selection / verification** seam into a sharper **buildable program**.

The missing contribution is not a universal refactoring platform, not a privileged assistant that rewrites the working tree, not an IDE export gimmick, and not a proof that every machine-produced patch is correct.
It is a disciplined companion layer that lets Rust tools share **portable reviewable-edit truth** across migrations, lint cleanup, IDE assists, CI automation, and agent proposals without pretending those producers all carry the same authority.

Read this note when the question is narrower than the broad ladder:

> if a serious Rust team decides to build the archive's clearest mutation/review/handoff seam, what should **Reviewable Edit** actually ship in theory and practice?

Read with:
- `design/reviewable-edit-contract-2026Q1.md`
- `design/edit-workflow-kit.md`
- `proposals/epic-edit-workflow-kit.md`
- `design/semantic-context-kit.md`
- `design/migration-kit.md`
- `design/worthy-contribution-shortlist-2026Q1.md`
- `design/ideal-rust-worthy-contributions-2026Q1.md`

## Why this note is needed now
The archive already knew that **Reviewable Edit Contract** was strategically real.
What it still lacked was a crisper answer to **what that contribution should actually look like**.

Fresh primary signals sharpen that answer:
- Cargo's 1.90 development-cycle post says the current `cargo fix` architecture is slow, only applies a subset of lints, and is hard to make selective or interactive because it uses a `rustc`-proxy loop with a cross-process lock.
  https://blog.rust-lang.org/inside-rust/2025/10/01/this-development-cycle-in-cargo-1.90/
- The GSoC 2025 `cargo-fixit` prototype says top-level control over which fixes apply can remove the locking bottleneck and opens the door to interactive modes, but also says more work is needed.
  https://blog.rust-lang.org/2025/11/18/gsoc-2025-results/
- Cargo's 1.93 development-cycle report says schema unification with Cargo JSON/report surfaces could unblock a faster, more flexible future `cargo fix` architecture.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- The Cargo Book says `cargo fix` automatically applies compiler suggestions only for the code that `cargo check` actually sees, so target/feature-specific code may require multiple runs.
  https://doc.rust-lang.org/cargo/commands/cargo-fix.html
- The Edition Guide says `cargo fix --edition` uses special lints, may loop multiple times, can back out failed fixes, and still may require multiple feature/target passes, `--broken-code`, editor quick-fixes, or custom tooling for advanced cases.
  https://doc.rust-lang.org/edition-guide/editions/advanced-migrations.html
- rustc's JSON output already exposes structured diagnostics with suggestion spans, replacements, and applicability classes like `MachineApplicable`, `MaybeIncorrect`, and `HasPlaceholders` — a strong reason to preserve candidate provenance and confidence rather than flattening everything into “patches”.
  https://doc.rust-lang.org/beta/rustc/json.html
- The StableMIR publication goal says Rust wants semver-governed public compiler-facing crates so tool developers can build analyzers and development environments without depending directly on compiler internals. That is exactly the kind of upstream substrate a durable edit boundary wants to sit beside.
  https://rust-lang.github.io/rust-project-goals/2025h1/stable-mir.html
- rust-analyzer already exposes meaningful edit surfaces — assists, cargo invocation/configuration knobs, and rename-conflict warnings — but those workflows still leave weak portable receipts once they escape the editor session.
  https://rust-analyzer.github.io/book/configuration
  https://rust-analyzer.github.io/thisweek/2025/02/24/changelog-277.html
- The 2025 State of Rust survey says online docs remain the canonical reference while editors with agentic support are rising. That is a strong reason to prefer a governed review boundary over direct assistant mutation.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

Taken together, those signals say the archive should stop describing Reviewable Edit only as a good boundary idea.
It should describe a real contribution shape.

## Headline answer
If one serious team wants to build the archive's clearest mutation/review/handoff contribution, the answer should now be:

> Build a **Reviewable Edit reference layer** that captures exact edit subjects, imports heterogeneous candidate lanes honestly, preserves selection/application/verification boundaries explicitly, and emits reusable packs and handoffs for CI, PR review, migration work, editor exports, and assistants.

That answer is deliberately narrower than “solve refactoring in Rust”.
It is also deliberately stronger than “make `cargo fix` faster”.

## What this contribution should be in theory

### Core thesis
A reviewable-edit system becomes ecosystem infrastructure when it can answer all of these from one reviewable pack:
1. **what exact edit subject is under discussion** — workspace/package/member identity, manifest/revision snapshot, targets/features/cfg/toolchain/edition, and selected file/module scope where relevant;
2. **what candidate lanes are being imported** — compiler suggestions, lint fixes, edition migration edits, assists/code actions, rename/SSR/refactor operations, or assistant/bot proposals;
3. **what provenance and confidence applied** — producer identity/version, diagnostic roots, applicability/confidence class, prerequisite relationships, and overlap/conflict posture;
4. **what selection and ordering decisions were made** — chosen/deferred/rejected candidates, grouping into waves, protected files, allow/deny lists, and explicit rationale;
5. **what actually happened on application** — pre/post snapshots, clean applies, skipped or drifted candidates, formatting/import side-effects, and manual interventions;
6. **what each downstream consumer is allowed to claim** — PR review, CI gating, migration progress, editor export, or assistant follow-up.

If a project cannot answer those questions without editor memory, shell history, and human folklore, it is not yet the contribution the archive is pointing at.

### Boundary rule
The contribution should stop at **portable edit truth and handoff**.

It should include:
- subject/context binding;
- candidate provenance and confidence;
- first-class selection/ordering;
- application receipts;
- scoped verification receipts;
- bounded diffing and explanation;
- consumer-specific exports and redactions.

It should not become:
- the new universal refactoring engine;
- the IDE itself;
- a one-true migration planner;
- a lint-policy layer;
- a branch-management bot;
- or a proof system that equates “patch applied” with correctness.

### Separation rule
The contribution must preserve at least six distinct truth classes:
- **subject truth** — what code/configuration snapshot the edits were derived against;
- **candidate provenance truth** — what produced each candidate and with what authority/confidence;
- **selection truth** — what was chosen, deferred, rejected, and in what order;
- **application truth** — what actually changed, drifted, conflicted, or required intervention;
- **verification truth** — what checks were rerun and what remains unverified;
- **consumer-handoff truth** — what a specific review/CI/editor/assistant consumer may import.

This is the biggest theory/practice guardrail in the whole design.
Without it, every downstream consumer turns into a hidden fork of edit truth.

### Lane hierarchy rule
A worthy v0 should prefer edit lanes in this order:
1. **compiler/Cargo-authoritative suggestion lanes**;
2. **edition and migration-oriented fix lanes**;
3. **editor/refactor lanes with explicit exportability and bounded authority**;
4. **assistant/bot proposal lanes as weaker-authority candidates**;
5. **consumer-derived summaries and automation reports**.

That order is strategic, not merely technical.
It keeps the strongest currently-reviewable facts ahead of the highest temptation to over-claim autonomy.

## What this contribution should be in practice

### Reference tool shape
A serious v0 should probably look like a thin companion tool and schema family:
- `cargo editflow collect`
- `cargo editflow plan`
- `cargo editflow preview`
- `cargo editflow apply`
- `cargo editflow verify`
- `cargo editflow diff`
- `cargo editflow explain`
- `cargo editflow handoff --to <pr|ci|migration|editor|assistant>`
- `cargo editflow pack`
- `cargo editflow doctor`

The tool should **import** compiler/Cargo/editor/service surfaces when available rather than replacing them.

### Public artifact spine
Keep the current family, but make the public review shape more explicit:
- `edit-subject/v0`
- `edit-candidate-report/v0`
- `edit-selection-plan/v0`
- `edit-apply-report/v0`
- `edit-verify-report/v0`
- `edit-diff-report/v0`
- `edit-explanation/v0`
- `edit-handoff/v0`
- `edit-pack/v0`

### First proving lanes
A credible rollout should rank proving lanes instead of pretending every producer must land at once.

#### Lane 1 — compiler suggestion / Cargo-fix import lane
Start where authority is strongest and semantics are already structured.
The v0 must prove that rustc/Cargo-originated suggestions can be imported as candidates without losing applicability/confidence, and that maintainers can select a bounded subset rather than accepting one opaque auto-apply run.

What to prove:
- import rustc/Cargo suggestions with source diagnostic IDs and applicability classes intact;
- scope by package/member/target/features/edition/toolchain;
- show ordered apply receipts and post-verify receipts;
- make “machine-applicable only” an explicit selection policy rather than an implied trust class.

#### Lane 2 — edition migration lane
Edition work is where Rust already tolerates automation but still carries real partiality and manual follow-up.
This makes it an excellent proving lane for ordered waves, partial coverage, and explicit incompleteness.

What to prove:
- multiple target/feature passes;
- migration waves grouped by lint family or edition step;
- support for `--broken-code` and other incompleteness markers without pretending migration is finished;
- attachable receipts reviewers can understand after the fact.

#### Lane 3 — editor/refactor export lane
rust-analyzer and adjacent tooling already provide useful rename/assist/refactor power.
The missing proof is not more editor capability; it is that those edits can leave the editor honestly.

What to prove:
- export bounded assists/renames/SSR batches into candidate reports or apply receipts;
- preserve editor provenance and weaker-authority posture where semantic guarantees differ from compiler suggestions;
- capture rename-conflict warnings or semantic-meaning-change risks as first-class evidence, not hidden UX.

#### Lane 4 — assistant/bot proposal lane
This lane matters strategically, but should arrive only after canonical-first lanes are solid.
The ecosystem needs a way to attach assistant proposals without letting them impersonate compiler truth.

What to prove:
- assistant-originated candidates enter as weaker-authority `edit-candidate-report` records;
- packs can carry redaction and path-scrubbing posture for issue/PR attachment;
- no assistant proposal may skip selection or verification receipts.

#### Lane 5 — consumer handoff lane
Only after the earlier lanes work should the pack become a broader routing substrate for CI bots, PR review, or future support systems.

What to prove:
- CI can import verify/apply summaries without claiming semantic correctness;
- code review can see chosen/deferred/rejected candidates and why;
- migration or maintenance dashboards can reference packs without silently becoming the system of record.

## What to refuse
A worthy contribution here must refuse the most tempting wrong shapes:
- a universal refactor language or AST-rewrite empire;
- direct assistant ownership of the working tree;
- flattening compiler suggestions, editor assists, and assistant proposals into one confidence class;
- treating successful apply as equivalent to correctness;
- hiding configuration/target/feature partiality;
- or making the review pack depend on one IDE, one hosted service, or one bot platform.

## Ranking and repo consequence
This revision does **not** rewrite the broad ladder.
It does **not** outrank **Build-State Evidence** overall.
It does **not** displace **Feedback Loop / Debuggability Acceptance** as the clearest under-ranked day-to-day missing middle.

What it does do is make one repeatedly promoted seam explicit:
- **Reviewable Edit** is now the clearest remaining **mutation / review / handoff execution blueprint** in the archive;
- its primary shape is **reference layer + report/pack command + adapter/acceptance corpus**;
- **Semantic Context Kit** remains the adjacent context substrate and **Migration Kit** remains an important imported planning layer, but neither is the same thing as the portable edit boundary itself;
- and future Rust-facing agent workflows should be understood as downstream consumers of this layer, not its replacement.

That gives the archive a better answer to a question that is only getting more central:
How should Rust let humans, CI, editors, and agents propose and review changes **without** smearing compiler truth, producer authority, and verification into one opaque patch event?
