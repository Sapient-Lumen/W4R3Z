# rev0313 field validation fixture firebreak refactor

## Problem

The previous source-chain fixes correctly moved positive validator fixtures into
`scratch/field/ft0181/validation/...` so they stopped looking like checker or
release scratch. That solved one laundering problem but left a practical
cloudtainer seam: after a validation run, those field-shaped fixtures could still
be visible to `owner-field-work`, `owner-field-next`, or `owner-field-report` when
the selected scratch root was the live field lane.

That would not create SRC2+ evidence, but it could waste the next operator turn by
routing from a validator artifact rather than the real live field state.

## Change

`tools/decide_ft0181_field_next_action.py` now treats field-lane validation
fixture paths as non-routable during live field scans. It ignores:

- `scratch/field/ft0181/validation/...`
- field-lane path parts with `validation-...`
- field-lane path parts ending in `-validation`
- artifacts outside those lanes whose provenance references point back into them

`tools/report_ft0181_field_lane.py` uses the same router ignore rule and reports a
count/sample of ignored validation fixture artifacts instead of including them in
live field-lane counts.

## Regression

`tools/check_ft0181_field_next_action.py` now builds a valid-looking contact clock
and prepared packet under field-lane validation fixture paths, then proves that:

- the router still emits `PREPARE-FIRST-CONTACT-PACKET` for an otherwise empty
  live lane;
- observed artifact counts stay zero;
- no latest artifact candidate is selected;
- the field-lane report scan excludes the fixture artifacts and counts them as
  ignored validation fixtures.

## Effect

Validators can keep using field-shaped source chains for positive tests, but
those chains do not become live operator state. The next executable step remains
based on real field artifacts only.

## Non-effect

This is not owner contact, not owner evidence, not SRC2+, not custody evidence,
not service-record authority, not public-summary support, and not `FT-0181`
closure.
