# ADR 0168: Bind sync authority to an exact transfer carrier

Status: accepted at the deterministic Agent boundary, 2026-08-25.

## Context

The primary IoTox session already proves the remote stable principal, current authority-ledger head,
online epoch, negotiated synchronization feature, and signed HEAD exchange. An authenticated bulk
worker proves that it is a member of the same remote principal's signed route set, but it is not an
authority session and must not be made one by copying primary facts onto its friend number.

ADR 0167 supplies a bounded object-only auxiliary frame carrier. Gate 3 still needs the parent Agent
to join that carrier to one real primary authorization, route FileId offers and terminal truth through
the exact worker incarnation, and continue safely when the carrier disappears.

## Decision

`SyncPeerContext` separates primary authority identity from transfer-carrier identity. Primary facts
remain the primary friend number, online epoch, Tox route key, complete local authority snapshot, and
the exact proven remote authority snapshot. A transfer carrier independently freezes:

- primary or auxiliary class;
- local Tox route key and random worker incarnation;
- carrier-local friend number and online epoch; and
- the authenticated remote route-set generation, exact coordinator Tox key, and primary authority
  epoch that admitted an auxiliary member.

A primary carrier must exactly equal the authority route and epoch. An auxiliary carrier must have a
nonzero remote generation and be present as a currently ready bulk member whose reciprocal binding
proves the same stable principal, coordinator key, and primary epoch as the selected current primary
authority session. No auxiliary callback constructs, caches, or substitutes authority.

HEAD discovery/result and activation remain on the primary route. Auxiliary routes admit only
whole-object request/result frames and their exact FileId file lane; range requests remain primary-
only. Publisher replay identity includes the complete transfer carrier in addition to primary
authority and message identity, so the same canonical request may be retried on a replacement route
without confusing it with an exact-incarnation replay.

Subscriber attempts freeze their carrier. File receive/cancel and terminal dispatch use that exact
carrier, and coordinator work admission/release is charged to the signed member budget. On auxiliary
loss, the parent first withdraws that carrier, purges retained application and transfer correlations,
fences its scheduler attempts, discards incomplete staging and active signed-attempt records, and
releases capacity. A ready replacement for the same proven principal receives fresh attempt IDs,
message IDs, FileIds, and staging paths. Already committed digest-addressed objects remain committed.
Late results, offers, or terminal records from the old carrier cannot match the replacement.

Agent enables the ADR 0167 worker frame gate only when both synchronization and route workers are
explicitly enabled. Single-route configuration retains the existing primary path and range behavior.
Auxiliary file managers run the same bounded per-peer carrier service as the primary Agent so a
second admitted object cannot remain paused indefinitely.

## Consequences

- Multi-route synchronization does not turn route membership into authorization.
- Whole immutable objects, not Tox file numbers or byte streams, are the reassignment unit.
- Route loss can waste transport bytes, but it cannot produce a partial object commit or advance the
  accepted HEAD.
- The current policy uses one exact carrier per pull at a time. It is safe reassignment, not striping,
  adaptive scheduling, transparent bonding, or multi-source qualification.
- A signed HEAD is accepted only after both candidate objects independently verify and commit; local
  activation remains a later explicit token-bound effect.

## Verification

Service tests freeze primary/auxiliary validation, carrier-scoped publisher replay, exact loss
cleanup, fresh reassignment identities, reordered offers/results, and rejection of stale old-route
results. The complete Agent test starts one protected primary and two reciprocally authenticated bulk
workers. It performs HEAD discovery on the primary, dispatches both object attempts to the first bulk
worker, forces that worker offline, observes selection of the second exact worker, commits both
objects, accepts the signed HEAD last, and activates only through local control. The test also exposed
and repaired missing auxiliary carrier-window service that had left the second receive paused.

The owned GCC Debug registry passes this deterministic boundary. Genuine two-guest Sandwurm loss,
late-completion injection, protected-Ratox coexistence, and fixed/adaptive scheduler science remain
Gate 3/4 evidence rather than claims of this ADR.
