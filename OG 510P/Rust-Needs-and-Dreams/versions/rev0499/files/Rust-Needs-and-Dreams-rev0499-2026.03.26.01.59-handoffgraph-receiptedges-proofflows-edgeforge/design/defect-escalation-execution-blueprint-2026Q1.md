# Design: Defect Escalation execution blueprint 2026Q1

## Question
Once the archive accepts that Rust bug reporting, minimization, routing, and regression-test handoff are strategically important, what should the worthy contribution actually become before it dissolves into “just improve the issue template”, “just use cargo script”, “just bisect with cargo-bisect-rustc”, or “just let an assistant file the issue for you”?

## Short answer
A worthy contribution here is a **reference layer + report/pack command + adapter/import corpus** for **observed-failure truth**, **minimization-lineage truth**, **routing/dedup truth**, **regression-candidate truth**, **evidence imports**, and **bounded consumer handoff**.

Not another issue form.
Not a silent minimizer.
Not an auto-filing bot.
Not a hosted bug portal that outruns local truth.

In repo language, the missing thing is closer to **`cargo defectpack` + `defect-escalation-pack/v0`** than to a new tracker or triage dashboard.

## Why this seam is execution-worthy now
The ecosystem's current shape makes the missing layer unusually visible:
- The cargo-script goal says single-file packages should reduce friction for development and communication, explicitly including **bug reports**, and it calls out the current tendency to under-specify repro cases because multi-file sharing is awkward.
  https://rust-lang.github.io/rust-project-goals/2024h2/cargo-script.html
  https://rust-lang.github.io/rfcs/3424-cargo-script.html
- The January 2026 program-management update says cargo script is particularly good for **minimal bug reproducers** and quick prototypes because one shareable file or Markdown code block materially lowers the cost of sharing a faithful reproducer.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- The 2026 flagship slate still lists **single-file scripts with dependencies** as an active higher-level-Rust milestone, which means the “tiny shareable subject” lane is not a side experiment anymore.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Forge triage already treats missing repros, MCVEs, and bisections as explicit workflow states (`E-needs-mcve`, `S-has-mcve`, `E-needs-bisection`, `S-has-bisection`) rather than as vague etiquette. That proves routing and evidence posture are already real upstream semantics.
  https://forge.rust-lang.org/release/issue-triaging.html
- `cargo-bisect-rustc` remains the standard Rust tool for bisecting compiler regressions across nightlies or CI artifacts, which means the ecosystem already has a strong **bisection lane** but not a shared pack that records when and how that lane was exercised.
  https://github.com/rust-lang/cargo-bisect-rustc
- The rustc-dev-guide says bug-fix PRs should generally come with **regression tests**, and those tests should be succinct and derived from the actual bug report. That means a serious escalation layer should already anticipate regression-candidate handoff rather than stopping at prose.
  https://rustc-dev-guide.rust-lang.org/tests/adding.html
  https://rustc-dev-guide.rust-lang.org/tests/best-practices.html
- The libtest-JSON goal says people relied heavily on programmatic test output and that the experiment is about moving reporting responsibility upward toward Cargo and runners. That makes test/run evidence more importable into escalation packs.
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- Cargo's build-analysis direction is normalizing machine-usable local evidence through `cargo report` rather than hosted dashboards. That is exactly the sort of substrate a defect-escalation layer should import instead of reinventing.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The Rust project's own release notes still ask users to test nightly and **report bugs early**, which means better escalation is a present-tense project need rather than archive ornament.
  https://doc.rust-lang.org/beta/releases.html
- The March 2026 challenges post and the 2026 debugging survey both reinforce that debugging friction, compiler errors, and uneven operability remain ecosystem-wide pain points. A better escalation boundary is one of the few improvements that helps both the reporter and the maintainer.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
  https://blog.rust-lang.org/2026/03/13/2026-Debugging-Survey/

That combination means the missing contribution is no longer “someone should file better bugs”.
It is a **portable repro-to-routing-to-regression handoff layer**.

## What to refuse first
The wrong shapes are clear enough that the archive should reject them explicitly.

### Wrong shape 1 — one issue template as the answer
Templates matter, but they are downstream prose.
If the design cannot preserve observation, minimization lineage, routing posture, and regression candidacy independently of a form, it is too small.

### Wrong shape 2 — one assistant that auto-files issues
An assistant can help produce candidate packs.
It should not become the owner of routing truth, duplicate truth, or regression-candidate truth.

### Wrong shape 3 — one minimizer that forgets the original subject
Minimization is important, but the original observed subject is part of the evidence.
A silent reducer that loses the before-state is not enough.

### Wrong shape 4 — one tracker or hosted portal as the answer
GitHub issues, Zulip threads, and other trackers are consumers.
They should not have to own the semantic boundary between observed case, minimized case, and regression handoff.

### Wrong shape 5 — “cargo script plus cargo-bisect-rustc will solve it later”
Those are valuable lanes.
They are not the pack that keeps their results reviewable together.

## Execution thesis
The worthy contribution should be built as six visibly separate truth layers.

### 1) Observed-failure truth
The pack must preserve what was actually seen before minimization changes it.
Examples:
- original subject identity (repo, package, script, branch/revision)
- toolchain/channel/target/workflow tuple
- command lane (`check`, `build`, `test`, `clippy`, rust-analyzer, Miri, etc.)
- observed vs expected behavior
- attached local evidence imports such as `cargo report`, logs, or screenshots
- redaction posture and what was omitted

### 2) Minimization-lineage truth
The pack must show how the reported case differs from the observed case.
Examples:
- original → reduced subject lineage
- removed dependencies, features, cfgs, targets, or environment assumptions
- whether the resulting subject is a single-file script, repo slice, test case, or lower-level artifact
- what still reproduces and what became unchecked
- confidence that the reduced case is faithful

### 3) Routing and dedup truth
The pack must keep routing honesty visible.
Examples:
- likely owner or component (`cargo`, `rustc`, `rustdoc`, `clippy`, `miri`, `llvm`, crate, docs, uncertain)
- consulted related issues, searches, or prior reports
- possible-duplicate posture and confidence
- information still missing
- why the current target is preferred over neighboring layers

### 4) Regression-candidate truth
The pack must say whether the result is ready to become a test artifact.
Examples:
- likely test family (`ui`, `run-make`, `cargo`, `rustdoc`, crate-local, LLVM-side, etc.)
- whether the case is minimized enough for a mergeable regression test
- what directives, expected output, or fixture shaping still remain
- whether it already maps to an open issue or fix PR

### 5) Evidence-import truth
The pack must keep attached evidence distinct from the escalation layer itself.
Examples:
- `cargo report` session or rebuild receipts
- libtest or runner JSON outputs
- `cargo-bisect-rustc` outputs
- debugger or log attachments
- replay or trace attachments
- raw terminal transcripts

### 6) Consumer-handoff truth
The pack must say what later consumers may honestly import.
Examples:
- issue filing can import observation, minimization, and routing slices
- reviewers can import routing uncertainty and duplicate work already done
- fix authors can import regression-candidate posture
- assistants can summarize the pack, but not invent stronger routing or dedup claims than the pack declares

## What the artifact should look like in theory
A serious v0 should standardize a small family, not a monolith:
- `defect-observation/v0`
- `defect-minimization-report/v0`
- `defect-routing-report/v0`
- `defect-regression-candidate/v0`
- `defect-evidence-import/v0`
- `defect-escalation-pack/v0`

And one top-level command surface:
- `cargo defectpack report` — collect and normalize a local failure plus bounded imports into reviewable reports
- `cargo defectpack pack` — bundle those reports and attachments into `defect-escalation-pack/v0`
- optional follow-on verbs later: `doctor`, `explain`, `handoff`

The contract must preserve raw attachments by reference where needed:
- single-file script subject
- repo-slice tarball or git revision
- `cargo report` JSON or sessions output
- `cargo-bisect-rustc` transcript
- test-run JSON or harness output
- stack traces, logs, screenshots, or reduced IR artifacts

## What the artifact should look like in practice
The archive should now prefer these proving lanes, in order.

### Lane 1 — single-file repro lane
Cargo script or equivalent single-file subject.

Why first:
- proves the design can preserve a tiny shareable subject cleanly;
- aligns with current Cargo/Rust goals;
- gives the fastest possible demonstration that observation and minimized report can sometimes coincide honestly.

### Lane 2 — workspace-slice lineage lane
A real multi-package workspace case reduced to a smaller repo slice.

Why second:
- proves the design can keep observation truth separate from minimization lineage;
- exercises redaction and removed-context honesty;
- stops the schema from becoming script-only.

### Lane 3 — bisection import lane
`cargo-bisect-rustc` as an imported evidence family.

Why third:
- proves the design can hold timeline/regression evidence without pretending bisection alone identifies the final owner;
- gives regressions a first-class home.

### Lane 4 — uncertain-routing lane
Case ends in `uncertain-owner` or `possible-duplicate`.

Why fourth:
- proves the contract can remain honest under ambiguity;
- prevents the system from being forced into fake confidence.

### Lane 5 — regression-test handoff lane
Carry a reduced case forward into a credible regression-candidate report.

Why fifth:
- validates that escalation can end in something stronger than “issue filed”;
- matches actual rustc-dev-guide expectations.

## Strategic boundaries with adjacent seams
This blueprint is intentionally close to other strong archive seams, but it is not them.

### It is not Feedback Loop / Debuggability Acceptance
That layer owns local operability, debugger capability truth, and repro fitness under development stress.
Defect Escalation starts when the question becomes “what reviewable artifact can another maintainer or upstream team honestly consume?”

### It is not Cargo Report
`cargo report` should be an imported evidence source.
It does not own minimization lineage, routing posture, or regression candidacy.

### It is not Prototype Elevation
Prototype Elevation helps small subjects become reviewable Rust projects or artifacts.
Defect Escalation owns the route from observed failure to upstream issue or regression-test handoff.

### It is not Harness Protocol or Test Run Evidence
Those layers own execution and runner-native truth.
Defect Escalation should import them when relevant.

### It is not issue-tracker policy
Project-specific labels, nomination decisions, or backport policy belong downstream.
The escalation pack should only carry the bounded facts those consumers need.

## What a worthy first implementation should prove
A real v0 does not need to solve every Rust bug-reporting workflow.
It needs to prove these narrower claims:
1. a local observed failure can become a reviewable pack without losing the original subject;
2. the pack can preserve minimization lineage honestly;
3. the pack can attach evidence imports such as `cargo report` or bisection output without flattening them into the whole story;
4. the pack can end in uncertainty without collapsing;
5. and the pack can support issue filing and regression-test handoff as two distinct downstream consumers.

## What this contribution should not claim yet
Even a strong first version should stay honest about its limits.
It should not claim:
- fully automatic routing to the correct upstream owner;
- reliable duplicate detection;
- universal minimization;
- automatic conversion into mergeable tests;
- or stable schema coverage for every runner, debugger, or CI artifact on day one.

It should instead make those limits explicit inside the reports.

## Why this is worthy in the archive's ranking model
This seam is worthy because it reduces repeated private reinvention across users, maintainers, and teams while leaving behind machine-usable truth.
It improves a painful workflow advanced users and upstream teams already hit.
And it composes with the project's present direction instead of fighting it:
- tiny repro subjects are becoming more first-class;
- machine-usable local evidence is increasing;
- triage already depends on reproducibility and bisection;
- and regression tests remain the durable fix boundary.

That makes this a real execution-grade contribution, not merely workflow polish.

## Current archive decision
Treat **Defect Escalation** as the next execution seam worth sharpening beneath the archive's existing build/debug/control-plane band.
The right answer is now:
- **reference layer + report/pack command + adapter/import corpus**;
- bounded by observation, minimization, routing, regression-candidate, evidence-import, and consumer-handoff truth;
- with first serious proving lanes in single-file repro, workspace-slice lineage, bisection import, uncertain routing, and regression handoff;
- and with explicit refusal of issue-template, portal, minimizer-only, and assistant-autofile stories.
