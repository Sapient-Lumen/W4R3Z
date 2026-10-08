# 569 — Nuclear emergency preparedness: watchdog pager, exception bridge, and alarm receipt controls

Revision: **rev0362**  
Base: **rev0361**  
Status: operational control; public-context-only; no real-site readiness claim.

## Why this file exists

Rev0361 added live watchdog invariant checks. The next failure mode is not detection; it is **silent detection**. A watchdog can find drift, a packet can trigger a loss cap, or a public-meeting clock can move, and the package can still fail if no one acknowledges the alarm, escalates the exception, or preserves the response trail.

Rev0362 therefore adds a watchdog pager and exception bridge. It turns drift into owner-visible, acknowledged, time-boxed work. The success state is not readiness. The success state is **capture-ready / claim-frozen / alarms routable / acknowledgements required**.

## Hard rule

A watchdog tick, pager notification, acknowledgement, escalation ticket, exception bridge row, shift handoff note, public meeting statement, AAR paragraph, dashboard cell, source ID, duplicate URL, local packet candidate, or complete-looking evidence packet can demand, cap, route, contradict, or reopen evidence. It cannot automatically close local emergency-readiness evidence.

## Watch-pager route

```text
live watchdog tick
  → invariant drift alarm
  → pager routing matrix
  → acknowledgement SLA
  → exception bridge ticket
  → owner / backup / incident commander escalation
  → shift handoff receipt
  → loss-cap and claim-freeze persistence
  → adjudication candidate only
  → CAP/retest/verifier if applicable
  → integrated claim-kernel release gate
```

## Correct successful outcome

The correct result remains **capture-ready and claim-frozen**. Rev0362 proves that alarms can be routed, receipts can be required, silent alarms become P0 blockers, and public claim language remains embargoed. It does not prove Beaver Valley, Pennsylvania, West Virginia, Ohio, any county, any ORO, any controller, any evaluator, any alerting authority, any EOC/EOF/JIC, or any facility is ready, passed, safe, sufficient, certified, demonstrated, released, or closed.

## What changed operationally

Rev0362 adds three things that were still too easy to miss:

1. **Alarm receipt is mandatory.** A drift alarm without owner acknowledgement is a P0 exception, not a yellow note.
2. **Escalation is clocked.** Missing acknowledgement, repeated drift, forbidden public language, first-drop packet arrival, source-clock movement, and loss-cap erosion all route to an exception bridge.
3. **No silent recovery.** A later green watchdog tick does not erase an unacknowledged alarm. The alarm needs acknowledgement, disposition, and a handoff-safe closeout.

## Non-closure defaults

Folders, packets, receipts, operator notes, pager acknowledgements, generated tickets, and local candidate evidence do not close readiness. They can only move a row into: rejected closure attempt, hold/no-upgrade, candidate-for-adjudication-not-closure, accepted reopen signal, or context/no-upgrade.

## Next useful real input

The next real input remains an actual or anonymized exercise evidence packet. When one arrives, rev0362 forces the operator to prove not only that the packet exists, but that any resulting alarms were acknowledged, escalated, and carried through shift handoff without weakening the public claim freeze.
