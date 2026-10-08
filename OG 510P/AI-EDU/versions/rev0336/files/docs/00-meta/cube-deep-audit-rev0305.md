# rev0305 cube deep audit

## Audit target

This audit looked for the next riskiest unfinished seam after the `rev0304` field
scratch lane split. The target was not a new doctrine layer; it was executable
waste in the live `FT-0181` rail.

## Finding 1: operator-local date drift

The cloudtainer UTC clock can be one date ahead of the operator's America/New_York
session. A clean first-contact run performed during the June 16 New York session
could default to a June 17 field date and a June 24 return date. That is not an
evidence breach, but it can waste a real owner-contact cycle and pollute field
clocks with a date the operator did not intend.

Corrective action:

- added `operator_today_iso()` and `operator_due_date_iso()` in
  `tools/ft0181_field_guards.py`;
- wired all live FT-0181 default clocks through that helper;
- added a validator assertion that `CUBE_AS_OF_DATE=2026-06-16` yields a default
  first-contact return date of `2026-06-23`;
- verified `make owner-field-work` emits `SENT_DATE=2026-06-16` and
  `RESPONSE_DUE_DATE=2026-06-23` under the same operator-local override;
- added `operator_local_date` to prepared packet manifests so route-block checks
  do not reject a same-session June 16 operator event merely because the UTC
  `created_at_utc` timestamp has crossed into June 17.

## Finding 2: lane split needed a low-cost inspection tool

After `rev0304`, the default lane was correct, but future maintainers still lacked
a quick way to inspect field-lane state without reading all scratch artifacts by
hand. That made accidental reversion to `SCRATCH=scratch` more likely.

Corrective action:

- added `tools/report_ft0181_field_lane.py`;
- added `make owner-field-report`;
- the report writes only under allowed scratch/external paths;
- it quotes the router's one next action, counts known field artifacts, flags
  legacy top-level scratch residue, and warns about executed/recorded field dates
  after the operator-local date;
- it explicitly labels itself `LOCAL_SCRATCH_HYGIENE_NOT_EVIDENCE`.

## Finding 3: context-pack re-entry could over-demand current doctrine copies

The context pack pointed directly at a revision-matched field-lane refactor note.
If a later revision changed only tooling, that exact note might not exist and the
pack could pressure maintainers to create a needless meta copy.

Corrective action:

- `tools/gen_context_pack.py` now falls back to the latest existing field-lane
  refactor note when no current-revision note exists.

## Waste avoided

This revision did not add a new schema, new branch family, new open question, new
public-claim row, or new evidence gate. The only new operator surface is a scratch
hygiene report because it reduces field execution risk and points back to the
existing router.

## Residual risk

The archive still cannot complete `FT-0181`. It can only prepare and guard the
local rail. The riskiest unfinished event remains a real owner contact and real
owner-returned `SRC2+` packet.
