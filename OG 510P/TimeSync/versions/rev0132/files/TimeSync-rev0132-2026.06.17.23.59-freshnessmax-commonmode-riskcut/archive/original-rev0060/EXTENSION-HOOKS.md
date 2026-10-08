# EXTENSION-HOOKS

This note defines the current tiny extension hooks for TimeSync.

A hook is smaller than a profile field set and much smaller than a subsystem.
It is just enough extra structure to let demanding profiles say something the invariant core cannot say cleanly by itself.

## Hook design rule

A hook should be:
- small
- reusable across more than one demanding profile when possible
- interpretable without a standards catalog
- and removable if later experience proves it unnecessary

## Current hook set

### H1 — `traceability_posture`

#### Why it survives
rev0027 made this hook boundary-bearing across P3 and P5.
rev0029 showed it survives a P4 pass.
rev0030 reduced the evidence axis.
rev0031 reduces the anchor axis.

#### What it means
A compact statement about:
- what kind of recognized reference a timing claim is tied to
- the minimum evidence posture for that tie

#### Thin current model
`reference_anchor`:
- `utc_named_realization`
- `utc_unqualified`
- `profile_reference`
- `local_private`
- `unknown`

`evidence_posture`:
- `claimed`
- `traceable`
- `unknown`

#### Current pressure judgment
This remains the first clearly cross-profile boundary-bearing hook outside the core narrow waist.
Its current strength comes partly from repeated reduction.
rev0034 adds one distinction: it still does not belong in the archive-wide minimal core,
but it now looks profile-default at some P4/P5 boundaries rather than merely optional everywhere.
rev0039 adds another: this hook is now best treated as a **dual-surface semantic**.
- In some P5-like cases it is carried as part of the live upstream claim/status path.
- In some P3-like cases it is more honestly established in local or service-assessed state.

### H2 — `sync_dimension`

#### Why it survives
This remains a strong surviving hook.
Smart-grid, telecom, and CPS material explicitly distinguish time, phase, and frequency synchronization rather than treating them as one thing.

#### What it means
A compact declaration of whether the profile is operating mainly on:
- time
- phase
- frequency
- or a combination

#### Current pressure judgment
Some P4 subcases are frequency-first,
while other P4 and many P5 cases remain phase/time-heavy.
That is one more reason not to collapse the hook prematurely.
rev0035 adds one judgment: this hook now looks like the second member of the archive's
`profile_default` middle tier, because omission at some P4/P5 boundaries would hide what dimension of synchronization is actually being promised.
rev0040 adds another: this hook is now best treated **primarily as a profile-declared semantic**.
- A profile or operating mode usually declares whether the system is doing time, phase, frequency, or a combination.
- The same dimension may be echoed on the wire or reflected in local state, but those are secondary placements.

### H3 — `holdover_class`

#### Why it survives
Precision-network, critical-infrastructure, and local-continuity profiles all need a little more structure around holdover than the core can justify.

#### What it means
A profile-defined class describing the expected holdover posture or envelope.

#### Current pressure judgment
rev0036 keeps this hook outside `profile_default`.
The sources repeatedly justify default-visible holdover state, degraded regime, and timing quality,
but not yet a richer reusable holdover class across multiple demanding boundaries.

### H4 — `validity_scope`

#### Why it survives
The semantic-boundary pass suggests that the archive still needs one compact way to say where a timing claim is valid and whether it is carrying recovery-locality semantics.

#### What it means
A profile-defined label describing whether the timing claim is:
- globally grounded
- local but still serviceable
- partition-local
- or in recovery / rejoin semantics

#### Current pressure judgment
rev0037 keeps this hook outside `profile_default`.
It remains strongest in P6-like local continuity work,
but the archive still lacks repeated cross-profile evidence that it must be default-visible across multiple demanding boundaries.

## Current archive judgment

The strongest current hook set is:
- `traceability_posture`
- `sync_dimension`
- `holdover_class`
- `validity_scope`

The archive now also has a tiny middle tier:

### `profile_default` hooks
Current members:
- `traceability_posture`
- `sync_dimension`

Not yet admitted:
- `holdover_class`
- `validity_scope`

The current hook hierarchy now looks roughly like:
1. `traceability_posture` — strongest cross-profile boundary-bearing hook
2. `sync_dimension` — strongest surviving structural pressure hook and second `profile_default` member
3. `holdover_class`
4. `validity_scope`
