# ADR 0227: Carry bounded sync ranges over authenticated auxiliary routes

Status: accepted implementation, deterministic gates, and genuine bounded Sandwurm qualification,
2026-08-28.

## Context

ADR 0136 froze `state-sync-ranges-v1`, message types 24/25, their canonical request/result records,
manifest-first planning, FileId transfer binding, reconstruction, final digest verification, and
accepted-HEAD-last ordering. ADR 0168 initially restricted auxiliary workers to whole-object frames.
That was the correct first authority/carrier split, but it forced a privacy-pinned large successor to
refetch a complete immutable object or fail closed even when an exact verified basis differed by only
a bounded region.

ADRs 0225–0226 now provide the missing policy boundary: the stable-device-signed route set binds the
exact worker to `tox/i2p-construction`, and a per-job fail-closed class pin has genuine router-loss
evidence. A second range encoding would add ambiguity without adding security. The existing range
frames already bind the target HEAD, transfer ID, canonical range vector, manifest, basis, and final
artifact digest.

## Decision

- Reuse the frozen range-v1 wire frames unchanged. Auxiliary workers may carry only canonical sync
  object/range request/result frames; they do not gain HEAD, activation, authority, or generic
  application traffic.
- Require `state-sync-ranges-v1` on both paths. The parent derives authority and HEAD state from the
  confirmed primary session, the exact worker reports its own bilateral negotiation, and the
  effective auxiliary context is range-capable only when both are true.
- Validate range frames at the route-worker boundary and again in the publisher/subscriber service.
  Preserve the exact worker incarnation, friend/online epoch, remote route-set generation, stable
  principal, authority snapshot, message ID, FileId, and terminal correlation already required for
  whole objects. Route loss and stale results remain fenced.
- Keep range planning, accepted-basis validation, reconstruction, final digest verification,
  accepted HEAD, and explicit activation in the parent Agent. The worker transports a bounded file;
  it does not decide what bytes are trusted or installed.
- Freeze route/failover policy only while a pull is active. A terminally settled same-epoch pull may
  be retired so a later generation can deliberately select another allowed class/policy. Authority
  changes remain conflicts, and an active pull cannot be retargeted by retry.
- Add `sync-file-range-actual-i2p`. It first pulls and activates deterministic 4 MiB generation 1 over
  native, then publishes a parent-linked generation 2 and begins a distinct
  `fail-closed tox/i2p-construction` pull. Both receipts and the host manifest must prove positive
  range reuse, a smaller positive fetch, exact byte equality, the signed I2P carrier, zero
  reassignment, and explicit generation-2 activation.

The runner and strict verifier classify this as a positive range scenario. Their isolated tests also
retain the corrupt-basis fallback distinction, which must not be mislabeled as successful reuse.

The final clean-suite repetition exposed one preexisting whole-object carrier-loss race adjacent to
the new path: a queued offer could pass cached carrier readiness, lose its worker immediately before
receive admission, and terminally fail before the authoritative offline pass applied the job's
failover policy. Auxiliary effects now revalidate the exact live worker incarnation, and an
`unavailable` receive at the remaining atomic edge locally fences its provisional attempt while the
pull awaits carrier-loss policy. Duplicate stale offers cannot reuse the burned attempt. A direct
subscriber seam test plus 100 consecutive full-Agent fail-closed repetitions accept that ordering.

Accepted compact proof `pair.ej_4507n` runs clean source revision
`38081157378597f61a86444a2f5fd1264348f0ae` in two simultaneous Sandwurm/KVM guests. Both use binary
SHA-256 `8a919501363fe3987806116843088744017e653f3877e7bca989a6e22888a726`.
The exact signed I2P member carries generation 2 with zero reassignment, while one range reuses
4,194,176 verified artifact bytes and fetches 128 bytes. The reconstructed 4,194,304-byte artifact is
verified, accepted through its linked HEAD, and explicitly activated. Both routers and all three
fronts remain on their initial incarnations. Raw and 17,563,648-byte compact forms independently pass
the strict verifier.

## Consequences

The large-successor protocol no longer equates privacy pinning with complete-object retransmission.
The framing freeze holds: no message type, feature bit, canonical encoding, or trust order changed.
The new surface is a strictly smaller carrier permission guarded by two negotiated sessions and the
existing signed route/authority context.

The 128-byte value is artifact-range payload, not total network use. The signed range index/manifest,
Tox/I2P framing, acknowledgements, and cover/background traffic still cross their respective paths.
This result is one positive construction window on one host. It does not qualify interruption/resume
of a live I2P range, byte striping, restart-persistent range staging, performance, anonymity,
independent paths, fleet behavior, or production `tox/i2p`.
