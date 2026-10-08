# Official voter-information browser-history surface checklist

Use this checklist for official voter-information routes that **change the visible answer, selected official item, details pane, or route meaning without a full page load and therefore may use `pushState()`, `replaceState()`, hash routing, or comparable same-document history mutation**.

## Mutation inventory and scope

- [ ] Record which routes mutate session-history entries and which user actions trigger those mutations.
- [ ] Distinguish meaningful answer-state changes from canonicalization, invalid-state repair, presentation-only tweaks, and overlay/subview routing.
- [ ] Re-check routes where a misleading Back/Forward outcome could change a voter’s understanding of location, deadline, eligibility, status, or next step.

## Push/replace truthfulness review

- [ ] Review whether user-meaningful answer or record changes create a recoverable history step when voters would reasonably expect Back to return to the prior state.
- [ ] Review whether canonicalization or repair uses replace-style mutation only when it should not masquerade as a distinct visited answer state.
- [ ] Review whether presentation-only changes avoid spamming the Back stack with cosmetic or transient entries.
- [ ] Review whether the same user action produces consistent history behavior instead of unpredictably mixing push and replace semantics.
- [ ] Review whether the last safe recovery point remains reachable instead of being silently erased.

## Back/Forward, overlays, and repair review

- [ ] Review what Back/Forward does after opening detail panes, drawers, overlays, alternate subviews, or item-specific states that behave like route layers.
- [ ] Review whether repaired invalid/stale route state creates loops, contradictory shells, or dead-end entries in browser history.
- [ ] Review whether meaningful history entries also remain legible through aligned page-title/history-entry naming.
- [ ] Review whether compact/mobile layouts preserve the same history semantics instead of collapsing distinct route layers into accidental traps.

## Evidence posture

- [ ] Preserve a small public digest of reviewed history-mutation classes, expected Back/Forward outcomes, recovery-point policy, and last review time.
- [ ] Do not retain named-user browser-history dumps, raw session replay, or giant client event streams merely to prove that a route once pushed or replaced a state entry.
