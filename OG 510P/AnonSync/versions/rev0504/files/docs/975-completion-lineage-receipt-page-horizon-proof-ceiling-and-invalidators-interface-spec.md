# Completion lineage receipt page — horizon, proof ceiling, and invalidators

## Purpose

Emit a durable artifact for any important completion or freshness claim so later operators do not have to guess what `complete` meant at the time.

## Receipt header

- subject name
- subject identifier
- claim type: completion / freshness / reduced completion / local-only completion
- issued at
- issuer / approving seat

## Required payload

### Claim sentence

Store the exact strongest safe sentence issued at the time.

### Horizon block

Store:

- intended peer set snapshot
- in-scope peer set snapshot
- excluded peer set snapshot
- policy basis for the horizon

### Proof block

Store:

- detection evidence summary
- hidden internal work summary
- transfer/queue summary
- stale debt summary
- proof timestamp

### Ceiling block

Store both:

- strongest safe sentence
- stronger rejected sentence

### Invalidator block

Examples:

- peer membership changed
- stale peer reappeared
- route/source posture changed
- detection basis changed
- manual rescan required
- local hidden work resumed
- subject policy or substrate changed

## Receipt behaviors

- Receipts are superseded, never silently edited.
- Historical receipts remain readable even if peers later expire from the active UI.
- Any consumer of the receipt must be able to read the horizon and ceiling without opening another page.
- A receipt never downgrades its own wording after the fact; a new receipt supersedes it.

## Example sentence family

- `Complete for all connected peers at issuance time; offline intended peers remained outside horizon.`
- `Fresh for the verified scope as of 11:50; local notification degradation prevented a stronger future-proof claim.`
