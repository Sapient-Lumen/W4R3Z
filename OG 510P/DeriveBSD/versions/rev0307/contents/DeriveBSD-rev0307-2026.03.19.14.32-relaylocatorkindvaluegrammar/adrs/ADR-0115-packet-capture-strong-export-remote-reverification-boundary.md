# ADR-0115: Packet-capture stronger export remote reverification boundary

- **Status:** Accepted
- **Date:** 2026-03-09
- **Deciders:** DeriveBSD archive maintainers

## Context

ADR-0114 kept stronger `packet.capture.normalized` export discoverable after handoff by preserving one typed recipient-side locator.
That closed the “same bytes, same recipient, same remote object, same validator, same protection posture, same locator” loophole.

One narrower ambiguity still remained:

- the archive could preserve the right locator,
- later operators could find the same remote object again,
- but the follow-up proof could still collapse back to screenshots, clicking around a portal, or re-downloading the packet bytes just to learn whether the accepted object still matches the recorded evidence.

That is too loose for DeriveBSD’s operability and regulatory story.
We need one typed way to say “we re-checked the same accepted remote packet evidence using metadata only.”

## Decision

For stronger `packet.capture.normalized` export, DeriveBSD now defines a typed **remote reverification** lane.

DeriveBSD reuses a generic receipt shape:

- `transport.reverification.receipt`

and a packet-capture specialization:

- `packet.capture.export.transport.reverification.receipt.profile`

This is **follow-on evidence**, not a new export completion requirement.
The stronger handoff still completes at recipient acceptance.
But whenever later support, audit, or regulatory work wants to claim that the same accepted remote packet object still stands as evidence, the canonical follow-up object is now a metadata-first reverification receipt rather than portal folklore.

For canonical stronger packet reverification:

- `reverification.body_downloaded = false`
- the reverification receipt joins the same `export.receipt` and `transport.acceptance.receipt`
- and the same remote validator / protection posture / locator stay aligned again

The reverification method stays intentionally generic.
Depending on adapter reality, it can be:

- `http-head`
- `object-head`
- `ticket-metadata-api`
- `message-metadata-api`
- `portal-manifest`
- `manual-reviewed`
- `custom`

## Consequences

### Positive

- Later packet-evidence checks no longer have to mean “download the stronger raw bytes again and hope the UI still lines up.”
- A and D get a typed, audit-friendly way to re-check remote evidence continuity without inventing a provider-specific evidence store.
- B and C stay viable because adapters that only surface coarse metadata can still emit an honest reverification receipt with generic method names.

### Trade-offs

- Some adapters will only be able to prove validator/locator/protection continuity, not a fresh remote digest.
  That is still better than screenshots and clicking, but it keeps the proof limit explicit.
- This remains packet-export-specific today.
  It does not yet generalize all remote evidence classes.

## What this does not decide

This ADR does **not** decide:

- a universal remote retrieval API,
- whether every adapter must support periodic reverification,
- or whether non-packet export classes should adopt the same receipt immediately.

It only fixes the stronger packet-capture boundary: if later work wants to treat the accepted remote copy as still-current evidence, the archive now expects a typed metadata-only reverification receipt instead of hand-audited portal behavior.
