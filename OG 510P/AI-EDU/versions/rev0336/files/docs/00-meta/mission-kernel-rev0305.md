# rev0305 mission kernel

`rev0305` keeps the mission narrow: move `FT-0181` toward real owner-reviewed
pilot evidence without letting local controls become evidence, proof, contact,
custody, public-claim support, lifecycle movement, or closure.

## Heart of the work

The archive exists to protect an education-AI pilot rail from two opposite
failures:

1. **False confidence:** a local packet, lint, report, registry row, or scratch
   artifact gets mistaken for an owner-reviewed `SRC2+` evidence packet.
2. **Stall by governance:** the maintainer adds another control surface instead
   of doing the smallest safe field action that could bring back real owner
   evidence.

The live answer is still executable, not rhetorical: run the bounded field router,
prepare only the local bridge it emits, stop at human/owner gates, and accept
nothing as evidence until a real owner-returned packet passes the existing intake,
custody, review, decision, live-window, readout, post-readout, context, and
closeout controls.

## rev0305 correction

`rev0304` split live field scratch from checker scratch. `rev0305` corrects the
next highest-risk seam: **operator-local field clocks**.

The cloudtainer can roll to the next UTC date while the operator session is still
on the prior America/New_York date. Before this revision, default field clocks
could drift by one day when no explicit `AS_OF_DATE`, sent date, status date, or
block date was supplied. That could waste a real outreach cycle, create confusing
response due dates, or misalign post-send/recheck clocks.

`rev0305` adds one shared helper in `tools/ft0181_field_guards.py`:

- `CUBE_AS_OF_DATE` overrides the operator-local date for reproducible sessions.
- `FT0181_AS_OF_DATE` remains a legacy override.
- `CUBE_OPERATOR_TIMEZONE` selects the local operator timezone.
- the default timezone is `America/New_York`.

The field router, packet prep, post-send recording, status/route-block recording,
returned CSV staging, post-readout action/recheck briefs, and route-block checker
now share that helper instead of calling container-local `date.today()`.

## What remains missing

No real owner was contacted by this archive. No real CSV is present. No owner
answers have been reviewed. No accepted `SRC2+` packet exists. No activation,
live-window card, terminal readout, post-readout dispatch, recheck, context
receipt, public claim, service-record update, or closeout exists.

The next substantive step remains outside the archive: a human must adapt/send the
bounded owner request or record a real route block. The archive can prepare the
local packet and post-send clock command, but it must not pretend either event
happened.
