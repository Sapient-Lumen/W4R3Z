# Critical open questions

This file is intentionally short.
It exists so future revisions do not forget the biggest remaining design seams while chasing feature surface.

## 1) Which I2P router implementation should ship first behind the stable contract?

The archive is clearer that the operator surface should stay runtime-implementation-neutral.
What remains unresolved is which actual I2P helper/router should back v1 first on Linux:

- a Java router bundle behind SAM
- an i2pd-style helper behind SAM or an equivalent stable boundary
- some phased validation strategy that tests both before one becomes the default

This matters for memory footprint, operability, persistence layout, shutdown behavior, and upgrade friction.

## 2) How should transport identities and overlay publication be scoped?

A device may have:

- a durable AnonSync identity
- LAN addresses
- approved clearnet known-host addresses
- a Tor onion identity
- an I2P destination / session identity

The archive still needs to decide how much of that is device-wide, share-scoped, or policy-scoped, and which of those identifiers should ever be published automatically.

## 3) What is the exact safety model for peer-pinned direct paths and direct-speed leases?

The archive now has known-host records and route leases as first-class concepts.
What remains unresolved is the stricter policy detail:

- should time-bounded direct leases also require byte caps by default or only optionally
- when a stale known-host record should warn versus block
- whether some direct exceptions should require a reviewed plan instead of an immediate lease
- how much remembered endpoint state may survive after a narrowing change before the daemon forces a clear

## 4) How strict should metadata fidelity be for first-class Linux support?

The archive now names support tiers, but there is still real policy work left around:

- which xattr namespaces are required
- how much ACL fidelity is mandatory
- what the default symlink / hardlink / special-file contract should be
- when downgrade should warn versus block

## 5) How should overlay scheduling differ from clearnet scheduling?

Tor and I2P are not just slower versions of direct TCP/UDP.
The daemon may need different behavior for:

- chunk sizing
- prefetch windows
- retry cadence
- concurrency limits
- settlement expectations

## 6) When, if ever, should bundled transport payloads update independently of daemon releases?

This archive still chooses a conservative v1 default: bundled transport updates should ordinarily ride AnonSync releases.
What remains unresolved is the later threshold for changing that rule.

## 7) Should bounded introductions ever auto-link, or should all new peers always stop in pending state?

This revision makes introduction policy explicit, but it does not settle the strongest convenience question:

- should any trusted constellation be allowed to auto-link peers at all
- should introduction always stop in a pending queue
- if limited auto-link exists, what scopes and maximum roles are still safe

## 8) What should survive successor replacement by default: contacts, approvals, grants, or almost nothing?

The archive now treats succession as reviewed continuity, but the default carry-forward policy is still unresolved:

- which remembered contacts should normally survive
- whether future-approval grants should freeze by default
- whether known-host direct paths should always require re-verification on the successor
