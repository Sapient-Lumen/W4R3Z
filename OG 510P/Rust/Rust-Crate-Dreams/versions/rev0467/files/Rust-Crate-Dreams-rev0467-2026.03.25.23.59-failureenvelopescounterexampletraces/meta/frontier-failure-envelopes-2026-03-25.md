# Frontier failure envelopes — 2026-03-25

This note keeps the frontier broadly stable **while making disproof and degraded guarantees first-class**.

The archive no longer needs more sector inflation.
It needs sharper answers to:
- what exact scenario breaks a claim,
- which witness disproves it,
- what narrower claim still survives,
- what exact guarantee must be withdrawn,
- and what smallest replay or rerun could clear the failure.

## Main judgment

The strongest missing Rust contributions are still mostly **receiver-facing control-plane kits**.
But many of the leading lanes should now be planned as shipping **failure envelopes / counterexample traces / degraded-claim notes** rather than only assurance cases or review summaries.

## Falsification-leverage board

### 1. P-0472 + P-0484
**Role:** failure-evidence and insufficiency-supplier ring

Why first under this lens:
- docs.rs metadata, build metadata, rustdoc JSON, and downloadable docs archives make hosted-vs-local and basis-vs-claim mismatch visible;
- docs.rs itself documents that local builds can pass while docs.rs still fails, which is exactly the kind of counterexample a worthy crate should preserve rather than compress away;
- target tiers and hosted default-target shifts create honest downgraded-claim conditions;
- and this ring is the right place to define “witness present but disproving” versus “witness present but insufficient”.

What the crate should provide:
- `failure-envelope.json`,
- `counterexample-trace.json`,
- `disproof-summary.md`,
- `degraded-claim.json`,
- and `repair-hint.json`.

### 2. P-0509 + P-0536 + minimal P-0535
**Role:** decision / recommendation front door that imports failure envelopes

Why second:
- another team still needs the counterexample turned into a usable recommendation, downgrade, or refusal;
- the front door is where failure evidence becomes “do not recommend under profile X” instead of a buried raw observation;
- and this is the natural place to explain what smaller claim still survives.

What the crate should provide:
- degraded recommendation packets,
- refusal notes,
- counterexample-linked recommendation traces,
- and one human-facing disproof summary.

### 3. P-0486
**Role:** debugger-matrix falsification borrower

Why third:
- debugging support explicitly varies across debuggers, operating systems, versions, and async scenarios;
- this lane benefits unusually strongly from a named failing tuple and a downgraded claim surface;
- but it should borrow the shared failure vocabulary after the support ring proves it first.

What the crate should provide:
- tuple-scoped failure envelopes,
- failing-tuple traces,
- downgraded debugger-support claims,
- and async-debug repair hints.

### 4. P-0431 + P-0496 + P-0125
**Role:** refutation-carry-forward and route-continuity ring

Why fourth:
- advisories, alternate registries, mirrors, and source-route drift often do not create a totally new claim, but they do falsify inherited assumptions;
- this ring is the natural place to track whether a failure invalidates an old claim entirely or only for one route/profile;
- and it is where a refutation bridge is more useful than mere supersession prose.

What the crate should provide:
- refutation bridges,
- inherited-failure notes,
- route-specific downgrade outcomes,
- and reset-vs-carry-forward decisions.

### 5. P-0537
**Role:** build-cause and replay falsification later

Why fifth:
- build-analysis and build-dir work make causal counterexamples more plausible;
- but the substrate is still moving enough that this lane should consume a shared failure vocabulary rather than define it first.

### 6. P-0538
**Role:** scenario-heavy falsification later

Why sixth:
- highly important,
- but scenario maintenance is expensive and should inherit a proven counterexample grammar rather than invent one first.

## Why the broad frontier still stays stable

This falsification lens still does **not** justify resetting the archive toward giant umbrella frameworks for web, GUI, game, ML, or local-first work.
Those sectors may still have unmet needs, but the sharper cross-domain missing value is usually:
- explicit failing scenarios,
- named disproving witnesses,
- downgraded claims,
- cheap repair hints,
- and clean refutation / supersession bridges.

That is why the archive still prefers control-plane kits above broad sector reinventions.

## Guardrail

Do not strengthen a lane under the falsification lens unless the pass can name:
1. the **failing scenario**,
2. the **decisive disproving witness**,
3. the **smaller surviving claim**,
4. the **withdrawn guarantee**,
5. and the **repair or replay slice**.
