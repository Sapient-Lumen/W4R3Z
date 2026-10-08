# SYNC-DIMENSION-SPLIT-TEST

This note runs the same split test on `sync_dimension` that rev0039 ran on `traceability_posture`.

The question is different in tone:
`sync_dimension` may not be a claim-versus-assessment problem in the same way.
It may instead be a **profile-declaration** problem.

## Question

Across the greenfield split between:
- wire claim
- local assessed state

is `sync_dimension` best treated as:
- a source declaration
- a negotiated profile semantic
- a local inference
- or a dual-surface semantic

## Comparison surface

### P4 pressure — explicit profile families
Telecom timing material is unusually clear here.
It does not merely describe a clock that happens to be good at several things.
It distinguishes:
- a **frequency profile**
- a **time/phase profile**

It also treats a PTP profile as a selected set of allowed features and options chosen to meet the requirements of a particular application.
That means `sync_dimension` is not just an after-the-fact observation.
It is part of what the profile says the system is doing.

### P5 pressure — requirement families
Power / smart-grid material points in the same direction, but from the requirement side.
The pressure there is not merely “better clocks.”
It is explicit need for:
- precision time synchronization
- phase synchronization
- frequency synchronization

Again, this reads more like an application/profile requirement family than like a purely local inferred judgment.

## Archive judgment

`sync_dimension` is best treated **primarily as a profile-declared semantic**.

That means:
- it may be carried or echoed by sources on the wire
- it may be recorded in local assessed state
- but its deepest home is usually the profile / negotiated operating mode of the system

## Why it is not mainly a local inference

A local system can often infer clues about what matters:
- a telecom slave may infer that it is using a frequency-oriented path
- a grid monitor may infer that phase alignment matters

But those inferences are weaker than the actual profile semantics.
The dimension is usually specified because it changes:
- acceptable mechanisms
- acceptable topology
- timing metrics
- downstream expectations
- and failure / fallback behavior

Those are not just private observations.
They are part of the synchronization arrangement itself.

## Why it is not source-declaration only

A source may advertise capabilities or operate inside a frequency or time/phase profile.
But the dimension usually exists above any one source.
It is often chosen by:
- the deployment profile
- the application requirement set
- or the end-to-end synchronization architecture

That makes source declaration useful but secondary.

## Smallest honest placement

The current archive answer is:
- `sync_dimension` is **profile-first**
- optionally echoed on the wire when a profile wants explicit signaling
- and optionally copied into local assessed state for downstream consequence mapping

This is different from `traceability_posture`.
`traceability_posture` became dual-surface.
`sync_dimension` currently looks **profile-declared, with optional wire/local reflection**.

## What changes in the archive

The `profile_default` tier now contains two different semantic patterns.

### H1 — `traceability_posture`
- dual-surface
- claim-capable
- assessment-capable

### H2 — `sync_dimension`
- profile-declared first
- optionally source-declared
- optionally locally reflected

This is useful.
It means the tier is real, but not uniform.

## Practical rule

The greenfield track should treat `sync_dimension` as:
- mandatory in profile definition where it matters
- optionally signaled on the wire where omission would confuse interoperating participants
- available in local assessed state when downstream logic needs to know whether the system is operating on time, phase, frequency, or a combination

## What this still does **not** settle

This note still does not decide:
- whether greenfield TimeSync needs an explicit negotiation/request field for `sync_dimension`
- whether profile-fixed declaration is enough for first deployment
- how mixed-dimension bridges should describe themselves
- whether dimension changes mid-flight should be modeled as regime changes or profile transitions

Those remain open.

## Next useful move

Test whether the archive now needs a small negotiation/request surface for `profile_default` hooks.
The tier may now be clear enough that the next question is not classification,
but how participants ask for or discover the extra surfaces without widening the core.
