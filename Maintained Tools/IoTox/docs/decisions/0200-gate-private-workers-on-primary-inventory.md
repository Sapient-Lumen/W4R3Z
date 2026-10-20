# ADR 0200: Gate private workers on primary inventory

Status: accepted and implemented behind an explicit construction gate, 2026-08-27.

## Context

ADR 0198 requires cross-context route inventories to remain private. ADR 0199 froze the v2 wire
formats, but a codec alone cannot enforce ordering, replay, revocation, or the point at which an
auxiliary worker becomes usable. Advertising v2 before those live rules existed would have claimed
a disclosure property the Agent did not yet provide.

## Decision

Add the explicit `--enable-private-route-bindings` Agent gate. It requires `--enable-route-workers`,
an authenticated signed route set, its generation checkpoint, and exact-key auxiliary savedata.
Without this flag the existing v1 worker exchange and bytes remain unchanged.

When enabled, the primary and auxiliary HELLO masks include both route-binding-v1 and its dependent
private-route-binding-v2 bit. For each exact application-ready, `remote_authorized` primary
friend/transport-key/online-epoch association, the Agent freezes one randomly identified type-26
frame and retries only those same bytes until toxcore accepts it. A changed authority principal
within that association fails closed. Reuse of a deleted friend number by a different transport key
starts a distinct association rather than inheriting the old key's epoch ordering.

Inbound type-26 frames enter a bounded process-local registry only after rechecking the exact
session, authority friend/key/epoch, transcript digest, authenticated stable principal, route-set
signature, and coordinator key. The registry retains at most 64 active primary edges and 64
stable-principal/coordinator generation high-water records. An exact duplicate is idempotent;
same-association conflict, older generation, or different same-generation artifact digest is
rejected.
Losing the exact authority edge removes the usable inventory immediately while retaining its
generation/digest high-water for the rest of the process lifetime.

Only a currently admitted inventory containing the auxiliary peer is handed to a worker. V2 and v1
worker factories are mutually exclusive. Before handoff, the worker may complete HELLO/CAPABILITIES
but sends no binding and cannot become authenticated. After handoff it sends only the fixed 256-byte
type-27 member proof, verifies the reciprocal proof against that exact inventory and primary edge,
and may then advance through the ordinary coordinator `authenticated`/`ready` states. Removing or
changing the context cancels worker transfers, terminates queued outcomes, purges sync frames, clears
both proofs, and makes the coordinator withdraw readiness before further application work.

## Consequences

- An auxiliary friendship no longer receives a sibling roster in v2 mode.
- Primary authority, inventory admission, auxiliary proof, and coordinator readiness now form one
  explicit ordering chain rather than independent best-effort facts.
- Process restart deliberately forgets remote generation high-water; the signed local route-set
  checkpoint remains durable, while durable remote-inventory rollback memory is a separate future
  policy decision.
- The deterministic provider gate proves primary inventory before member proof, exact 256-byte
  worker exchange, readiness, and readiness withdrawal on primary friendship removal. It does not
  establish a genuine two-guest native/Tor mixed-context route, public Tor privacy, anonymity, or a
  long-running multi-route soak.
- The next scientific gate is a Sandwurm two-guest v2 topology using independent route identities,
  followed by the actual-Tor multi-peer/relay/time matrix already open in M8.
