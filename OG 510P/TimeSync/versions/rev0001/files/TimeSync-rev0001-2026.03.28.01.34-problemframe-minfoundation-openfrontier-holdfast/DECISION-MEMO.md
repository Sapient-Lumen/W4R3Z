# DECISION MEMO

This file records only the smallest set of up-front decisions that currently look justified.

## Decision 1 — Do not define TimeSync as a new protocol yet
**Status:** adopted for rev0001

Reason:
the existing problem already spans NTP, NTS, PTP, GNSS/PNT, public timing services, and application-level uncertainty APIs.
Declaring "new protocol" this early would force a shape before the scope is understood.

## Decision 2 — Treat uncertainty as first-class
**Status:** adopted for rev0001

Reason:
research and practice both point to bounded uncertainty as load-bearing.
A scalar timestamp alone hides too much.

## Decision 3 — Separate authenticity from trustworthiness
**Status:** adopted for rev0001

Reason:
a source can be authenticated and still yield a poor or attackable time estimate because of delay asymmetry, stale trust anchors, topology issues, or regime mismatch.

## Decision 4 — Keep the project's identity open
**Status:** adopted for rev0001

Candidate identities remain open:
- protocol,
- narrow-waist time-state spec,
- risk/governance profile,
- orchestration architecture,
- or combination.

## Decision 5 — Start with foundation artifacts, not deep architecture
**Status:** adopted for rev0001

Reason:
the problem shape is still being discovered.
A small foundation is more honest and more durable than a large premature design.

## Non-decisions deliberately preserved

These remain intentionally unresolved:
- exact definition of "global"
- whether scope includes civil/legal time semantics or only sync/dissemination
- whether TimeSync targets public infrastructure, private systems, or both
- whether "time state" should be standardized at wire level, API level, operational level, or all three
- whether TimeSync needs a reference implementation early
