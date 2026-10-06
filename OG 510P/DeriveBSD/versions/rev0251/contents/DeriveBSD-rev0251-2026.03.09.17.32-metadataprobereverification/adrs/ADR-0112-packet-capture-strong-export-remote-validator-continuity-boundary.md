# ADR-0112: Packet-capture stronger export remote-validator continuity boundary

- **Status:** Accepted
- **Date:** 2026-03-09
- **Deciders:** DeriveBSD archive maintainers

## Context

ADR-0111 kept stronger `packet.capture.normalized` export on one stable remote object id.
That closed the “same case, different attachment” loophole.

A narrower loophole still remained:

- the same `remote_id` can still refer to a mutable remote object handle,
- recipient acceptance can confirm the right bytes at one moment,
- and final export evidence can still close over the same object id even if the remote system later distinguishes representations by a stronger validator or revision token.

In other words, the archive could still prove **same recipient + same bytes + same object id** without yet proving **same remote representation/version token**.

## Decision

For stronger `packet.capture.normalized` export, the canonical proof chain is now **remote-validator-continuous** as well as digest-stable, destination-bound, recipient-accepted, and remote-object-continuous.

DeriveBSD still reuses the generic transport / acceptance / export substrates rather than inventing a packet-only transport protocol.
The only extra rule is that canonical stronger packet export must keep one stable remote representation/version validator across the joined receipts:

- `transport.receipt.result.remote_validator`
- `transport.acceptance.receipt.acceptance.remote_validator`
- `export.receipt.adapter.remote_validator`

The validator stays intentionally generic. Depending on adapter reality, it can be:

- a strong or weak HTTP `ETag`,
- an object-store version id,
- an attachment revision token,
- a message id when that is the strongest immutable representation handle the adapter exposes,
- or another opaque remote revision token.

## Consequences

### Positive

- The stronger packet-export lane can now prove not just which remote object id held the artifact, but which remote representation/version token the recipient lane actually accepted.
- Adapters that surface stronger validators (for example ETags or version ids) become more valuable without forcing the archive into one provider’s object model.
- Fleet and appliance/regulatory shapes gain a tighter evidentiary story for later support escalation or audit.

### Trade-offs

- Some adapters expose only a weak or opaque validator. Those adapters remain usable, but the proof chain now has to say so explicitly instead of pretending object identity alone is enough.
- This is still stricter only for stronger packet export today; generic export receipts remain broader.

## What this does not decide

This ADR does **not** decide:

- how every other export class should model remote representation/version continuity,
- whether remote validators must always be immutable forever after acceptance,
- or whether a future generalized transport revision token deserves its own first-class schema.

It only fixes the stronger packet-capture boundary: if the adapter surfaces a remote representation/version validator, canonical stronger export must keep that same validator aligned through transport, recipient acceptance, and final export evidence.
