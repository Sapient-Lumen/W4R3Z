# ADR 0311: Witness update policy and lifecycle state

- Status: accepted and implemented for the opt-in update-lifecycle lane
- Date: 2026-09-02

## Context

The signed-update path already separates transfer, release authorization, inert staging, slot
selection, restart, health confirmation, and rollback. Its canonical owner-local policy selects the
release signers, target, namespace, payload kind, store root, bounds, and health interval. Its fixed
stable-device-signed state selects the confirmed/candidate revisions and records lifecycle
generation, health, boot, and rollback facts. Those signatures prove authorship and integrity, but
a storage attacker could restore an older mutually consistent policy, state, slots, and `current`
pointer. Restoring a policy from before signer revocation could admit a release key the owner retired.

A generic low-churn policy checkpoint is insufficient for this state machine. Once an external
witness accepts a pending successor, crash recovery must possess the exact device-signed successor
state it is authorized to install. Guessing or aborting to the old side would weaken the monotonic
protocol.

## Decision

Add a separately enrolled `update-lifecycle` rollback-witness lane. Its digest length-binds the exact
canonical update-policy record and either explicit state absence or the complete fixed signed
`update.state` bytes. Slot payload bytes are not duplicated in the witness digest: signed state
already binds the selected sequence, size, digest, kind, and manifest record, and every selected
slot is independently rehashed before use. `current` is not authority; it is a derived pointer that
must be repaired from the witnessed signed state.

The v1 lane has one deliberate invariant. State absence is witness position 1, and signed state
generation `g` is position `g+1`. Every lifecycle mutation already advances generation exactly once,
so the invariant removes a redundant local checkpoint and detects skipped, repeated, or forked
state. The enrolled policy is immutable within this witness epoch. Policy rotation therefore
requires the later explicit replacement/re-anchor ceremony; there is no silent policy adoption or
counter reset.

Before external pending CAS, IoTox writes one owner-private stable-device-signed intent containing
the exact selector, current/next heads, random transaction nonce, and complete signed successor
state. The order is:

1. reconcile policy, local state, retained intent, and authenticated external record;
2. durably write the exact successor intent;
3. compare-and-swap external committed old to pending new;
4. atomically install and reverify the exact signed successor state;
5. compare-and-swap external pending to committed new; and
6. durably remove the intent, then perform or repair the derived pointer effect.

Ambiguous CAS replies are resolved only by authenticated query and exact idempotent retry. Pending
recovery accepts only the two exact state sides named by the signed intent. Missing/tampered intent,
wrong selector, wrong generation, same-position fork, unrelated local state, unavailable service, or
complete old-state restoration fails closed.

`iotox witness-update-enrollment --config PATH` emits the device-signed no-replace enrollment for
the current exact policy/state. Witnessed startup requires the complete authenticated service,
`--witness-update-lifecycle`, enabled signed updates, the policy, and an explicit intent path in an
owner-private directory. The Agent constructs and reconciles the store inside security startup,
before RuntimeTree. Later update service construction must observe the identical policy.

Stage, apply, health-window opening, confirmation, explicit health expiry, automatic restart
rollback, and failed-service rollback all use the coordinator because each changes signed lifecycle
state. In witnessed mode rollback commits state before moving `current`. If apply committed state but
crashed before the pointer switch, restart repairs the pointer forward to the witnessed candidate;
the one-use health token still controls confirmation. The default-off unwitnessed mode retains its
existing state-first apply and pointer-first rollback recovery contract. Quarantine retention does
not select a slot or lower signed lifecycle state and remains outside this lane; permanent purge is
still absent.

## Consequences

Four owned checks bring the direct registry to 787. They cover complete local state rollback,
pending-CAS lost reply with local old state, committed-CAS lost reply with local new state, and
interrupted apply-pointer repair followed by witnessed health-window advancement. The retained
two-guest service gate enrolls this eighth lane, starts the source-linked Agent through it, and
rejects an uncommitted canonical update-policy substitution before RuntimeTree.

This closes update policy/lifecycle freshness relative to the selected authenticated service record.
It does not prove that the service is operationally independent, protect an unlocked live kernel,
certify payload correctness, make quarantine deletion safe, or define witness replacement. It also
does not witness per-namespace synchronization roots or tree-v2 frontier/maintenance state.
