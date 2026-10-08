# TRACEABILITY-SPLIT-TEST

This note tests the first live frontier question from rev0038:
should `traceability_posture` be treated primarily as:
- a source claim
- a local assessment
- or a dual-surface semantic

The archive now has enough profile pressure to answer this one more sharply than before.

## Question

What is the smallest honest placement for `traceability_posture` across the greenfield split between:
- wire claim
- local assessed state

## Comparison surface

### P5 pressure — live measurement boundary
P5-like power / synchrophasor cases push traceability outward, toward the source-facing boundary.

The source pattern is unusually explicit:
- the source is expected to provide time traceable to UTC
- the source should indicate leap-second changes
- the time status / quality is expected to indicate traceability and accuracy at the measurement boundary

That is not merely an audit-side reconstruction.
It is part of the live boundary contract.

### P3 pressure — service / audit boundary
P3-like finance cases push traceability inward, toward assessed and documented state.

The source pattern is different here:
- clocks must stay synchronized to NIST time within stated tolerances
- firms must document procedures, keep logs, and certify compliance
- services such as TMAS continuously compare the local standard to UTC(NIST) and expose uncertainty relative to the national standard

This still involves real upstream sources and real reference anchors.
But the strongest reusable traceability semantics appear at the service, monitoring, and audit boundary,
not necessarily in every runtime timestamp object.

## Archive judgment

`traceability_posture` is best treated as a **dual-surface semantic**.

But the two surfaces do not carry equal weight in every profile.

### In P5-like cases
`traceability_posture` is often a **claim-bearing boundary semantic**.
The upstream source or time-status path is expected to carry it live.

### In P3-like cases
`traceability_posture` is often a **locally assessed or service-assessed semantic**.
The strongest evidence comes from continuous comparison, documented uncertainty, calibration, procedure, and certification.

## Why the archive should not force a single placement

### Not source-claim only
If the archive made `traceability_posture` source-claim only,
it would fit P5 reasonably well,
but it would understate how much of P3 traceability is actually established by:
- monitoring systems
- procedural evidence
- local uncertainty accounting
- and audit-facing controls

### Not local-assessment only
If the archive made `traceability_posture` purely local,
it would fit P3 better,
but it would hide the fact that some demanding P5 boundaries already expect traceability to be surfaced in the live time-status path itself.

### Therefore: dual-surface
The archive's smallest honest answer is:
- allow an upstream `traceability_posture_claim` where the profile carries it live
- allow a local assessed `traceability_posture` where the profile derives or confirms it from stronger local evidence

## Practical rule

The greenfield track should treat `traceability_posture` as:
- **claim-capable** on the wire
- **assessment-capable** in local state
- and **non-upgradeable by default** across aggregation without new evidence

This builds directly on the earlier non-upgrade rule from `GREENFIELD-TRACEABILITY.md`.

## What changes in the archive

rev0038 left open whether `traceability_posture` belonged on one side of the split or both.
rev0039 closes that question provisionally.

Current archive judgment:
- `traceability_posture` is the first clear **dual-surface** member of the `profile_default` tier
- P5 shows why the claim surface matters
- P3 shows why the assessed surface matters

## What this still does **not** settle

This note still does not decide:
- whether wire-level absence should mean `unknown`, `not-carried`, or `profile-forbidden`
- how relays should preserve versus restate a traceability claim
- how strongly `traceability_posture` should bind downstream applicability in each profile

Those remain open.

## Next useful move

Run the same split test on `sync_dimension`.
That hook may turn out to be:
- source-declared
- negotiated
- inferred locally
- or dual-surface in a different pattern than traceability.
