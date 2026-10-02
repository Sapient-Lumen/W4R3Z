# ADR 0258: Bind content sources to exact auxiliary routes

Status: accepted, 2026-08-30; deterministic construction and genuine one-source actual-Tor
qualification complete; routed multi-source qualification accepted separately by ADR 0259

## Context

ADR 0255 proved complementary content-v2 sources over direct UDP, but the corresponding forced-TCP
construction could not retain a second authenticated friendship on one subscriber Tox identity.
Thirteen bounded relay, admission, key-reuse, address-rendezvous, and placement variants narrowed
that result to durable second-session rendezvous in that topology. They did not show that c-toxcore
cannot carry the bytes, and repeating them would not answer a new question.

IoTox already owns distinct auxiliary Tox identities through route workers. Each worker is joined to
one live primary authority session by a reciprocal private route proof and an exact fence containing
the local route key, worker incarnation, auxiliary friend/epoch, remote route generation, remote
stable principal, remote coordinator key, and primary authority epoch. Range-v1 already uses this
separation. Content-v2 deliberately had not crossed it.

The important authority distinction is that an auxiliary worker cannot repair a missing primary
edge. The primary session proves the stable writer, ledger-v3 `sync.publish`, namespace membership,
and signed HEAD. A worker can only carry already-authorized object negotiation and file bytes.

## Decision

Permit content-v2 object request/result and exact sparse availability request/result frames on an
exact reciprocally authenticated bulk worker when both ends negotiate feature bit 29. The worker
still refuses HEAD frames, activation, authority records, and every unrelated application frame.
Its feature advertisement is separately construction-gated on both parent content services. Agent
finalizes that service-derived gate after content-service construction and before worker startup;
the supervisor refuses any later change, so negotiated capability remains lifetime-immutable.

Split each subscriber source into two frozen roles:

- its primary `SyncPeerContext` remains the only authority and signed-HEAD context; and
- before HEAD admission, the owner may bind that registered source's transfer context to one exact
  auxiliary carrier for availability, object request/result, FileId offer, CTA1 receive, terminal,
  cancel, and local retirement effects.

The bind is legal only while the job is strictly `awaiting-head`, only for an already registered
source with the identical independently authorized session/principal/capabilities/ledger head, and
only for a negotiated auxiliary carrier. HEAD admission freezes it. Rebinding after HEAD, changing
the source principal, or using an absent incarnation fails closed. The primary source's root
manifest request now uses its frozen source carrier rather than inheriting the HEAD carrier.

Local-control v1.43 operation 90 exposes the atomic entrance:

```text
iotox sync-pull-multi-route PRIMARY NAMESPACE ROUTE_CLASS SOURCE [SOURCE...]
```

`ROUTE_CLASS` must be `tox/native`, `tox/tor`, or `tox/i2p`. Before allocating the job, Agent proves
every primary session and selects one ready content-capable auxiliary worker in that exact local
class for each source principal. It then creates the job on the primary HEAD context, binds the
primary source carrier, installs all other auxiliary-bound sources, and only then releases the one
HEAD request over the original primary session. Setup or dispatch failure cancels the new job. Loss
of any registered auxiliary content carrier fails the current content job as a whole; there is no
transparent privacy downgrade or same-job source continuation.

The existing single-source spelling also accepts a named class only as
`sync-pull FRIEND NAMESPACE fail-closed ROUTE_CLASS`. Unqualified primary and primary-peer
multi-source commands keep their prior behavior.

No peer wire format changes. Frozen content-v2 message types 28--31, signed HEAD encoding, FileId,
CTA1, CAS verification, HEAD-last acceptance, and explicit activation are unchanged.

## Consequences

IoTox can now test the architecture the failed forced-TCP experiment actually suggested: keep
independently authenticated primary authority/HEAD edges on direct native sessions, while distinct
route identities carry forced-TCP, Tor, or I2P content. This is mixed-route content evidence, not a
claim that the authority session itself used the named route.

The deterministic owned-registry gate converges one frozen HEAD from two complementary authorized
stores while both availability/object/file paths use distinct auxiliary carrier incarnations. It
also proves that HEAD dispatch remains primary, a wrong principal cannot bind, post-HEAD rebinding
is refused, and exact auxiliary loss fails closed. The route-worker gate carries a canonical
content availability frame only when bit 29 is constructed and negotiated.

The genuine one-source Sandwurm gate keeps direct-UDP authority/HEAD context on each primary Agent,
uses two independent actual Tor processes for the reciprocal `tox/tor` workers, and moves the exact
paged 4 MiB content revision through the selected auxiliary carrier in one pull with zero failure.
Both receipts state the native primary and Tor auxiliary networks separately; the pulling role binds
the exact worker-key commitment and zero reassignment. See
`../evidence/2026-08-30-sandwurm-sync-content-actual-tor.md`.

This does not add source discovery, byte striping, automatic route replacement, authority over an
auxiliary friendship, or I2P qualification. ADR 0259 preserves the same split claim and qualifies
two independently authorized sources on distinct actual-Tor worker identities.
