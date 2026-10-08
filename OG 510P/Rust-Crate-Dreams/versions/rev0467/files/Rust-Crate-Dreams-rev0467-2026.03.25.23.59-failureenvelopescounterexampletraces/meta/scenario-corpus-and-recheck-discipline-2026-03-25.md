# Scenario corpus and recheck discipline — 2026-03-25

This note makes one repo-level rule explicit:

A strong crate plan should not stop at artifacts.
It should also ship a **scenario corpus** that proves what those artifacts mean, when they drift, and when the crate must refuse to overclaim.

## Why this matters now

The current leading archive lanes all sit near moving boundaries:
- registry/advisory posture,
- docs.rs hosted versus local build reality,
- target and toolchain variance,
- mirror and alternate-registry differences,
- debugger / OS / version mismatch,
- and evolving Cargo internals.

These are exactly the places where a crate can sound persuasive while quietly becoming wrong.

So the archive should now treat scenario corpora as part of the product plan, not a late testing detail.

## What a scenario corpus is

A scenario corpus is a named set of reproducible cases that includes:
- the starting basis,
- the imported inputs,
- the trigger or drift event,
- the expected machine-readable outputs,
- the expected summary language,
- and the expected refusal boundary when certainty is not justified.

It is a memory device as much as a testing device.

## Minimum anatomy of one scenario

Each scenario should ideally contain:

- `README.md`
  - what this case is proving
- `inputs/`
  - pinned witness material or pointers
- `expected/`
  - one or more golden outputs
- `drift-trigger.note.md`
  - what future change should reopen the case
- `review-notes.md`
  - where manual review begins

The exact layout may differ by crate.
But those roles should exist.

## Scenario classes every top lane should cover

### A. Happy-path scenarios
The crate produces its normal artifact family with no major ambiguity.

### B. Degraded-but-honest scenarios
The crate still provides useful output but marks missing scope, degraded evidence, or narrower confidence.

### C. Recheck-trigger scenarios
The crate receives a new signal that should reopen an earlier answer without overwriting it.

### D. Refusal scenarios
The crate lacks enough evidence to strengthen the claim and says so cleanly.

## Priority scenario families for the current frontier

### 1. Public-registry versus alternate-registry divergence
Relevant to:
- **P-0496**
- **P-0535**
- **P-0509**

Why:
Public crates.io posture does not automatically settle alternate-registry exposure or mirror parity.

### 2. Hosted docs versus local/package witness mismatch
Relevant to:
- **P-0472**
- **P-0536**

Why:
docs.rs uses nightly, sandboxing, configurable metadata, and default targets that may not match local intent.

### 3. Advisory arrives but replacement is not obvious
Relevant to:
- **P-0535**
- **P-0509**

Why:
The crate should re-open the answer and narrow the support ceiling without pretending that one new advisory automatically chooses the next dependency.

### 4. Public/private boundary widens or narrows
Relevant to:
- **P-0431**
- **P-0535**

Why:
Support, semver, and migration posture can all change when public exposure changes.

### 5. Target support differs from popular assumptions
Relevant to:
- **P-0484**
- **P-0509**

Why:
A crate that “works for me on Linux” does not automatically earn a stronger cross-target support claim.

### 6. Debugger/OS/version variance
Relevant to:
- **P-0486**

Why:
The debugging story is explicitly variable across debuggers, versions, OSes, async support, and visualizers.

### 7. Build-dir or build-script behavior changes under new Cargo rules
Relevant to:
- **P-0537**
- **P-0489**
- support/control-plane lanes that infer build behavior

Why:
Many tools still rely on details Cargo calls internal-only or transitional.

### 8. Restricted-delivery or offline mirror environment
Relevant to:
- **P-0496**
- **P-0536**
- **P-0509**

Why:
A worthy crate should degrade honestly when networked live sources disappear.

### 9. Safety-critical narrowed boundary
Relevant to:
- **P-0484**
- **P-0509**
- **P-0536**

Why:
Higher-criticality environments demand smaller trusted surfaces, stronger evidence, and explicit decomposition.

## Recheck discipline

A scenario corpus should also encode when a rerun is needed.

Each scenario should ideally state:
- what signal reopens it,
- whether that signal is intake-only or posture-changing,
- and what older artifact it inherits.

This helps prevent a common failure mode:
new facts silently replacing old conclusions without a visible transition path.

## Claim-upgrade rule after this pass

A lane should not be upgraded from “promising” to “practical next build” unless the archive can point to:
1. an operating model,
2. a small first artifact family,
3. and a scenario corpus that exercises both success and refusal behavior.

## LLM / human memory consequence

This note is also an amnesia resistor.
Future passes should not rely on high-level summaries alone.
They should look for the named cases that still carry the meaning of the lane.

If a pass cannot say which scenarios justify a stronger claim, it should not strengthen the claim.
