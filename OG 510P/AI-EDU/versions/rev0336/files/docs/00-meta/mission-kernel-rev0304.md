# rev0304 mission kernel

The mission remains the same: keep AI-in-education work answerable to real
learning, learner agency, access, teacher capacity, source truth, and public-claim
humility when AI systems become ordinary education infrastructure.

`FT-0181` remains the live center. The cube may prepare local bridges, but it may
not pretend those bridges are owner evidence, source custody, acceptance, public
support, lifecycle movement, or closure.

## Heart of the work

The archive is now mature enough that the risky work is not another governance
surface. The risky work is keeping the next real field move executable and clean:

```text
prepare first-contact packet
→ real human send/adaptation outside the archive
→ minimal post-send clock
→ actual returned owner CSV/context, if it exists
→ bounded intake/review/decision/live-window/readout/recheck rail
```

Everything else is support. If a change does not make that rail easier to run or
harder to fake, it should wait.

## rev0304 correction

`rev0304` turns the rev0303 scratch firebreak into an explicit lane split.

The default `owner-field-next` and `owner-field-work` scratch root is now:

```text
scratch/field/ft0181/
```

Generated field commands now write their local artifacts under that lane. Checker
fixtures now write under:

```text
scratch/checks/
```

The router still ignores `check-*`, `smoke-*`, `test-*`, and `fixture-*` subtrees
and artifacts that provenance-link back to those subtrees. The difference is that
the default field scan no longer starts from the whole `scratch/` tree. It starts
from the field lane.

## Why this matters

The cube's worst local failure mode is wasting a session by looking busy while no
real owner packet exists. A maintainer can run checks, create many synthetic local
artifacts, and then ask the router what to do next. Before rev0303, checker state
could compete with field state. After rev0303, it was filtered. After rev0304, it
is separated by path and by scan default.

This is not a new doctrine layer. It is a working-directory refactor that protects
forward motion.

## Current field rail

Run the safe local rail without an explicit scratch override unless you are
intentionally inspecting a legacy scratch lane:

```bash
make owner-field-work
```

The first clean run prepares the bounded first-contact packet under
`scratch/field/ft0181/owner-request-packets/...`, reruns the router, and stops at
the real human-send boundary. It must not record a send, contact, review,
decision, ticket, live-window state, readout, post-readout action, recheck, context
receipt, custody, acceptance, public claim, lifecycle move, or closure.

## Missing on purpose

The missing thing is still real owner-reviewed material. The archive still lacks a
real accepted SRC2+ packet, real owner-reviewed field readout, owner-held
post-readout action result, accepted context cycle, and closeout. The correct next
external move is not more schema work; it is a real bounded owner route or a real
returned owner packet through the guarded lane.
