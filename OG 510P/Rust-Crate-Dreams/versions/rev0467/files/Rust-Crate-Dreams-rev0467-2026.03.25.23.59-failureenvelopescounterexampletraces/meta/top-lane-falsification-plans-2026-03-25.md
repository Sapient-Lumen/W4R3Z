# Top-lane falsification plans — 2026-03-25

This note turns the falsification doctrine into concrete build planning for the current leading lanes.

## 1. P-0472 + P-0484
**Role:** failure-evidence supplier ring

### Receiver
- tool builders who need machine-usable negative evidence
- reviewers who need one decisive disproving witness
- decision crates that need auditable downgraded claims

### First honest `0.1`
- ingest docs.rs metadata, build metadata, rustdoc JSON, download archives, and target facts
- capture one hosted-vs-local or scope-vs-claim counterexample family
- emit degraded claims instead of a binary pass/fail
- emit one repair-hint note with the smallest honest replay slice

### Package shape
- `failure-witness-core`
- `failure-witness-schemas`
- `cargo-failure-witness`
- adapters for docs.rs and target facts only

### Artifact family
- `failure-envelope.json`
- `counterexample-trace.json`
- `disproof-summary.md`
- `degraded-claim.json`
- `repair-hint.json`

### Refusal boundary
Do not pretend one hosted or target-specific failure automatically disproves all runtime, recommendation, or domain claims.

## 2. P-0509 + P-0536 + minimal P-0535
**Role:** decision front door that imports failures honestly

### Receiver
- maintainer choosing among crates
- release or security reviewer
- team lead needing an explicit “why not” basis
- higher-assurance adopter who needs surviving-claim boundaries

### First honest `0.1`
- intake one reviewed failure-envelope family
- emit one downgraded recommendation or refusal
- attach one decisive counterexample trace
- attach one surviving smaller claim
- link the failure to one prior recommendation case

### Package shape
- `pathfinder-failure-core`
- `pathfinder-failure-schemas`
- `cargo-pathfinder-falsify`
- bounded import adapters only for already-reviewed bundle families

### Artifact family
- `failure-envelope.json`
- `counterexample-trace.json`
- `disproof-summary.md`
- `degraded-recommendation.json`
- `withdrawn-guarantee.md`
- `refutation-bridge.json`

### Refusal boundary
Do not imply that a failure in one profile or tuple bans the crate universally unless the counterexample actually supports that broader refusal.

## 3. P-0486
**Role:** debugger-matrix falsification borrower

### Receiver
- teams needing to know whether debugger support claims fail for a specific tuple
- maintainers triaging debugger regressions
- reviewers who need explicit async-debug downgrades

### First honest `0.1`
- emit tuple-scoped failure envelopes
- attach decisive failing-tuple traces
- emit downgraded debugger-support claims
- refuse broad debugger support claims outside tested tuples

### Artifact family
- `tuple-failure-envelope.json`
- `failing-tuple-trace.json`
- `tuple-disproof-summary.md`
- `tuple-degraded-claim.json`

## 4. P-0431 + P-0496 + P-0125
**Role:** refutation-carry-forward ring

### Receiver
- teams revisiting old approvals after advisory, mirror, or route changes
- offline / mirrored / alternate-registry users
- supply-chain and lifecycle reviewers

### First honest `0.1`
- intake prior assurance or review case
- classify failure inheritance outcome
- link advisory, route, or inventory changes to explicit downgrades
- emit reset-vs-carry-forward decisions

### Artifact family
- `refutation-bridge.json`
- `inherited-failure-note.json`
- `route-downgrade.outcome.json`
- `reset-vs-carry-forward.json`

### Refusal boundary
Do not silently carry forward prior trust across advisory, route, or mirror changes when a counterexample or route mismatch now exists.

## Cross-lane rule

The support ring should define the first reusable failure envelope.
The front door should define the first compact human-facing disproof summary.
The debugger lane should define the first tuple-scoped borrowed variant.
The continuity ring should define the first refutation bridge.

## What not to do next

Do **not** spend the next pass on:
- more broad sector scanning,
- a giant generic “breakage platform” supercrate,
- or one mega-schema that merges evidence, policy, and falsification.

The tighter next move is to make one leading lane ship a **counterexample another reviewer can actually inspect and act on**.
