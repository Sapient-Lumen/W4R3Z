# rev0313 field execution risk burndown

## Burned down this pass

**Validation fixture contamination of the live field lane.** Positive validator
fixtures under `scratch/field/ft0181/validation/...` are now ignored by
`owner-field-next`, `owner-field-work`, and `owner-field-report` scans. A copied or
leftover validation fixture cannot become the selected latest artifact for a live
route.

## Why this was next

The previous revisions hardened returned CSVs, activation source packets,
downstream hash anchors, post-readout lane classes, public/closure boundaries, and
operator handoff commands. The next fragile point was not another policy gate; it
was whether validator-generated field-shaped artifacts could distract the live
operator path.

## Current next action

Run the router/report against the live lane, not against validation lanes:

```bash
make owner-field-report
make owner-field-work
```

If a real owner return arrives, use only:

```bash
make owner-field-next CSV=/path/to/real-owner-return.csv
```

## Still blocked

`FT-0181` remains live. Closure, public claim promotion, service-record authority,
and evidence acceptance remain blocked until a real owner-reviewed `SRC2+` packet
passes the full chain.
