# ADR-0114: Packet-capture stronger export remote-locator continuity boundary

- **Status:** Accepted
- **Date:** 2026-03-09
- **Deciders:** DeriveBSD archive maintainers

## Context

ADR-0113 kept stronger `packet.capture.normalized` export honest about recipient-side durability.
That closed the “same recipient, same bytes, same remote object, same validator, same protection posture” loophole.

One narrower loophole still remained:

- the archive could say the stronger handoff reached the right recipient,
- the proof chain could keep the same normalized digest, remote object id, validator, and protection posture,
- and operators could still be left without one stable, typed, recipient-side locator for finding that same remote object again later.

In practice this pushes support and regulated workflows back toward provider folklore:
“open the ticket and click around until you find the right attachment again.”
That is too soft for DeriveBSD’s operability/forensics UX goals.

## Decision

For stronger `packet.capture.normalized` export, the canonical proof chain is now **remote-locator-continuous** as well as digest-stable, destination-bound, recipient-accepted, remote-object-continuous, remote-validator-continuous, and remote-protection-shaped.

DeriveBSD still reuses the generic transport / transport-acceptance / export substrates.
The only extra rule is that canonical stronger packet export must keep one aligned typed `remote_locator` object across the joined receipts:

- `transport.receipt.result.remote_locator`
- `transport.acceptance.receipt.acceptance.remote_locator`
- `export.receipt.adapter.remote_locator`

The locator stays intentionally generic.
Depending on adapter reality, it can describe:

- a URI hint,
- a ticket attachment path,
- a portal object path,
- a message part,
- another object path,
- or an opaque reviewed locator.

## Consequences

### Positive

- The stronger packet-export lane now gives operators a stable retrieval/discovery handle instead of leaving later evidence lookup to provider-specific clicking.
- A and D gain a clean place to preserve recipient-side discoverability for audits, rebuilds, and incident follow-up.
- B and C remain viable because the field is redacted/non-secret and generic rather than a new provider-specific API contract.

### Trade-offs

- Some adapters will only be able to emit `opaque` locators.
  That is still better than silent folklore, but it makes the archive state the discoverability limit explicitly.
- This still tightens only stronger packet export today; it does not yet generalize all export classes.

## What this does not decide

This ADR does **not** decide:

- a universal recipient-side retrieval API,
- whether the remote object must remain permanently readable,
- or whether future generalized export discoverability deserves its own first-class schema.

It only fixes the stronger packet-capture boundary: if stronger raw-byte export is treated as canonical completed handoff, the proof chain must keep one typed recipient-side locator aligned through transport, recipient acceptance, and final export evidence.
