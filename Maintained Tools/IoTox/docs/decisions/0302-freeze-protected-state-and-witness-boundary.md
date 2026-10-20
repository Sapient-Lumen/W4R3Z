# ADR 0302: Freeze protected-state closure and independent witness boundary

- Status: accepted design; fscrypt tier and authority coordinator implemented by ADR 0303, remote service by ADR 0305
- Date: 2026-09-02

## Context

IoTox stores authority across many protocols: opaque Tox savedata, plaintext private keys, signed
ledgers and guards, incarnations, route identities, Ratox profiles, synchronization CAS/workspaces,
update slots, and deployment policy. Several have their own descriptor-pinned atomic replace or
committed/pending recovery transaction. Encrypting a few records inside `StateStore` would miss
equivalent authority, break custom recovery ordering, and invite an inaccurate at-rest claim.

Every current local guard detects isolated rollback. None detects coordinated replay of the guard
and all matching roots from the same disk image.

## Decision

Implement workstream 8 in two explicit tiers described by `docs/protected-local-state.md`:

1. an externally unlocked fscrypt-v2 root with fail-closed verification of the complete configured
   and derived durable-state closure before any network or effect surface; then
2. an independently controlled monotonic compare-and-swap witness, piloted on the authority lane
   with local durable intent and witness pending/committed recovery.

IoTox will not take an unlock secret in argv, environment, config, local control, or peer traffic;
derive the data key directly from RecallRoot; silently accept plaintext; infer dm-crypt custody from
a path; treat an on-disk mock as independent; reset a counter for restore; or let witness outage
downgrade protection.

The design includes explicit initialization, quiescent backup, forward restore, witness/board
replacement, emergency re-anchor, cloning, key escrow/loss, and offline migration ceremonies. The
witness expands to other lanes only after the authority crash matrix is proved. Mutating commands
must be witnessed before effect, not only after journaling.

## Consequences

Existing file formats and crash semantics can operate unchanged inside the encrypted filesystem.
The protection claim becomes measurable and deployment-specific instead of a per-file cosmetic
feature. The witness can later prevent whole-root replay without putting high-churn diagnostics or
content CAS writes directly behind a TPM counter.

This ADR closed the architectural ambiguity, not workstream 8. ADR 0303 implements and retains VM
evidence for the fscrypt mode plus the authority transaction coordinator; ADR 0305 adds the
authenticated remote-service backend and two-guest state-separation gate. No same-host test proves
operational independence, no full sync/effect witness lanes exist, and restoration of the service's
own disk still depends on its deployment's rollback-resistant or independently checkpointed
persistence. Protected permanent purge and witnessed effect claims therefore remain unavailable;
stolen-media protection is limited to an exactly configured fscrypt deployment while its externally
held key is absent.
