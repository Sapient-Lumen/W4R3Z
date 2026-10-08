# VALIDITY-SCOPE-TEST

This note tests whether `validity_scope` should join the archive's `profile_default` tier.

## Question

Does the archive now have repeated evidence that locality / partition / recovery semantics need a reusable default-visible hook across multiple demanding boundaries,
or is `validity_scope` still mainly a strong branch-specific extension?

## Comparison

### P4 — Precision network / telecom timing

Telecom timing certainly cares about:
- bad references
- backup-path selection
- holdover entry
- and return to acceptable synchronization

But the source pressure still lands mainly on:
- quality/status signaling
- regime change
- control-plane selection behavior

That is not yet the same thing as a reusable default-visible `validity_scope` hook.

### P5 — Critical infrastructure precision timing

Critical-infrastructure timing strongly distinguishes:
- absolute versus relative timing needs
- full versus partial timing solutions
- and degraded local operation when trusted references are disturbed

Even so, the pressure still does not repeat in the same shape as the `profile_default` members.
It more often says:
- understand the application requirement
- understand the available source type
- manage degraded operation honestly

That is important,
but it is still not the same as repeated evidence for one reusable boundary hook that must be default-visible.

### P6 — Local continuity / survival

This is the strongest case for `validity_scope`.
Here the distinction between:
- globally grounded
- local-only
- partition-local
- and recovery-local

is obviously meaningful and often decisive.

But this pressure is still concentrated in one branch of the archive.
That is not yet enough to admit the hook into `profile_default`.

## Current judgment

`validity_scope` remains outside `profile_default`.

It survives as a useful extension hook,
especially for P6 and related degraded-operation work,
but it does not yet show the repeated cross-profile default-visible pattern needed for the tier.

## Consequence for the tier

The `profile_default` tier now looks more stable.
Current members remain:
- `traceability_posture`
- `sync_dimension`

Still outside:
- `holdover_class`
- `validity_scope`

## Why this is a good result

The archive now has a stronger reason to keep the new tier small.
Both borderline candidates failed by the same standard:
- important, yes
- useful, yes
- but not yet repeatedly default-visible across multiple demanding boundaries

That makes the tier feel earned rather than permissive.

## Next useful move

Return to the greenfield track and sketch the thinnest response/state layout that carries:
- the minimal core
- plus `profile_default` hooks where a demanding profile needs them

without widening the archive-wide core.
