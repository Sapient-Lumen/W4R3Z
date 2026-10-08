# Surface handoff page — proof exists here versus inspectable here, and better-host route

## Purpose

When the current seat or surface cannot honestly inspect a witness, this page prevents bluffing and turns the limitation into a typed handoff.

## Typical triggers

- Web surface can point to hidden `.sync/Archive` but cannot inspect it directly
- iOS cannot access Archive
- current seat has placeholders or announcements but another seat has the witness bytes
- app is gone but filesystem residue remains
- service-state exists, but only a lower-level surface can inspect it safely

## Questions this page must answer

1. What is proved to exist?
2. Why is the current surface insufficient?
3. What is the best next seat or tool?
4. What can still be claimed before that handoff?
5. What stronger claims remain forbidden?

## Layout

### A. Current limitation banner
Example statements:

- `Archive witness exists, but this surface cannot inspect it directly.`
- `This iOS surface cannot access Archive witnesses.`
- `Residual share bytes remain on disk, but the app surface that owned them is gone.`

### B. Best-next-route cards
Each card includes:

- next surface or seat
- why it is better
- what will become inspectable there
- what risk or cost the route carries
- whether the route is read-only inspection or an action path

### C. Claim-before-handoff panel
Three stacked sentences:

- **proved now**
- **not yet proved**
- **what the handoff is expected to prove, if successful**

### D. Handoff package
Bundle forwardable context:

- subject identifier
- witness class
- current access class
- residual risks
- no-surprises note for the next operator / next seat

## Actions

- `Open on desktop`
- `Continue in file browser`
- `Route to witness-bearing host`
- `Export handoff bundle`
- `Stay here and keep only narrow claim`

## Guardrails

- Never let the UI imply that the handoff already succeeded.
- Never let `best next route` look like `only route` if several seats are viable.
- Never erase the current-surface limitation after a route is suggested.
- Never let the product say `restore available` when only `inspect on another host` is proved.

## Result

A typed, auditable bridge from current-surface limits to the next best inspection surface, without overstating what the current surface can already prove.
