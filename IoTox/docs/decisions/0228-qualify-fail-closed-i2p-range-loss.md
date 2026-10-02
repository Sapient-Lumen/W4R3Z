# ADR 0228: Qualify fail-closed I2P range loss

Status: accepted implementation, strict verifier, and genuine bounded Sandwurm qualification,
2026-08-29.

## Context

ADR 0227 proves that the frozen `state-sync-ranges-v1` records can carry a changed artifact region
over an authenticated `tox/i2p-construction` auxiliary. It deliberately leaves interruption open.
ADR 0226 proves router loss and explicit fresh recovery for a small whole object, but does not show
that a live range bundle is classified, cleaned, fenced, and reconstructed correctly.

The first range-loss attempt exposed an observability error in the gate and a real cleanup bug. A
pull reports range intent before its prerequisite manifest has arrived. Treating intent as a live
range caused manifest loss to take the bundle-cleanup path. Aggregate transfer progress also let the
host mistake manifest bytes for artifact-range bytes. Neither result could qualify range loss.

## Decision

- A range job is considered to have a live bundle only when it owns a concrete range lane. Local
  `sync-status` now reports `range-lane-active`, the range attempt ID, and exact bundle bytes. A
  manifest receive without that lane remains a whole-object prerequisite and is retired by the
  whole-object coordinator on carrier loss.
- The actual-I2P fault gate requires the exact signed I2P carrier, a nonzero worker incarnation, a
  concrete range lane, a positive provider position of at least 65,536 bytes, and a position strictly
  below the exact bundle size before stopping the client router.
- Loss must retire the carrier receive before cleanup, remove the range staging file and open staging
  descriptor, count exactly one carrier loss and one blocked fail-closed job, make zero reassignment,
  and leave the old job awaiting explicit operator action.
- Recovery preserves the i2pd datadir and adapter listener, replaces only the router process, and
  requires SAM generation two, one auxiliary recovery, the same signed carrier key, and zero IoTox
  worker restarts. The old job is explicitly cancelled. A distinct fresh job may then select the same
  `fail-closed tox/i2p-construction` policy.
- The fresh job must verify and commit its manifest, fetch a complete new range bundle, reconstruct
  and digest-check the artifact from the accepted basis, accept the linked HEAD last, and activate
  only through the explicit token. Bytes from the failed range are not retained or reused.
- `iotox routes` now appends a local, content-free line for every auxiliary worker: constructed
  network class, transport state, application readiness, both binding directions, online epoch,
  range negotiation, sync frame counters, and last failure. This changes no peer framing. The lab
  retains bounded recovery and repull heartbeats so a rejected run identifies the exact layer.
- The strict verifier treats this scenario as a router replacement and bounds the pre-fault position
  against the scenario's fetched range bytes. Its self-test covers both the new restart classification
  and refusal of a position at or beyond the range boundary.

Accepted proof `pair.a9zwongf` runs clean source revision
`9af199fb227acd16a101f7686b2c644244354c9c` in two simultaneous Sandwurm/KVM guests. Both use IoTox
binary SHA-256 `a64e17d381e9ee7bf24c9596d163169afafcde4c6b79d77eea48369f646a885e`.
The first bundle reached 86,373 of 1,048,576 bytes when the host stopped only the client router.
IoTox removed all staging state, counted one loss and one blocked job, and reassigned nothing. The
router returned under a distinct PID over the same datadir and the exact worker requalified once
without restart. After explicit cancellation, a distinct job fetched the full 1,048,576-byte range
over the same member, reused 3,145,728 verified basis bytes, reconstructed the 4,194,304-byte target,
accepted generation 2, and explicitly activated it. Raw and 26,558,464-byte compact forms both pass
the independent verifier.

## Consequences

IoTox now has bounded evidence for the complete fail-closed lifecycle of a live privacy-pinned range:
positive bytes, router loss, exact cleanup, no downgrade, authenticated route recovery, explicit
old-job retirement, fresh same-carrier range transfer, full digest convergence, and activation.

This is not byte resume. The 86,373 failed bytes are deliberately discarded and the fresh job
downloads the complete 1 MiB bundle. It does not authorize implicit revival, same-attempt continuation,
restart-persistent range staging, byte striping, production `tox/i2p`, anonymity, independent paths,
availability, or a throughput SLA. Repeated and very-late loss, larger object distributions, and
cross-process range-prefix resume remain separate gates.
