# RFC-0186: Export transparency logs

## Problem

`export.receipt` proves locally that an export occurred, but local receipts can be deleted or modified after compromise.
In regulated environments we often need tamper-evident, append-only history of “what left the system”.

## Proposal

Introduce an optional export transparency lane:

- New artifact: `export.transparency.entry` (`spec/export.transparency.entry.schema.json`)
- Common log proof bundle: `transparency.proof` (`spec/transparency.proof.schema.json`)
- Extend `export.policy` with optional `transparency{...}` requirements:
  - `required`: export completes only when a log entry is committed
  - `metadata_profile`: minimal vs standard logged metadata
- Extend `export.receipt` with optional `transparency_entry_digest`

## Minimum logged metadata

Default profile (`minimal`) logs only:
- artifact digest
- export.receipt digest
- export.policy digest
- optional bundle.plan digest
- log inclusion proof/checkpoint (opaque)

Ticket ids and recipients should be hashed or omitted unless policy permits.

## Why now

Greenfield systems can bake in “sharing transparency” early without breaking backward compatibility.
Retrofitting it later usually collides with privacy and operational workflows.

## Risks / tradeoffs

- Availability: if policy requires logging and the log is down, exports stall (need operator override lanes).
- Privacy: even minimal metadata may be sensitive; policy must allow opting out or hashing.

## Open questions

- Recommended internal log stack (Rekor-like vs SCITT receipts vs bespoke append-only log)
- How to checkpoint/pin log states for offline verification

See also: `docs/254-export-transparency-logs.md`.
