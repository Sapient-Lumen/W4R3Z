# TRACEABILITY-SEMANTICS

This note defines the thinnest real semantics the archive can currently justify for `traceability_posture`.

## Question

Now that `traceability_posture` looks boundary-bearing across P3 and P5,
what is the smallest semantics that make it real and reusable without turning it into a large audit taxonomy?

## Current result

The archive currently justifies a **two-axis thin model**:
- `reference_anchor`
- `evidence_posture`

Current `reference_anchor`:
- `utc_named_realization`
- `utc_unqualified`
- `profile_reference`
- `local_private`
- `unknown`

Current `evidence_posture`:
- `claimed`
- `traceable`
- `unknown`

rev0032 strengthens this by showing that `local_private` does not yet need to split.

## Why this reduction works

### 1. Traceability is not identical to accuracy
The source base discusses traceability alongside accuracy, stability, and resolution rather than as a synonym for them.
That means the hook should not swallow all performance semantics.

### 2. Traceability is not identical to timescale semantics
The core already has `timescale`.
A timing claim can be on UTC while still differing in how strongly it is anchored to an authoritative realization or reference chain.
So the hook should not simply duplicate `timescale`.

### 3. Stronger verification is not identical to minimal evidence posture
rev0030 concluded that “verified” is better understood as a stronger overlay or process,
not as part of the thinnest common hook.

### 4. Named anchors are not always needed at hook level
rev0031 concluded that literal names can usually be reduced into categories,
as long as the archive preserves the distinction between named UTC realizations,
generic UTC claims,
profile-specific reference families,
and local/private references.

### 5. Local/private variation is currently adjacent, not structural
rev0032 concludes that current differences inside `local_private` are better captured by regime and holdover semantics than by splitting the anchor family itself.

## What stays outside the hook

### Accuracy / uncertainty
This belongs with:
- `interval`
- `time_error_bound`
- `rate_error_bound`
- profile-local timing quality signals

### Timescale semantics
This belongs with:
- `timescale`
- any future adjacent leap / smear / civil-time handling surfaces

### Control and recovery semantics
This belongs with:
- `regime`
- `holdover_class`
- profile-local path-selection or control logic

### Stronger verification / audit overlays
This belongs with:
- profile-local verification services
- audit and measurement overlays
- stronger receipts or certification surfaces

### Full audit chain / provenance dossier
The archive does not need to turn this hook into a complete provenance ledger.
That would be a different layer.

## Current archive judgment

`traceability_posture` is now best understood as:
- a small but real boundary-bearing hook
- reduced to anchor categories plus a minimal evidence posture
- explicitly adjacent to, but not identical with, accuracy, timescale, control, and stronger verification concerns

## Why this is enough for now

This model appears to survive:
- finance cases that need named UTC-realization distinctions
- synchrophasor cases that need UTC traceability at hook level without always naming a realization
- telecom cases that need profile-specific references
- local/degraded cases without forcing a split of `local_private`

That is enough justification to keep the hook real and small.

## Next useful move

Thread this stabilized hook into the greenfield track and test what it changes there.
