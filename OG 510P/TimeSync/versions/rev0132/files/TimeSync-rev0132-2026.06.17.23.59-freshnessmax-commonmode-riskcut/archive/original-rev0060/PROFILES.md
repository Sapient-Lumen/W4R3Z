# PROFILES

This note defines the first light profile family for TimeSync.

These are not full specifications.
They are compact containers for requirement-heavy pressure that should not automatically widen the invariant core.

## Common profile template

Each profile should eventually answer:
- purpose
- dominant timing pressure
- likely extension hooks
- dominant control-surface pressures
- degraded-operation stance

## P1 — General computing profile

### Purpose
Routine auth, certificates, logging, and ordinary service coordination.

### Dominant pressure
Broad deployability and sane degraded behavior.

### Likely extension hooks
Usually none.

### Dominant control-surface pressures
- acceptability thresholds that are practical rather than extreme
- clear degradation signaling
- simple source policy

### Degraded stance
Prefer continued safe operation with conservative applicability downgrades.

## P2 — Distributed coordination profile

### Purpose
Datacenter and distributed-system coordination where temporal uncertainty affects ordering, commit, or consistency behavior.

### Dominant pressure
Uncertainty budgets and stronger downstream semantics.

### Likely extension hooks
None yet.
This profile stays close to the invariant core.

### Dominant control-surface pressures
- error / acceptability policy
- downstream applicability policy
- regime transitions that interact with coordination logic

### Degraded stance
Prefer explicit widening of uncertainty and conservative behavior over false precision.

## P3 — Traceable finance profile

### Purpose
Transaction timestamping, traceability, and audit-sensitive sequencing tied to an official reference.

### Dominant pressure
Traceable official time plus dense evidence requirements.

### Likely extension hooks
- `traceability_posture` (often assessment-heavy or service-heavy at this profile's strongest boundary)

### Dominant control-surface pressures
- source policy
- error / acceptability policy
- downstream applicability policy

### Degraded stance
Prefer rapid downgrade when traceability or official-reference confidence is lost.

## P4 — Precision network profile

### Purpose
Telecommunications and other precision network environments that care about continuity, holdover, and tight synchronization transfer.

### Dominant pressure
Continuity plus phase / frequency-sensitive performance.

### Internal structure
P4 should be read through:
- `P4-LANES.md`
- `P4-COHESION.md`

The archive now treats P4 as **one cohesive profile with two lanes**:
- **Lane A — frequency continuity / syntonization**
- **Lane B — phase / time alignment**

### Likely extension hooks
- `traceability_posture` (often claim-bearing at live measurement/status boundaries)
- `sync_dimension`
- `holdover_class`
- `validity_scope`

### Dominant control-surface pressures
- holdover policy
- source policy
- regime transition

### Degraded stance
Prefer controlled degradation with explicit continuity semantics over invisible drift.

## P5 — Critical infrastructure precision profile

### Purpose
Grid and other consequence-sensitive infrastructure where timing failure is a system hazard, not merely an IT inconvenience.

### Dominant pressure
Resilience under failure plus assured timing quality.

### Likely extension hooks
- `traceability_posture`
- `sync_dimension`
- `holdover_class`
- `validity_scope`

### Dominant control-surface pressures
- holdover policy
- regime transition
- downstream applicability policy

### Degraded stance
Prefer safety-preserving fallback and strong visibility into degraded state.

## P6 — Local continuity profile

### Purpose
Disconnected, partition-local, expeditionary, or emergency operation after loss of trusted external inputs.

### Dominant pressure
Continue locally without pretending global certainty.

### Likely extension hooks
- `validity_scope`
- `holdover_class`

### Dominant control-surface pressures
- holdover policy
- regime transition
- downstream applicability policy

### Degraded stance
Prefer honest locality and replayable recovery over hidden reconciliation.

## Why P4 and P5 remain separate

They are technically adjacent, but the archive keeps them separate for now because:
- telecom-style continuity and network topology pressure are not identical to infrastructure consequence pressure
- P4 contains two lanes but still one operational neighborhood
- grid-like systems still appear more phase- and safety-heavy than the strongest telecom counterexamples

## Profile discipline

The archive should keep profiles:
- short
- comparative
- citation-backed
- subordinate to the invariant core
- and connected to the smallest possible hook set

A profile is not a license to dump standards catalogs into the archive.

## rev0053 alias discipline

Profiles may document operator-facing aliases when useful,
but those aliases are not profile-default requirements and not shared request syntax.

A profile-local alias sheet must name its explicit expansion.
The expanded item list, not the alias name, is the accountable machine-facing representation.


## rev0054 request lifetime discipline

Profiles may require default visibility when omission would mislead.
That is profile behavior, not request persistence.

The ordinary shared request list remains exchange-scoped.
A profile or tool may repeat explicit item requests for convenience, but it should not treat a prior request as a remote standing obligation unless an explicit lease/subscription surface has been defined.


## rev0055 request-result discipline

Profiles may define when explicit optional request results are visible,
but the base result shape remains item-level and negative-only.

A profile should not create alias-level or bundle-level result status.
If it needs access-denial or policy-failure reporting, that should be a narrow authenticated profile rule, not a generic TimeSync error vocabulary.


## rev0056 required/default absence discipline

A profile may require/default an item only when absence would mislead the profile's clients, operators, or control logic.

Once it does, omission has teeth:
- the response is not full-profile-satisfying by default
- local assessed state must downgrade hook-dependent consequences
- explicit degraded fallback is allowed, but it must be profile-defined and weaker

Profiles should not declare required/default visibility casually.
Every such declaration creates a profile-conformance obligation, not just a display preference.

## rev0060 profile-reference discipline

Profiles should carry a stable identity discipline without turning into archive bloat.

A profile definition should know:
- its identifier
- its version or revision
- its authority or namespace when not globally obvious
- whether exact-rule retention requires a digest
- whether a signed binding is required for the boundary that consumes the assessment

Most profile notes in this archive do not need full binding records.
They need enough identity to prevent `profile_conformance` from becoming an
unscoped verdict when exported.
