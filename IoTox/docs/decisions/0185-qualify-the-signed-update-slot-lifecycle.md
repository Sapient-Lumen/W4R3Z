# ADR 0185: Qualify the signed update slot lifecycle

Status: accepted construction lifecycle over direct UDP and forced TCP, 2026-08-26.

## Context

ADR 0184 separated release intent from synchronization delivery and froze the signed bundle. The
remaining first M7 slice was a durable device-side state machine. A valid release signature alone
cannot make received bytes current: the device must bind an exact accepted sync HEAD, install only
an inactive immutable slot, survive interruption at every pointer/state boundary, require a later
Agent incarnation to report health, and retain a known confirmed rollback target.

The first adapter intentionally handles an inert `opaque-slot-v1` regular file. It is a construction
vehicle for update authority and recovery semantics, not a bootloader or executable installer.

## Decision

Store a stable-device-signed fixed record beside owner-private immutable slots. Staging joins the
exact accepted sync HEAD to its artifact, independently verifies the pinned release signature and
payload digest, copies only the payload to `slots/<sequence>-<SHA256>.payload`, rehashes it, freezes
it at mode `0400`, and commits `staged` state. At most eight slots may exist; exhaustion refuses new
work without deleting rollback material.

Applying commits `pending-restart` before replacing the exact `current` symlink and returns a random
one-use health token. The applying Agent cannot confirm itself. The next durable protocol
incarnation verifies the slot and pointer, records one boot attempt, and opens the bounded health
window. Exact-token confirmation in that incarnation advances the confirmed release high-water.
A second restart, health expiry, or incomplete transition rolls back to the last confirmed slot.
Corrupt slots, invalid signed state, and bad tokens fail closed rather than authorizing a repair from
untrusted local facts. A transient live-expiry transition failure is recorded and retried once per
second only while that same signed health incarnation remains pending.

Both directions of the pointer/state crash window have deterministic recovery. Startup completes a
state-first interrupted apply when the candidate pointer was not yet installed. If rollback changed
the pointer before its final signed record was committed, startup recognizes that exact confirmed
target and completes rollback instead of treating the state as corrupt. Slot-capacity checks occur
before pointer mutation.

Expose only same-user local controls in this slice: `update-status`, `update-stage`, `update-apply`,
and `update-confirm`. Keep `signed-ota-v1` feature bit 20 dark. Remote update admission remains a
separate capability-gated protocol using existing `install.firmware` authority.

## Consequences

- Sync publication, delivery, HEAD acceptance, release signing, local update policy, and device
  health are independent gates.
- A confirmed sequence cannot be replaced by an older or equal sequence. A failed unconfirmed
  sequence may be retried because it never became the high-water.
- Local corruption and isolated signed-record rollback fail closed. Coordinated replay of every
  valid local record remains outside a software-only monotonic guarantee.
- There is no destructive slot collector. A full eight-slot store closes admission until a later
  separately reviewed retention policy exists.
- A deployment adapter may consume the selected opaque slot only after separately defining boot,
  power-cut, recovery, health, and representative-hardware behavior.

## Qualification

Deterministic unit, process, and real-Agent tests cover canonical bundle/policy parsing, no-clobber
creation, tamper and unsafe-path refusal, stage/apply/restart/confirm, health-expiry rollback, abrupt
process exit, interrupted apply, interrupted rollback, and a complete sync-publication-to-rollback
sequence.

The same source-linked binary
`c3fe27569d07092c6fde2876ed43fcff1db8eb520ed94645001970cb027d1ada` passes the genuine
two-Sandwurm-guest lifecycle over observed direct UDP and forced TCP. Each cell publishes and
transfers one exact 4,194,624-byte bundle, accepts its signed sync HEAD, stages sequence 1, applies,
restarts the Agent once, observes `health-window-opened`, confirms the exact token, and verifies the
selected private slot. Neither peer advertises feature bit 20. Exact receipts and nonclaims live in
`evidence/2026-08-26-sandwurm-signed-update.md`.
