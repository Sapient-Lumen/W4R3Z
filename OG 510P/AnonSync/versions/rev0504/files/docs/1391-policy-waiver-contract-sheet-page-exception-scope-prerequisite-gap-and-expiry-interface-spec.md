# Policy-waiver contract sheet page — exception scope, prerequisite gap, and expiry

## Purpose

This page answers the exception question that profile conformance alone does not finish:

> this subject is not cleanly on profile — what exact exception class explains that, what fields are affected, what must happen before the exception can end, and when must we review it again?

## Core decision

Every serious policy exception must render one first-class **Policy-waiver contract sheet** before the product allows silent exclusion, deferred rollout, or `special case` language.
The page owns:

- waiver identity
- profile reference
- exception class
- affected scope
- removal condition
- expiry / rereview
- strongest safe waiver sentence

## Fixed page order

1. waiver strip
2. profile-reference card
3. exception-class card
4. scope-and-field card
5. removal-condition card
6. conformance consequence card
7. waiver receipt

### 1) Waiver strip

Show:

- canonical waiver id
- linked profile id
- linked profile revision
- focused subject id
- focused world id
- waiver status: `proposed`, `active`, `expired`, `satisfied`, `rejected`, `unknown`
- top question being answered: `why is this subject not cleanly on profile?`

### 2) Profile-reference card

Show the exact profile context:

- profile id
- profile revision
- target cohort or subject
- intended binding class if the waiver did not exist
- currently blocked binding class
- witness confidence

## Hard rule

The page may not issue a waiver against a vague `defaults pack`.
It must anchor to one canonical profile id and revision first.

### 3) Exception-class card

Render exactly one top-line class:

- `unsupported-world`
- `unsupported-surface`
- `ignored-by-runtime`
- `local-parallel-lane`
- `missing-prerequisite`
- `migration-gap`
- `temporary-hold`
- `evidence-gap`
- `hard-out-of-policy`
- `unknown`

For the chosen class show:

- what is proven
- what is not proven
- whether the exception is expected to be temporary
- stronger sentence blocked

## Hard rule

`ignored-by-runtime` may never be collapsed into `unsupported-surface`.
A visible but ineffective control is a different truth from no supported control at all.

### 4) Scope-and-field card

List exactly what the waiver covers:

- affected subjects
- affected worlds
- affected fields
- unaffected fields that still conform
- whether value similarity exists despite the exception
- whether the exception blocks rollout, merely downgrades conformance, or both

## Hard rule

Anything not listed in scope is outside the waiver.
The page must not let one exception blur across neighboring fields or worlds.

### 5) Removal-condition card

Show what must happen before the waiver can end:

- prerequisite to satisfy
- migration step to complete
- surface/world join that must be proven
- evidence still missing
- review owner
- review schedule
- expiry time

If no expiry is set, the page must demand a stronger justification and owner class.

### 6) Conformance consequence card

Show how this waiver changes profile truth:

- `excluded from profile counts`
- `included but downgraded`
- `rollout blocked`
- `rollout proceeds around subject`
- `cannot bind until prerequisite met`
- `unknown until evidence collected`

Also show the exact stronger sentence the product refuses to make.

### 7) Waiver receipt

Emit one compact receipt with:

- waiver id
- profile id
- profile revision
- focused subject id
- exception class
- field count
- expiry / rereview
- removal condition headline
- strongest safe waiver sentence
- blocked stronger sentence

## Copy rules

- Never say `special case` without naming the exception class.
- Never say `temporary` without expiry or rereview.
- Never say `still on profile` if the waiver excludes the subject from conformance counts.
- Never say `unsupported here` when the truer sentence is `visible here but ignored`.
- Never say `just mobile behavior` when the real class is `local-parallel-lane`.

## Example strongest-safe sentence patterns

- `This subject is excluded by an active local-parallel-lane waiver: the profile governs desktop fields, while this mobile share keeps its own supported local route for the affected settings.`
- `This field is visible in Linux WebUI but currently treated as ignored-by-runtime, so profile conformance is blocked for that field until a stronger witness or product change exists.`
- `The subject is under a migration-gap waiver after service-world fork; profile attachment remains blocked until the successor world is explicitly re-bound.`
- `No waiver class has yet been proven; the product currently knows only that conformance evidence is incomplete.`
