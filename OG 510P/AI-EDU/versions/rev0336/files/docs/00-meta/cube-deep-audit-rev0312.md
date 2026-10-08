# rev0312 cube deep audit

## What was audited

This pass audited the re-entry and operator-handoff path rather than the doctrine
surface area. The concrete question was: after all of the field-lane, clock,
source-chain, hash-anchor, readout, and public/closure firebreaks, can the next
maintainer still run the wrong command or bypass the router from the official
handoff?

## Finding

Yes. The handoff example carried obsolete `python3 tools/run_lint_suite.py
--mode ...` commands. The current runner is lane-based, so those commands fail
before any substantive field work happens. That is wasteful and risky because it
pushes maintainers back toward explanatory edits instead of the bounded field
rail.

The handoff validator also did not require the most important re-entry shape:
router/report first, no direct downstream action lists. Without that guard, a
future handoff could list dense targets such as returned-reply work, activation,
readout, real-import acceptance, or closeout as allowed actions even though the
router is supposed to choose the source artifact and exact command.

## Refactor made

`tools/check_operator_handoffs.py` now rejects obsolete `--mode` handoff
commands, requires the four current lint lane commands, and requires the field
router/report-first allowed next actions. It also blocks handoff records that
advertise direct downstream owner/import/closeout actions as allowed next moves.

`tools/check_reentry_navigation.py` now rejects obsolete `--mode` commands in
root re-entry docs and requires the three field-router entry commands to remain
visible: `make owner-field-work`, `make owner-field-report`, and `make
owner-field-next CSV=...`.

## Waste corrected

The correction is intentionally small. It does not add a new schema family,
branch family, or evidence class. It removes a command trap and makes future
trap reintroductions fail in lint.

## Still missing

No real owner-reviewed SRC2+ packet exists. No real returned CSV has been
accepted. No owner-held post-readout action result, accepted context cycle,
closeout, or signoff exists. `FT-0181` remains live.
