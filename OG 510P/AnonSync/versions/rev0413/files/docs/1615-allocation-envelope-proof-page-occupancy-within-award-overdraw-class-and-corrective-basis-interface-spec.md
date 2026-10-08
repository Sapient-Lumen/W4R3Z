# Allocation envelope proof page — occupancy within award, overdraw class, and corrective basis

## Purpose

This page is the durable proof object for the strongest true sentence about whether an active winner is still honoring its award envelope.
It exists so the archive can say exactly whether the winner stayed inside bounds, grazed the edge, overran ordinary room, breached protected reserve, or was corrected back into conformance.

## Sentences this page may support

- `winner active within awarded room`
- `winner active at envelope edge under explicit watch`
- `winner active using temporary emergency borrow`
- `winner active but overdrawn beyond ordinary award`
- `winner active and breaching protected reserve`
- `winner narrowed or throttled back into conformance`
- `winner lost room because envelope breach required reclaim or reopened contention`

## Mandatory proof blocks

### A. Award and limit basis

- winning-claim reference
- awarded room amount
- exception/borrow amount if any
- protected-reserve floor
- impacted claimant set

### B. Consumption evidence

- latest observed consumption witness
- latest in-envelope witness
- latest overdraw witness
- measurement confidence basis
- reserve-impact witness
- neighbor-impact witness if any

### C. Corrective basis

- correction route chosen
- throttle or narrow witness
- reclaim or reopen witness if used
- exception-expiry witness if relevant
- restoring-conformance witness if achieved

### D. Stronger blocked sentences

- strongest blocked sentence for the winner
- strongest blocked sentence for losers or neighbors
- exact fact needed to upgrade either sentence

## Required badges

- `within-envelope`
- `edge-use`
- `temporary-borrow`
- `ordinary-overdraw`
- `reserve-breach`
- `corrected`
- `reclaimed`
- `reopened`

Badges must stack rather than overwrite lineage when later truth strengthens or weakens.

## Proof obligations

- prove envelope conformance separately from activation and heartbeat
- prove reserve breach separately from ordinary overdraw
- prove correction separately from mere continued activity
- preserve impacted-claimant consequence until conformance is restored or room is reallocated
- preserve exception basis whenever protected reserve was borrowed intentionally

## Stronger-sentence guard

This page may say `winner is active`.
It may not say `winner is honoring the award` unless the current proof supports within-envelope or valid temporary-borrow-within-exception truth.
