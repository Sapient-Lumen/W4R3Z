> Refresh note (rev0410): this stack is now read as a first-class **Defect Escalation Contract**.
> Use `design/defect-escalation-contract-2026Q1.md` for the frontier-level statement; use this file for the deeper stack decomposition and artifact sketches.

# Design: Defect Escalation Stack (Prototype Elevation + Feedback Loop + Cargo Report + rustc contribution workflows)

## Goal
Treat the route from **local Rust failure / weirdness / regression suspicion** to **actionable upstream artifact** as a first-class ecosystem seam.

The missing contribution is **not** another issue template, another crash uploader, another hidden minimizer bot, or another hosted triage dashboard.
It is a thin, reviewable layer that keeps these truths separate while letting them compose:
- **observation/session truth** — what the user actually saw, on which toolchain/workflow/subject, with what local evidence;
- **minimized subject truth** — what standalone script, repo slice, test, or reduced case still demonstrates the problem;
- **escalation-target truth** — whether the right next consumer is Cargo, rustc, rustdoc, Clippy, Miri, LLVM, docs, a crate maintainer, or local support;
- **dedup/search truth** — what prior issues or likely-duplicates were consulted, and how the new report was distinguished;
- **regression/handoff truth** — what regression-test candidate, reproduction fixture, or upstream-fix lane may legitimately import next.

That separation matters because many Rust problems fail today in one of two bad ways:
- evidence remains local and never becomes actionable upstream; or
- the escalation artifact hides how the issue was minimized, classified, or distinguished from prior work.

## Why this seam matters now
Fresh official Rust signals line up unusually well:
- The active cargo-script goal says single-file packages should reduce friction for **bug reports**, teaching material, prototypes, and small utilities, and explicitly calls out today’s tendency to under-specify repro cases.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-script.html
- The January 2026 program-management update says cargo script is especially good for **minimal bug reproducers** and quick prototypes because being able to share one file or paste it into Markdown makes a practical difference.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- The Cargo build-analysis goal and Cargo 1.94 work make **machine-usable local evidence** more real through `cargo report rebuild`, `cargo report sessions`, and timing history tied to a build identifier.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Rust release notes still explicitly ask users to test nightly and **report bugs early**, which means the project is actively asking for better escalation, not merely better local coping.
  https://doc.rust-lang.org/beta/releases.html
- The rustc-dev-guide’s fuzzing guide now gives a concrete reporting contract: verify on latest nightly, include a **reasonably minimal standalone example**, fill in the template information, search for existing reports, and format the test case.
  https://rustc-dev-guide.rust-lang.org/fuzzing.html
- The rustc-dev-guide’s testing docs say minimized bug reports should become **succinct regression tests**, which means a good escalation path should already anticipate testability and not stop at prose.
  https://rustc-dev-guide.rust-lang.org/tests/adding.html
- The compiler team’s triage docs say regressions and high-priority bugs are actively tracked, which means escalation artifacts have a real upstream consumer rather than being archival noise.
  https://rustc-dev-guide.rust-lang.org/compiler-team.html
- The March 20, 2026 challenges post and the 2026 debugging survey both reinforce that debugging, compiler errors, and ongoing friction remain live ecosystem pain points; a better escalation boundary is one of the few improvements that helps both users and maintainers.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/

## Current archive decision
The right contribution is **not**:
- a universal “file bug” wizard,
- a tool that silently strips context until the report becomes misleading,
- a hosted issue portal that competes with upstream trackers,
- or a local assistant that fabricates component ownership and duplicate status.

It is a stack with explicit boundaries:
- [`design/prototype-elevation-stack.md`](./prototype-elevation-stack.md) owns the move from tiny subject to reviewable project when the issue needs more structure.
- [`design/feedback-loop-stack.md`](./feedback-loop-stack.md) owns local build/debug/session evidence.
- [`design/cargo-report-kit.md`](./cargo-report-kit.md) owns machine-usable Cargo build/report artifacts.
- [`design/debuggability-stack.md`](./debuggability-stack.md) owns failure/debug/repro evidence after local investigation.
- A new **Defect Escalation Stack** should own the explicit route from those local artifacts to a reviewable upstream issue or regression-test candidate.

## What a worthy contribution would look like in practice
### 1) Make “do not escalate yet” a first-class outcome
A credible escalation stack must be able to say:
- fix locally first,
- collect more evidence first,
- minimize first,
- ask a crate maintainer first,
- escalate to a Rust project tracker,
- escalate to an upstream dependency like LLVM,
- or attach as a regression-test candidate to an existing issue/PR.

Without that, every confusing local failure becomes an unhelpful upstream report.

### 2) Preserve the observed subject before minimization changes it
The stack should preserve:
- original subject identity,
- original toolchain tuple,
- whether the problem was seen on stable/beta/nightly,
- exact command lane (`check`, `build`, `test`, `clippy`, rust-analyzer, etc.),
- raw error family / symptom summary,
- and any attached `cargo report` / debugger / log evidence.

Otherwise the minimized report stops being traceable back to the thing that actually failed.

### 3) Make minimization explicit, not magical
A strong escalation path must say how the case changed:
- script reduction,
- repo slicing,
- dependency removal,
- target/toolchain narrowing,
- feature narrowing,
- environment pinning,
- or IR / lower-level reduction when escalation moves downstream.

The difference between **observed case** and **report case** is one of the main truths that existing issue templates usually lose.

### 4) Keep target ownership and duplicate posture visible
A good pack should record:
- expected component / team / repo,
- consulted related issues or searches,
- why this appears distinct,
- whether the same symptom might belong to another layer,
- and whether the report is still `uncertain-owner` or `possible-duplicate`.

That matters because useful escalation is as much about routing honesty as about minimization.

### 5) Treat regression-test handoff as a native outcome
A good defect path should be able to end in:
- standalone reproducer,
- upstream issue,
- linked regression-test candidate,
- fix PR with reviewed test,
- or “needs additional local evidence”.

The stack should not assume that “GitHub issue created” is the finish line.

## Suggested artifact family
A good epic candidate should add only a thin composition family:
- `defect-observation/v0`
- `defect-minimization-report/v0`
- `defect-routing-report/v0`
- `defect-regression-candidate/v0`
- `defect-escalation-pack/v0`

### `defect-observation/v0`
Defines:
- original subject identity,
- toolchain/workflow/session identity,
- symptom family,
- attached Cargo/debug/repro evidence,
- user-visible observed-vs-expected statement,
- redaction posture.

### `defect-minimization-report/v0`
Records:
- original subject → minimized subject lineage,
- steps removed or normalized,
- what still reproduces,
- what became `unchecked`,
- whether the result is one-file/script/repo-slice/test-case/IR,
- confidence that the minimized case is faithful.

### `defect-routing-report/v0`
Records:
- likely target (`cargo`, `rustc`, `rustdoc`, `clippy`, `miri`, `llvm`, `crate`, `docs`, `other`),
- consulted prior issues/searches,
- duplicate posture,
- confidence / uncertainty,
- required next information,
- suggested issue-title atoms and labels when known.

### `defect-regression-candidate/v0`
Records:
- whether the minimized case is suitable as a regression test,
- probable test family (`ui`, `run-pass`, `codegen`, `cargo`, `rustdoc`, etc.),
- what remains to make it mergeable,
- whether expected output / directives are still missing,
- links to prior issue or PR if any.

### `defect-escalation-pack/v0`
Thin bundle linking:
- observation,
- minimization,
- routing,
- regression-candidate,
- attached Cargo/debug/build artifacts,
- issue or PR links when they exist,
- checksums and generator identity.

## Shared success criteria
A strong defect-escalation contribution should let a reviewer answer six questions quickly:
1. What actually failed, and in which local workflow?
2. What minimal subject still demonstrates the problem?
3. What changed between the observed case and the report case?
4. Which upstream consumer is the best fit, and how certain is that?
5. What duplicate or prior-art search was already done?
6. Is the result merely an issue, or is it also a regression-test candidate / fix handoff?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## Ranked opportunity inside this stack
1. **local failure → minimal standalone repro lane**
2. **minimal repro → actionable upstream issue lane**
3. **issue → regression-test candidate lane**
4. **cargo/debug/build evidence import lane**
5. **cross-repo routing lane** (crate vs Cargo vs rustc vs LLVM)

That order matters. The archive should not jump straight to automated cross-repo filing.

## Boundaries / non-goals
- not a replacement for upstream issue trackers,
- not a replacement for Cargo Report,
- not a replacement for debugger or replay tools,
- not a replacement for compiler-team triage,
- not a justification for auto-filing low-quality issues,
- not a promise that ownership or duplication can always be inferred mechanically.

## Why this is an ecosystem contribution, not just workflow polish
Rust is simultaneously making it easier to create **tiny precise reproducers** and to attach **machine-usable local evidence**.
That means the next missing question becomes unavoidable:
> how does a local Rust problem become an actionable upstream artifact without losing the truth of what was observed, how it was minimized, and whether it can become a regression test?

A real **Defect Escalation Stack** would answer that with bounded artifacts and explicit handoffs instead of folklore, vague issue templates, or assistant guesswork.
