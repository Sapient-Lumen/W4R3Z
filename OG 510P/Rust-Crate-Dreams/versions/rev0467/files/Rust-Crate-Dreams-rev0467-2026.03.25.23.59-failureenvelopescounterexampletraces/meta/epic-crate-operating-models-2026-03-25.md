# Epic crate operating models — 2026-03-25

This note extends the archive’s worthiness, adoption-contract, and continuity-contract lenses.

A crate can have a sharp thesis, useful artifacts, and even good citations, yet still fail a deeper practical test.
A truly worthy crate should also have an explicit **operating model**.

## Definition

An **operating model** is the compact plan for how a crate is actually used in theory and practice:
- by whom,
- on what trigger,
- with what imported inputs,
- producing which artifacts,
- under what review cadence,
- with which scenario corpus,
- and under what claim ceiling.

The operating model is where “interesting concept” becomes “real contribution other people can adopt”.

## What should a worthy crate provide other people?

A worthy crate should provide another team with all of the following:

1. **A repeated answer**
   - not just a one-off analysis;
   - a question that recurs in real teams and deserves a stable workflow.

2. **A small, portable artifact family**
   - machine-readable outputs for automation;
   - short human-readable summaries for review and handoff.

3. **Imported substrate instead of invented truth**
   - lean on official registry/docs/tooling surfaces where possible;
   - add value by joining them into a usable contract.

4. **A recheck story**
   - how the answer gets reopened;
   - what signals are intake-only versus posture-changing;
   - and how older answers stay legible.

5. **A scenario corpus**
   - happy path;
   - degraded path;
   - ambiguous path;
   - refusal path.

6. **A bounded support promise**
   - what the crate can honestly say now;
   - and what it refuses to say without stronger imports or more manual review.

7. **A handoff surface**
   - something a teammate can read later without recreating the entire reasoning chain.

8. **An exit route**
   - keep, pin, except, migrate, replace, or stop using.

## The theory / practice split

### In theory
A worthy crate provides durable leverage over a repeated ecosystem problem.

### In practice
A worthy crate usually looks like:
- one CLI or library surface,
- a small set of JSON artifacts,
- a markdown summary,
- imported official evidence,
- a handful of named scenarios,
- and a visible refusal boundary.

If a proposal cannot name those things, it is still too abstract.

## The operating-model questions every top lane should answer

1. **Who is the primary receiver?**
   Engineer, reviewer, release manager, CI, compliance lead, maintainer?

2. **What repeated workflow is being shortened?**
   Choice, freeze, parity check, recheck, support audit, transition, or something else?

3. **What are the imported sources of truth?**
   crates.io, docs.rs, `cargo metadata`, toolchain facts, repository witnesses, policy files?

4. **What is the smallest first release?**
   Which one CLI/API surface and which three to six artifacts make the crate useful?

5. **Who runs it and when?**
   Interactive use, CI, nightly, release-time, quarterly review, incident response?

6. **What exact triggers reopen the question?**
   new release, advisory, target change, mirror change, docs mismatch, manual review request?

7. **Which scenarios prove the claim ceiling?**
   Not just “works for us”, but named cases with expected outputs.

8. **What does success certify — and what does it not certify?**
   This is the difference between honest support and vague confidence theater.

9. **What is preserved from prior runs?**
   Basis lock, prior comparison, carried-forward note, old summary, old ticket?

10. **What is the clean off-ramp?**
    Can the user pin, defer, migrate, replace, or safely stop using the crate?

## A practical scorecard for epic worthiness

A proposal becomes stronger when it can score well on these dimensions:

- **receiver breadth via one seam**
  - it helps many domains because the seam is shared, not because the crate is vague.

- **artifact clarity**
  - outputs are obvious and bounded.

- **official-substrate leverage**
  - it stands on existing public ecosystem surfaces.

- **operating-loop clarity**
  - it says who runs it, when, and why.

- **scenario depth**
  - it proves support ceilings rather than only advertising capabilities.

- **memory durability**
  - another person can inspect the result later.

- **exit honesty**
  - the crate makes replacement or downgrade legible.

## Anti-patterns

A proposal is weaker when it mainly says:
- “Rust needs a whole new umbrella framework”;
- “we should have a smarter assistant for X”;
- “this should integrate everything”;
- “the crate will just know the right answer”;
- or “support” without naming targets, versions, scenarios, or review boundaries.

Those may sound ambitious.
They are rarely good first contributions.

## Immediate consequence for the archive

The archive should now prefer ideas that can pass this test:

**Could another team adopt this crate with one operator, one runner, one corpus, and one bounded support promise in `0.1`?**

If not, the proposal probably needs more narrowing before it should rise.
