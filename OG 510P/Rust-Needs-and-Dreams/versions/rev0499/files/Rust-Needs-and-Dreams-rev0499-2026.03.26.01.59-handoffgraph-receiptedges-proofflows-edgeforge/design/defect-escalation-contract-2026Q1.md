## Execution addendum (rev0453)
For questions about **what the archive's defect-escalation seam should actually ship once “better bug reports and reproducers matter” is no longer enough**, read `design/defect-escalation-execution-blueprint-2026Q1.md` immediately after this note.

Interpretation rule:
- the broad defect-escalation seam is unchanged;
- this revision says more explicitly what **Defect Escalation** should become in theory and practice;
- treat it as **reference layer + report/pack command + adapter/import corpus**;
- keep **Cargo Report**, **Feedback Loop / Debuggability Acceptance**, **Prototype Elevation**, and **Harness/Test evidence** as adjacent import layers rather than substitutes;
- and refuse the tempting wrong shapes first: one issue template, one auto-filing bot, one minimizer, or one hosted bug-report portal.

# Design: Defect Escalation Contract 2026Q1

## Goal
Promote the archive's repro / issue-routing substrate from “good local evidence plus a decent bug report” to a first-class **Defect Escalation Contract**: a reviewable boundary for **what was actually observed, how the case was minimized, what target and duplicate posture are honest, whether the result is test-worthy, and what issue / PR / regression-test consumers may legitimately import next**.

This contract should sit:
- **above** raw terminal output, ad-hoc Markdown snippets, one-off gists, and issue-template prose;
- **below** project-specific triage policy, release backport decisions, and long-horizon maintenance/funding workflows;
- and **beside** Cargo Report, Debuggability, Harness Protocol, and Prototype Elevation rather than replacing any of them.

The point is not to auto-file more issues.
The point is to stop losing truth when a local Rust failure turns into a “probably duplicate?” thread, a misleading MCVE, or a regression fix that no longer points back to the thing the user actually saw.

## Why this seam matters now
The case for a first-class escalation contract is stronger in 2026 than it was even a year ago:
- The 2025H2 goals explicitly say stabilizing `cargo script` should make reproducible bug reports easier.
- The February 2026 program-management update says single-file Rust is especially good for minimal bug reproducers and quick prototypes because it is materially easier to share.
- Forge triage already treats missing repros, MCVEs, missing info, and bisections as explicit workflow state instead of vague etiquette.
- The rustc-dev-guide says bug fixes should come with succinct regression tests, which means escalation should anticipate testability rather than stopping at prose.
- The libtest-JSON goal is explicitly about moving reporting responsibility upward toward Cargo and runners, which creates better machine-usable imports for escalation.
- Cargo 1.94 keeps making local build evidence more machine-usable through `cargo report rebuild` and `cargo report sessions`.
- The March 2026 challenges post and the 2025 survey both reinforce that debugging, resource usage, and persistent friction remain live enough that a better repro-to-regression lane would help both users and maintainers.

That combination means the missing contribution is no longer “a nicer issue template”.
It is a **portable escalation contract** that keeps observation, minimization, routing, and regression handoff visibly distinct.

## References (signals)
- 2025H2 Rust goals: `cargo script` should make small utilities, examples, and reproducible bug reports easier.
  https://rust-lang.github.io/rust-project-goals/
- February 2026 program-management update: `cargo script` is especially good for minimal bug reproducers and quick prototypes.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- Forge triage: explicit `S-needs-repro`, `S-needs-info`, `E-needs-mcve`, `E-needs-bisection`, `S-has-mcve`, and `S-has-bisection` workflow semantics.
  https://forge.rust-lang.org/release/issue-triaging.html
- rustc-dev-guide testing docs: fixes should come with regression tests, and tests derived from bug reports should be succinct/minimized.
  https://rustc-dev-guide.rust-lang.org/tests/adding.html
- 2025H2 libtest-JSON goal: reporting should shift upward toward Cargo/runners and lower the barrier for custom harnesses/runners.
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- Cargo 1.94: `cargo report rebuild` and `cargo report sessions` continue the build-analysis / machine-report direction.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- March 2026 challenges post and 2025 survey: debugging and persistent workflow friction remain ecosystem-wide pain points.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/

## Working thesis
A worthy contribution here should make it easy to answer all of these without guessing:
1. What exactly was **observed**, in which workflow, on which toolchain/target/context?
2. What **minimized subject** still demonstrates the problem?
3. What changed between the observed case and the minimized/report case?
4. What is the honest **routing posture**: Cargo, rustc, rustdoc, Clippy, Miri, LLVM, crate maintainer, docs, or “still uncertain”?
5. What prior-art or duplicate search already happened, and how confident is it?
6. Is this merely an issue, or is it already a **regression-test candidate** or fix handoff?

If the design cannot answer those questions, then Rust still lacks the escalation layer it needs.

## Contract shape
Read the existing stack as a contract with five visibly separate layers:

### 1) Observation truth
The contract must preserve what was actually seen before minimization changes it:
- original subject identity
- toolchain/channel/target/workflow tuple
- commands or invocation lane
- symptom family and observed-vs-expected summary
- attached Cargo/debug/build artifacts
- redaction posture

### 2) Minimization-lineage truth
The contract must show how the case changed:
- original subject → minimized subject lineage
- removed dependencies, targets, flags, or environment assumptions
- what remains checked versus what became unchecked
- confidence that the minimized case is faithful
- whether the minimized result is one-file/script/repo-slice/test-case/IR

### 3) Routing and duplicate truth
The contract must keep routing honesty visible:
- likely target owner / consumer
- consulted issues, searches, or prior reports
- duplicate posture and uncertainty
- information still missing
- why the current target is preferred over neighboring layers

### 4) Regression-candidate truth
The contract must say whether the result is ready to become a test artifact:
- likely test family (`ui`, `run-make`, `cargo`, `rustdoc`, crate-local, etc.)
- what is still missing for mergeability
- whether expected output, directives, or fixture shaping remain incomplete
- whether the case already maps to an open issue or fix PR

### 5) Consumer-handoff truth
The contract must tell later consumers what they may honestly import:
- issue authoring can import observation + minimization + routing
- reviewers can import routing uncertainty and duplicate work already done
- fix authors can import regression-candidate posture
- maintainers can import the pack without assuming it already resolves priority or backport policy

## What the MVP should look like in theory
A realistic v0 is not “solve bug reporting for all of Rust”.
It is:
- one schema family for observation, minimization, routing, regression candidacy, and bundle packaging;
- one cargo-script / single-file proof;
- one workspace/repo-slice proof;
- one regression-candidate handoff proof;
- and one honest uncertain-routing proof.

Required artifacts:
- `defect-observation/v0`
- `defect-minimization-report/v0`
- `defect-routing-report/v0`
- `defect-regression-candidate/v0`
- `defect-escalation-pack/v0`

Required rules:
- keep **observation** distinct from **minimization**;
- keep **routing** distinct from **duplicate confidence**;
- keep **issue filing** distinct from **test readiness**;
- keep **local evidence imports** distinct from **upstream conclusions**;
- keep **uncertain owner** and **possible duplicate** as first-class valid states.

## What the MVP should look like in practice
### Pilot 1 — single-file repro lane
Use `cargo script` / ScriptKit style input to prove that a single shareable file plus attached evidence can become a reviewable escalation packet.

### Pilot 2 — workspace-slice repro lane
Use a real workspace case to prove lineage and redaction posture survive minimization.

### Pilot 3 — uncertain-routing lane
Show that the system can honestly end in “Cargo vs rustc uncertain” or “possible duplicate” rather than fabricating confidence.

### Pilot 4 — regression-candidate lane
Take a minimized case and prove the pack can carry enough information for a test author to continue toward a real regression test.

### Pilot 5 — evidence-import lane
Attach Cargo Report and debugger/build artifacts without letting them impersonate the whole escalation story.

## Why this should be promoted instead of just deepening debug tooling
The archive already has strong work on Debuggability, Feedback Loop, Cargo Report, and Harness Protocol.
Those are still right, but the next sharpening move is **not** “more local evidence” on its own.

Why this promotion wins now:
- official signals are strongest on **reproducer sharing, triage state, and regression-test expectations**;
- the archive already has enough local evidence substrate to justify a composition layer;
- promoting the escalation contract reduces the risk that one MCVE, one duplicate guess, one issue template, or one assistant filing flow quietly redefines the whole upstream surface.

So this revision promotes the **observation → routing → regression handoff** seam, not the entire debugging or maintenance stack.

## Ranking impact
This does **not** reorder the archive's top band.
It adds one more explicit frontier beneath the current map:
- Build-State Evidence stays #1 overall.
- Adoption Navigation remains the strongest anti-tacit-knowledge frontier.
- Debuggability stays high.
- Maintenance Reality remains the clearest stewardship/continuity seam.
- Defect Escalation Contract becomes the clearest next **upstream-routing / repro-to-regression-handoff** move.

That means it should sit below the broad build/debug/control-plane band, but above another round of issue-template folklore or assistant-only filing glue.

## What not to build
Do **not** build:
- a universal issue portal;
- a bot that auto-files low-quality issues from local output;
- a silent minimizer that loses the original subject;
- a dashboard that infers routing from labels alone;
- or a fake one-shot “bug pack” that claims observation, minimization, routing, and test readiness are all solved at once.

The winning contribution is thinner and more durable:
**preserve the observed case, preserve minimization lineage, record routing/duplicate posture honestly, and hand off enough structure that the next consumer can continue toward an issue or regression test without rediscovering everything from scratch.**
