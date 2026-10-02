# ADR 0306: Witness application and Ratox startup incarnations

- Status: accepted and implemented for opt-in application and Ratox lanes
- Date: 2026-09-02

## Context

The application protocol and Ratox host already use device-signed, process-locked incarnation
records. Advancing those records on every process start prevents two live local processes from
sharing one namespace, but their monotonic truth lived on the same disk. Restoring a complete older
Agent snapshot could therefore reuse session identifiers, replay windows, or terminal host
namespaces even after ADR 0305 protected authority.

The two lanes have unusually clean witness semantics: every successful startup must consume exactly
one next incarnation before any runtime, network, command, or PTY surface exists. They can reuse the
authenticated witness protocol without inventing a policy-mutation API or changing peer framing.

## Decision

Extend the closed witness lane vocabulary with `application-incarnation` and
`ratox-incarnation`. Each lane is enrolled separately under the same create-once device/domain/epoch
identity. A quiescent offline command reads the exact device-signed local record under its ordinary
lease lock; absent state enrolls the all-zero position-zero head.

An opted-in startup performs this transaction while retaining the incarnation lock:

1. load and verify the exact local signed record and query its enrolled witness lane;
2. reject any committed-head mismatch before creating `RuntimeTree`;
3. durably write a fixed device-signed intent containing both heads, nonce, and the exact next
   128-byte signed incarnation record;
4. CAS the witness from committed to one-step pending;
5. atomically install and re-read that exact local record;
6. CAS pending to committed; and
7. fsync-unlink the intent.

Recovery is forward-only. Pending plus exact intent accepts only the exact old or exact new local
side and deterministically completes it. Missing intent, a foreign selector, deletion, fork, digest
mismatch, non-adjacent position, or service uncertainty fails closed. Ambiguous CAS replies are
resolved by a signed query. A successfully recovered prior start is completed and then the current
fresh process consumes the following incarnation.

The application lane is optional with `--witness-application-incarnation`. The Ratox lane is
optional with `--witness-ratox-incarnation` and is valid only when the Ratox host is enabled. Both
reuse the pinned ADR 0305 endpoint, domain, epoch, device identity, and independent-service
requirement, but have distinct enrollment records, service records, hashes, and local intents.
Default intent paths are companions of their respective state records.

The Ratox witness is acquired during security initialization, before terminal profile activation
and runtime creation. A later startup failure may consume an incarnation; monotonic namespace burn
is safe, while reuse is not. Application is ordered before Ratox. If the latter refuses, the former
may already have advanced, but no external effect surface has appeared.

## Consequences

Five new owned checks bring the direct registry to 772. They cover both closed lanes, exact
position-one/two advancement, complete correctly signed local rollback refusal, same-host backend
refusal, recovery when the external record remains pending after the local write, and a real
authenticated TCP-service application advance.

The retained two-guest service gate now enrolls authority, application, and Ratox independently. It
uses a real non-root Ratox login profile, advances all three through the source-linked Agent, and
restores older valid application and Ratox records separately. Both refuse before runtime while the
witness guest remains current. Authority rollback, exact-current restoration, outage, service
restart, wrong-key refusal, and final recovery remain in the same gate.

This closes startup namespace freshness, not terminal policy freshness. An old profile/binding can
still restore sudo or weaker confinement, and route generation, sync policy/state, update state,
and mutating-command effects still need purpose-built witness transactions. The VMs still share one
physical/admin failure domain; ADR 0305's production independence requirement is unchanged.
