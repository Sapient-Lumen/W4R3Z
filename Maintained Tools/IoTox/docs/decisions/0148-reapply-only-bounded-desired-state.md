# ADR 0148: Reapply only one bounded desired state

Date: 2026-08-24

Status: accepted

## Context

M6 needs a real remote mutation before IoTox can reason honestly about physical effects. The first
slice must exercise authority, durable admission, provider mutation, savedata, readback, crash
recovery, and terminal evidence without pretending that a Tox presence value is actuation. A generic
mutable-command framework would be unsafe: distinct effects have distinct idempotency, expiry,
cancellation, compensation, and power-cut contracts.

The hardest local ambiguity occurs after an incoming record is durably `STARTED`: the provider may
have applied the effect even though IoTox died before it persisted savedata or committed a result.
Reporting expiry or transferring that unfinished work to a different principal or ownership epoch
would erase material uncertainty.

## Decision

- Register operation 3 as `profile.status.set` with exactly one `ICQ1` byte-6 value: 0 available,
  1 away, or 2 busy. Byte 7 remains zero. Advertise it as operation bit 2 only on the durable command
  feature; the legacy non-durable path rejects every mutation.
- Require the existing narrow `write.settings` capability. Friendship, `read.telemetry`, and
  `actuate` do not authorize this operation.
- Reject every nonzero expiry at local admission and remote envelope validation. The command cannot
  become expired after its effect may already have occurred.
- Commit received, admitted, and started lifecycle truth before calling the provider. Perform the
  real c-toxcore presence mutation on its owner thread, persist provider savedata, read the value
  back, and only then commit a successful result. Surface atomic savedata failure instead of merely
  emitting a diagnostic; effect, persistence, or readback uncertainty leaves lifecycle `STARTED`
  with no terminal result.
- Freeze the successful `IPS1` body as desired value, provider-observed value, and reserved zero.
  Success is canonical only when desired equals observed.
- After a crash in the `STARTED` window, permit reapplication of only the exact frozen desired value.
  Resume only when the currently authenticated stable principal equals the committed principal,
  the ownership epoch equals the committed epoch, and a fresh exact-head authority proof still
  grants `write.settings`. A revocation, principal substitution, or ownership transition holds the
  unfinished record without another effect.
- Replay an exact terminal duplicate from durable evidence without touching the provider. A
  same-identifier/different-payload request remains a conflict.
- Retain the existing local cancellation boundary: an outgoing command may be cancelled only before
  its first committed send attempt. There is no remote post-admission cancellation or compensation.
- Qualify the operation with deterministic codec/engine/store tests, a separate-process provider
  failpoint that stops after effect but before savedata/result commit, and genuine two-IoTox
  Sandwurm convergence over direct UDP and forced TCP.

## Consequences

IoTox now has one complete low-consequence identity-to-provider desired-state path. A repeated
application can only converge on the same three-valued presentation state, and successful evidence
binds the provider readback rather than merely the requested value. Crash uncertainty remains
visible and bounded instead of being mislabeled as expiry or silently inherited across ownership.

This decision does not authorize a generic setting, arbitrary argument, physical output, target
controller, or safety-critical effect. Presence can be changed later by another authorized or local
action. The command store has no independent rollback-resistant witness, and the gate does not prove
power-loss durability, permanent state, representative hardware, electrical timing, two-physical-host
behavior, or fitness for locks, medical, fire, vehicle, or industrial control. Every later mutation
needs its own reviewed effect contract.
