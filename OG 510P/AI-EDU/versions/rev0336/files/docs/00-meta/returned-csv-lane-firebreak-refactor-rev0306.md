# rev0306 returned CSV lane firebreak refactor

## Problem

Returned-owner CSV routing is the first point where external field material can
enter local handling. Before this pass, archive fixtures and smoke markers were
blocked, and the default router scanned only `scratch/field/ft0181`. But a CSV
living under checker scratch could still look plausible to direct returned-reply
helpers or to an intentionally broad scratch scan.

That creates two bad outcomes:

- wasted review time on validator output;
- accidental confidence that a local byproduct is a returned owner input.

## Change

`tools/ft0181_field_guards.py` now exposes a common non-field scratch lane block
for returned CSV inputs. A returned CSV is allowed only when it is external to the
archive or under the live field lane:

```text
scratch/field/ft0181/
```

It is blocked when it is under:

```text
scratch/checks/
scratch/releases/
scratch/<legacy-non-field-lane>/
*/check-*
*/smoke-*
*/test-*
*/fixture-*
```

`tools/decide_ft0181_field_next_action.py` now applies the same exact-lane
firebreak during scratch scans, so `SCRATCH=scratch` debug runs do not promote
checker or release scratch into field state.

## Regression coverage

`tools/check_ft0181_field_next_action.py` now writes a valid-looking checker CSV
and asserts it is blocked before returned-reply work. Checker tests that need
plausible returned CSVs now create those CSVs outside the archive while keeping
all generated local outputs in `scratch/checks`.

## Boundary

This refactor does not accept owner evidence. It only prevents local non-field
scratch from being mistaken for the CSV/source packet that a real owner would
return.
