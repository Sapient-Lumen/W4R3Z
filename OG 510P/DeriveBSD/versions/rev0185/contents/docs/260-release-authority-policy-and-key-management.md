# Release authority policy and key management

DeriveBSD already has:
- `trust.policy` (what a client trusts)
- `release.capsule` (what a release *is*)
- optional transparency entries (`release.transparency.entry`)

What’s missing is a **first-class object that defines who is allowed to publish releases, under what thresholds, with what emergency controls**.

This document introduces `release.authority.policy` and binds publication to explicit receipts.

## Lessons to steal (TUF-shaped)

TUF’s core operational lesson is role separation + thresholds:
- The **root role** indicates which keys are trusted for which roles, and signature thresholds can require multiple signatures.
- Root keys are intended to be handled with higher security (often offline).
- Recovery from key compromise involves revocation and re-issuing trust metadata; if a threshold of root keys is compromised, the system may require **out-of-band** root updates.

DeriveBSD should *not* require full TUF everywhere, but should bake in the **same key-management ergonomics**.

## DeriveBSD object model

### `release.authority.policy`

Defines:
- release scope (namespace/channel patterns)
- signing roles and thresholds for:
  - publish
  - halt
  - resume
  - key rotation
- required evidence attachments:
  - transparency entry required/optional
  - witness cosignature quorum (optional)
- emergency controls:
  - kill switch for a channel (policy-bound)
  - “publish allowed only if monitors are clean” (optional)

### `release.publish.receipt`

A typed receipt emitted by the publisher that binds:
- `release.capsule_digest`
- `release.authority.policy_digest`
- optional `release.transparency.entry_digest`
- optional `rollout.policy_digest`

Clients (or fleet controllers) can require a publish receipt in addition to capsule signatures.

### `release.halt.event`

A typed event used for emergency halts that can be:
- referenced by rollout halt conditions
- attached to incident bundles
- audited as a signed decision

## Why this is groundfloor-worthy

- Prevents “release authority” from turning into undocumented CI scripts.
- Makes emergency actions (halt/resume) mechanically explainable.
- Makes multi-party publishing (threshold) a first-class capability instead of a social process.

## Relationship to existing lanes

- `release.capsule` gains optional bindings:
  - `release_authority_policy_digest`
  - `release_publish_receipt_digest`

- Rollout decisions (`rollout.policy`/`rollout.receipt`) can pin a required authority policy digest.

- Transparency monitors (`docs/259-…`) validate that logged publication events match the authority policy.

## Related docs

- `docs/61-channel-metadata-tuf-inspired.md`
- `docs/203-full-tuf-metadata-adapter.md` (interop)
- `docs/257-release-capsules-and-transparency.md`
- `docs/259-transparency-monitors-and-witness-gossip.md`
