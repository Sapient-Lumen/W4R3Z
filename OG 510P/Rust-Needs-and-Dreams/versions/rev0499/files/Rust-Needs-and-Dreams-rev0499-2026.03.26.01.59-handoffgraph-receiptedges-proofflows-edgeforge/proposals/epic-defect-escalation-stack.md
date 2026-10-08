# Proposal: Epic Defect Escalation Stack

## Thesis
Rust should have a thin, reviewable escalation layer that turns:
- local observation,
- minimal reproducers,
- routing / duplicate posture,
- and regression-test candidacy

into portable artifacts instead of issue-template folklore.

This is an ecosystem contribution because it would help:
- end users who can reproduce a confusing failure but do not know what to file;
- maintainers who need better issue input without losing the original case;
- compiler/Cargo/docs/tooling teams that already operate explicit triage workflows;
- and assistants/IDEs/CI systems that increasingly mediate how users ask for help.

## MVP
Ship:
- `defect-observation/v0`
- `defect-minimization-report/v0`
- `defect-routing-report/v0`
- `defect-regression-candidate/v0`
- `defect-escalation-pack/v0`

Plus four proofs:
1. single-file `cargo script` / ScriptKit-style repro proof
2. workspace-slice proof
3. uncertain-routing / possible-duplicate proof
4. regression-candidate handoff proof

## Success criteria
A reviewer should be able to answer quickly:
1. What failed locally?
2. What minimized subject still reproduces?
3. What changed during minimization?
4. Who is the likely target and how certain is that?
5. What prior-art search already happened?
6. Is this ready to become a regression test or still just an issue candidate?

## What not to build
Do not build:
- a universal issue portal,
- auto-filing bots as the primary deliverable,
- a silent minimizer,
- or a dashboard-first product that guesses routing from labels.

The winning contribution is smaller:
**a durable escalation contract that preserves truth across observation, minimization, routing, and regression handoff.**
