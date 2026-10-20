# ADR 0169: Qualify immutable sync reassignment across live routes

Status: accepted, 2026-08-25.

## Context

ADR 0168 completed deterministic Agent reassignment but did not prove that two genuine IoTox peers
could carry the same policy through independent toxcore instances. Gate 3 required a real partial
receive, exact loss of only its auxiliary carrier, rejection of old-incarnation outcomes, fresh
assignment to another authenticated bulk route, restoration within the signed restart budget, and a
still-usable protected Ratox route. The proof had to pass both native carrier classes without making
route loss, connection choice, or recovery timing implicit.

The signed route-set format and auxiliary object framing were already frozen. Qualification needed
an operator authoring entrance and a narrow fault seam, not a new wire message.

## Decision

`route-set-create` is an offline, creation-only authoring command. It requires an existing stable
device identity, generation, coordinator key, and two through sixteen explicit member records. It
signs the canonical route-set-v1 bytes, verifies its own result, writes one owner-private file without
replacement, and emits only a content-free summary. It is not a runtime membership mutation.

The default-off `--qualify-route-stop-after-bytes N` seam is accepted only when synchronization and
route workers are both explicitly enabled. After an actual incoming immutable-object receive reaches
the exact positive byte threshold, Agent stops that attempt's bulk worker. The protected member is
ineligible. Agent must then:

1. retire the old worker incarnation and fence its attempts before reuse;
2. discard incomplete staging and issue fresh attempt, message, FileId, and staging identities on a
   different ready bulk route;
3. reject every terminal result retained for the old incarnation as stale;
4. verify and commit each immutable object once, accept the signed HEAD last, and activate only by
   the existing explicit local token; and
5. spend exactly one signed restart-budget unit, reconstruct the stopped route from its retained
   savedata under a fresh random worker incarnation, reauthenticate it reciprocally, and return it to
   `ready` without erasing the observed fault counters.

Content-free status retains exact qualification position, carrier-loss, reassignment, stale-terminal,
and recovery counters. This seam is laboratory control, remains disabled by default, and supplies no
general runtime route-kill API.

The protected primary continues to own authority, HEAD exchange, activation, and Ratox. The
subscriber principal receives one atomic least-privilege `operator` grant containing only
`sync.subscribe,interactive.terminal`; auxiliary membership still grants no authority.

## Consequences

- Gate 3 proves whole immutable-object failover, not byte striping or transparent socket bonding.
- Bytes received before the fault may be wasted; no partial bytes, Tox file number, or old worker
  result become durable scheduler truth.
- Same-savedata recovery preserves a Tox route identity but receives a fresh process-local worker
  incarnation, so stale callbacks remain distinguishable.
- UDP and TCP may place the fault at different byte positions. Both must preserve identical object,
  manifest, and signed-HEAD identities.
- The protocol-route-set-v1, route-binding-v1, sync-wire-v1, and Ratox v1 framing remain unchanged.
- Adaptive selection, phase/startup ordering, relay diversity, and long-running churn were deferred
  to Gate 4 and Gate 5. ADRs 0170 and 0171 subsequently accept selection and counterbalanced policy
  phase order; ADR 0175 accepts one loss→reassignment→replacement-progress→cancel order. Randomized
  startup/timing and opposite/simultaneous fault order remain open.

## Verification

Owned tests cover strict route-set authoring, malformed members, no-clobber output, exact worker
retirement/restart, fresh incarnation assignment, and the default-off Agent counter path. The
`sync-tree-route-loss` Sandwurm cell constructs a protected primary plus two independently keyed,
reciprocally authenticated bulk routes in each of two simultaneous NixOS guests. It injects loss only
after at least 65,536 incoming bytes, converges the same deterministic directory through the other
bulk route, restores the stopped route, and then runs 40 exact Ratox samples on the primary.

Accepted direct-UDP and forced-TCP cells, their exact measurements, compact proof hashes, and
nonclaims are retained in `../evidence/2026-08-25-sandwurm-sync-route-loss.md`.
