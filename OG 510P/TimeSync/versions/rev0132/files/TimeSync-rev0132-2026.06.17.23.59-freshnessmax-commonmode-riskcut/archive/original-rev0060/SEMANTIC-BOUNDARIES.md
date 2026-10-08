# SEMANTIC-BOUNDARIES

This note records the current semantic separation inside the TimeSync narrow waist.

The archive was at risk of treating several different questions as if they were one.
This note keeps them separate.

## 1. `regime`

### Question answered
How is the system operating right now?

### Examples
- normal
- degraded
- holdover
- recovery

### Not the same as
- where the claim is valid
- what uses should rely on it
- which sources support it

## 2. `applicability`

### Question answered
What classes of downstream use should trust this state?

### Examples
- acceptable for routine auth/logging
- not acceptable for high-integrity sequencing
- only acceptable for local continuity

### Not the same as
- the system's operating mode
- the geographic or locality scope of the claim
- the type of source footing behind it

## 3. `source_posture`

### Question answered
What kind of source / trust footing supports the state?

### Examples
- authenticated multi-source
- mixed source set
- local holdover only

### Not the same as
- how the system is operating
- what downstream uses remain acceptable
- where the claim should be treated as valid

## 4. `validity_scope`

### Question answered
Where, and under what recovery-locality envelope, should this claim be treated as valid?

### Examples
- globally grounded
- local but serviceable
- partition-local
- recovering / rejoining

### Why it survives
A system can be in the same regime, with similar applicability, but differ materially in whether its timing claim is globally grounded or only locally valid while recovering.

## Compact examples

### Example A
- regime: holdover
- applicability: local continuity only
- source_posture: local oscillator only
- validity_scope: partition-local

### Example B
- regime: recovery
- applicability: restricted
- source_posture: PTP-assisted recovery
- validity_scope: recovering toward global grounding

### Example C
- regime: normal
- applicability: routine network and auth uses
- source_posture: authenticated multi-source
- validity_scope: globally grounded

## Archive judgment

rev0011 keeps `validity_scope` because collapsing it into `regime` or `applicability` would erase a distinction the recovery and fail-safe material keeps surfacing.
