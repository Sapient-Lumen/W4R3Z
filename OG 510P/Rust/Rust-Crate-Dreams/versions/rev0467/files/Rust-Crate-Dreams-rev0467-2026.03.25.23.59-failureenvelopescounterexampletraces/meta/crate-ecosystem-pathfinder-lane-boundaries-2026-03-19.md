
# Crate ecosystem pathfinder lane boundaries — 2026-03-19

This note exists to keep **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** from dissolving into neighboring lanes.
The archive now has enough adjacent support/health/trust/interop/upgrade ideas that this proposal needs sharper boundaries.

## What P-0509 is

P-0509 is the lane for **task-oriented crate choice** that emits:

- a compact candidate/role/interop view,
- a ranked decision pack,
- a freezeable starter-set lock,
- explicit starter-set readiness,
- explicit lock-in cost,
- and explicit scope-split truth.

Its center of gravity is **decision support for choosing crates**, not operating them after the choice.

## What P-0509 is not

### Not P-0011 Crate Health
P-0011 is about maintenance/MSRV/governance/sustainment posture.
P-0509 may **import** health evidence, but it should not absorb the health lane.

### Not P-0017 Trust Lens
P-0017 is about trust/risk/security/identity posture.
P-0509 may **import** trust evidence, but it should not become a disguised trust score.

### Not P-0006 stdx-curated or another façade crate
A façade or battery-pack crate is a concrete dependency output.
P-0509 is the lane that decides whether such a thing is appropriate for a task, not the lane that reexports it.

### Not a global blessing mechanism
P-0509 should not become “the official Rust top crate per category” debate.
Its outputs are **scoped**, **portable**, and **reviewable**.
It is allowed to say that teaching and production defaults differ.

### Not upgrade-pack / off-ramp support
P-0515 and adjacent lanes are about exiting, replacing, or sunsetting a choice.
P-0509 is about **making the choice in the first place**, with enough lock-in truth that later exit planning is not a surprise.

### Not a silent auto-replacement engine
P-0509 may record revisit triggers and watch state for frozen starter sets.
But it should not quietly turn imported advisories, docs-surface shifts, or health changes into automatic crate replacement without a human decision.

### Not examples / tests / guidance / diagnosis / observability / lifecycle / resource / persistence support
Those lanes describe what a chosen crate provides once someone is trying to use, support, observe, or operate it.
P-0509 is upstream of them.
It may import their artifacts later, but its core question is still **what should we choose and freeze?**

### Not docs.rs parity or toolchain-support work
Docs.rs target/default-target posture and toolchain facts are inputs.
They are not the pathfinder product itself.
P-0509 imports visible support posture; it does not subsume docs.rs or toolchain conformance lanes.

### Not pure ranking/search UI
Search and ranking can be part of the surface.
But a pathfinder without freeze readiness, lock-in cost, or scope split would collapse back into a weak catalog.

## Positive boundary tests

A proposed feature belongs in **P-0509** if it answers one of these questions:

1. **Which crates should we consider for this task lane?**
2. **Which roles or companion crates are actually required?**
3. **Is the starter answer mature enough to freeze?**
4. **Where does this choice buy lock-in that a future migration will have to pay?**
5. **Should teaching and production defaults intentionally diverge?**
6. **What changed between the old decision pack and the new one?**

If a feature instead answers:

- “how do we troubleshoot this chosen crate?”,
- “how do we test or document it?”,
- “how do we reason about its shutdown/resource/persistence behavior?”,
- “how do we ship it to another ecosystem?”,
- or “how healthy/trustworthy is it in general?”

then it likely belongs to an adjacent lane.

## Design rule

Future passes must keep **starter-set readiness**, **lock-in cost**, **scope split**, and **decision-watch state** separate.
Do not let the archive quietly flatten P-0509 back into:

- popularity ranking,
- health ranking,
- trust ranking,
- or a disguised blessed-crates list.
