# Update channel lessons from `freebsd-update` (signed metadata, conservative failure)

DeriveBSD’s channel model can learn from FreeBSD base updates:
- signed metadata
- strict integrity checks
- conservative failure modes (“refuse to proceed”)

FreeBSD Update’s design is documented publicly, and FreeBSD tracks issues in advisories and wiki pages.
(See `docs/32-curated-references.md`.)

## What to learn (salient)

### Signed metadata + index
- updates are described by metadata which is verified before applying.
- clients refuse to proceed on mismatch (a good default posture).

### Compatibility assumptions
- FreeBSD Update targets systems installed from official RELEASE builds and assumes limited local divergence.
- DeriveBSD should avoid such assumptions by making “divergence” an explicit part of the Plan.

### “Delta distribution” vs “rebuild closure”
- FreeBSD Update distributes deltas for base.
- DeriveBSD can support:
  - full closure distribution (content-addressed blobs)
  - optional delta/patch layers (future), but only if they are verifiable and reconstructable.

### Advisory integration
When update tooling breaks (or causes incorrect deletions), advisories exist and should feed policy gates.
DeriveBSD should treat “update tooling” as part of the threat surface.

## DeriveBSD translation
- channel metadata is signed
- cache content is digest-verified
- failure modes are conservative
- rollback is first-class (boot environments + generations)

Product-shape note: signed channels remain byte authority across all profiles, but `docs/472-update-delivery-and-release-posture-by-profile.md` now fixes how delivery/finalization differs between fleet, workstation, general-purpose, and factory/regulatory shapes.

See RFC-0059.

Last updated: 2026-03-06r201
