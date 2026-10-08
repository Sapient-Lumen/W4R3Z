# Top-lane assurance-case plans — 2026-03-25

This note turns the assurance doctrine into concrete build planning for the current leading lanes.

## 1. P-0509 + P-0536 + minimal P-0535
**Role:** decision-assurance front door

### Receiver
- maintainer choosing among crates
- release or security reviewer
- team lead needing a frozen recommendation basis
- higher-assurance adopter who needs explicit non-claims

### First honest `0.1`
- intake one reviewed bundle family
- emit one bounded recommendation claim
- attach decisive witnesses
- attach one warrant vocabulary
- expose open challenges and non-claims
- link to one prior case when re-run

### Package shape
- `pathfinder-assurance-core`
- `pathfinder-assurance-schemas`
- `cargo-pathfinder-assure`
- bounded import adapters only for already-reviewed bundle families

### Artifact family
- `claim-catalog.json`
- `assurance-case.json`
- `witness-bundle.json`
- `challenge-register.json`
- `assurance-summary.md`
- `non-claims.md`
- `inheritance-bridge.json`

### Refusal boundary
Do not imply:
- runtime qualification,
- organization-specific approval,
- or stronger support than imported witness scope justifies.

## 2. P-0472 + P-0484
**Role:** witness-supplier ring

### Receiver
- tool builders who need machine-usable basis facts
- reviewers who need decisive witness excerpts
- front-door decision crates that need auditable imports

### First honest `0.1`
- ingest docs.rs metadata, build metadata, rustdoc JSON, download archives, and target facts
- emit witness bundles with freshness and scope
- emit “witness present but insufficient for claim” when higher-level support is missing

### Package shape
- `support-witness-core`
- `support-witness-schemas`
- `cargo-support-witness`
- adapters for docs.rs and target facts only

### Artifact family
- `witness-bundle.json`
- `basis-trace.json`
- `scope-annotation.json`
- `freshness-note.json`
- `insufficient-witness.outcome.json`

### Refusal boundary
Do not pretend raw docs/build/API facts already equal a recommendation, support tier, or adoption verdict.

## 3. P-0431 + P-0496 + P-0125
**Role:** inheritance and supersession ring

### Receiver
- teams revisiting old approvals
- offline / mirrored / alternate-registry users
- supply-chain and lifecycle reviewers

### First honest `0.1`
- intake prior assurance case
- classify inheritance outcome
- link route, advisory, boundary, or inventory changes
- emit explicit supersession or reset outcomes

### Package shape
- `continuity-bridge-core`
- `continuity-bridge-schemas`
- `cargo-continuity-bridge`
- bounded adapters for route and advisory inputs

### Artifact family
- `inheritance-bridge.json`
- `supersession-link.json`
- `route-parity-challenge.json`
- `claim-reset.outcome.json`

### Refusal boundary
Do not silently carry forward prior trust across advisory, route, or mirror changes without an explicit bridge object.

## 4. P-0486
**Role:** debugger-matrix assurance borrower

### Receiver
- teams needing to know whether debugging support claims apply to a specific tuple
- maintainers triaging debugger regressions
- reviewers who need explicit async-debug non-claims

### First honest `0.1`
- emit tuple-scoped claims
- attach decisive witnesses for those tuples
- attach async-debug challenge notes
- refuse broad debugger support claims outside tested tuples

### Artifact family
- `tuple-claim-catalog.json`
- `tuple-witness-bundle.json`
- `tuple-challenge-register.json`
- `tuple-assurance-summary.md`

## Cross-lane rule

The front door should define the first compact human-facing assurance case.
The support ring should define the first reusable witness bundle.
The continuity ring should define the first inheritance bridge.
Debugger and later lanes should borrow those semantics unless they can prove a better bounded variant.

## What not to do next

Do **not** spend the next pass on:
- more broad sector scanning,
- a giant generic “trust platform” supercrate,
- or a fully general proof assistant posture.

The tighter next move is to make one leading lane ship a **claim graph another reviewer can actually inspect**.
