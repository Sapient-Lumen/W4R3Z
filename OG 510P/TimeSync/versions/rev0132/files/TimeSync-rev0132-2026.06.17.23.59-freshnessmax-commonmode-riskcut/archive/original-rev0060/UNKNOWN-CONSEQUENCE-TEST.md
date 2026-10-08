# UNKNOWN-CONSEQUENCE-TEST

This note tests whether `unknown` needs one tiny downstream consequence rule for `applicability`.

The archive wants to keep this smaller than a policy lattice.
It also wants to avoid a misleading outcome where a hook becomes `unknown` but a stronger downstream applicability label survives unchanged as if nothing happened.

## Question

When a `profile_default` hook becomes `unknown`,
does the archive need one small default consequence for `applicability`?

## Source pattern

The source base keeps repeating one family of pressure.

- Integrity in PNT is not only about correctness; it also includes timely warning when data should not be used.
- Smart-grid timing guidance treats known uncertainty as something an application needs in order to decide whether its required accuracy is still met.
- Telecom timing uses explicit failure / unusable conditions to prevent a degraded source from continuing to drive a stronger downstream decision path as if it were still healthy.
- PMU / synchrophasor timing quality likewise ties usability to known time-error ranges rather than to silent optimism.

That pattern does **not** force one universal downgrade table.
It does force a small anti-false-confidence rule.

## Smallest rule that survives the pressure

The current best rule is:

> If a current `applicability` claim depends on a hook that is now `unknown`, that stronger `applicability` claim may no longer be asserted unless a profile-defined fallback explicitly permits it.

This can be read more compactly as:
- `unknown` must never widen `applicability`
- and `unknown` must not preserve a stronger **hook-dependent** applicability claim by default

## Why this is smaller than a policy lattice

This rule does **not** say:
- every `unknown` means unusable
- every profile must downgrade to the same destination tier
- every client must apply the same consequence mapping

It only says:
- do not keep asserting a stronger applicability judgment when one of its load-bearing semantics is no longer known

The exact fallback tier remains profile-local.

## Traceability case

If `traceability_posture` becomes `unknown` at a boundary,
a profile may still preserve some weaker applicability outcome.
But it should not keep asserting a stronger traceability-dependent applicability outcome unless the profile already defines a safe fallback.

This matches the archive's earlier distinction between:
- traceable/claimed/unknown posture
- and downstream consequence labels that depend on that posture

## Sync-dimension case

If `sync_dimension` becomes `unknown`,
a downstream system may still retain some coarse time-use applicability.
But it should not continue to assert a stronger phase-sensitive or frequency-sensitive applicability label that depended on the now-unknown dimension.

Again,
the point is not universal demotion to zero.
The point is withdrawal of the unjustified stronger claim.

## Why the archive needs this

Without this rule,
`unknown` is too easy to treat as a purely descriptive state that leaves consequence untouched.
That would conflict with the source pattern:
- warnings that data should not be used
- usability tied to known uncertainty or quality
- and failure semantics that intentionally trigger selection, holdover, or degraded operation

## Current archive judgment

Yes.
`unknown` needs one tiny downstream consequence rule.

The rule should remain this small:
- block stronger hook-dependent applicability claims by default
- leave the exact fallback tier profile-local

## What this still does **not** settle

This note still does not decide:
- whether all reasons for `unknown` belong on the wire
- whether the same tiny rule is enough for both direct-source and relay-generated unknowns
- whether some profiles will want a stronger local default than this minimal rule

## Next useful move

Test where the optional reason layer should live.
The next question is whether the small reason vocabulary belongs:
- on the wire
- in boundary metadata
- or only in local assessed state
