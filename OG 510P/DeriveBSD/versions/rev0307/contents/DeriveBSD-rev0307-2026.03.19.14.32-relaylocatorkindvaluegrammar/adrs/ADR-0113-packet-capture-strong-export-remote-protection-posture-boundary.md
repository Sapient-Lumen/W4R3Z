# ADR-0113: Packet-capture stronger export remote-protection posture boundary

- **Status:** Accepted
- **Date:** 2026-03-09
- **Deciders:** DeriveBSD archive maintainers

## Context

ADR-0112 kept stronger `packet.capture.normalized` export on one stable remote representation/version validator.
That closed the “same bytes, same remote object id, same revision token” loophole.

A narrower loophole still remained:

- a recipient can accept the right bytes,
- the proof chain can keep the same remote object id and validator,
- and the archive can still say almost nothing about whether the remote side protected that accepted representation against later overwrite or routine deletion.

In other words, the archive could still prove **same recipient + same bytes + same remote object + same remote validator** without yet proving whether the remote side treated that object as durable evidence or as a merely transient upload.

## Decision

For stronger `packet.capture.normalized` export, the canonical proof chain is now **remote-protection-shaped** as well as digest-stable, destination-bound, recipient-accepted, remote-object-continuous, and remote-validator-continuous.

DeriveBSD still reuses the generic transport acceptance / export substrates rather than inventing a packet-only evidence store.
The only extra rule is that canonical stronger packet export must carry one aligned `remote_protection` object across the joined receipts:

- `transport.acceptance.receipt.acceptance.remote_protection`
- `export.receipt.adapter.remote_protection`

The posture stays intentionally generic. Depending on adapter reality, it can describe:

- versioned noncurrent retention,
- a retain-until window,
- policy-locked retention,
- legal hold,
- append-only logging,
- or an opaque reviewed non-overwrite posture.

## Consequences

### Positive

- The stronger packet-export lane can now say whether the remote copy counts as durable evidence rather than merely delivered bytes.
- A and D gain a clean place to express WORM- or hold-shaped recipient posture without a vendor-specific transport fork.
- B and C remain viable because the field stays generic and still permits versioned or opaque reviewed posture when that is the strongest thing the adapter can honestly say.

### Trade-offs

- Some compatibility adapters will only be able to report a weak posture such as `opaque-reviewed`.
  Those adapters remain usable, but the archive now has to say so explicitly instead of pretending recipient acceptance alone implies durable evidence.
- This still tightens only stronger packet export today; it does not yet generalize all export classes.

## What this does not decide

This ADR does **not** decide:

- the exact transport/backend API used to request remote retention or legal holds,
- which product profiles require which remote-protection modes by default,
- or whether a future generalized export durability lane deserves its own first-class schema.

It only fixes the stronger packet-capture boundary: if stronger raw-byte export is treated as canonical completed handoff, the recipient-side proof chain must say what overwrite/delete-resistance posture the remote side claims and keep that posture aligned through final export evidence.
