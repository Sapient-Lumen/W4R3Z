# ADR 0269: Distribute same-source content across exact auxiliary carriers

Status: accepted, 2026-08-31

## Context

ADR 0259 proved complementary content over two auxiliary workers, but each worker belonged to a
different independently authorized source principal. ADR 0262 separately proved two simultaneous
object lanes from one source over one Tox session. Neither result answered whether one stable source
and one primary authority session could deliberately use more than one authenticated auxiliary
carrier without weakening HEAD authority, object attribution, or fail-closed loss.

Numeric Tox friend and file numbers are local to one transport instance. The first genuine
same-source run made that boundary concrete: both isolated route workers legitimately assigned their
only peer `friend=0`. Treating those numbers as globally unique would alias two distinct carriers.

## Decision

Allow repeated source selectors only in the routed atomic entrance:

```text
sync-pull-multi-route PRIMARY NAMESPACE ROUTE_CLASS SOURCE [SOURCE...]
```

Each repetition means “select another exact ready auxiliary carrier for this already authenticated
source principal.” Agent selects the complete carrier set atomically, requires every selected route
key/worker incarnation to be distinct, installs every binding before releasing the primary HEAD,
and refuses admission when the named class has too few eligible carriers. The ordinary
`sync-pull-multi` entrance continues to reject repeated peers.

The repeated path keeps the same stable principal, primary friend/online epoch, authority route,
coordinator, writer proof, and frozen signed HEAD. Only the auxiliary transfer carrier differs.
Availability, object request/result, FileId, CTA1, offer, and terminal truth bind the full carrier
tuple: class, route key, worker incarnation, route-local friend/epoch, route generation, coordinator,
and primary authority epoch. Route-local friend/file numbers may collide across workers and are
never sufficient correlation keys.

Schedule only complete immutable content objects onto a selected carrier. Do not split bytes inside
an object. Exact carrier loss remains terminal for the whole atomic job; there is no downgrade,
reassignment, post-HEAD rebinding, or same-job continuation. Repeated paths remain bounded by the
existing 15-auxiliary control limit and count conservatively against source admission.

Expose owner-private `requested`, `committed`, and `fetched-bytes` counters on every
`content-source-job=` row. These counters reveal no object content and exist to prove positive path
contribution and diagnose skew. Keep content-v2 message types 28--31, CTA1, feature bit 29, route
binding, and local-control v1.43 operation 90 byte-for-byte unchanged. Repetition was already
representable in operation 90; only its previously over-strict duplicate rejection changes.

## Evidence

Deterministic coverage now:

- converges one exact signed revision from complementary object inventories on two auxiliary
  carriers sharing one principal and primary authority session;
- requires positive availability and object contribution from both carriers;
- freezes the exact accepted HEAD and reconstructed artifact;
- rejects ordinary duplicate-source admission and routed admission when distinct carriers are
  unavailable;
- ignores loss of a lookalike/unrelated worker and fails the whole job on loss of either exact
  selected carrier; and
- uses colliding route-local friend numbers on the two carriers so correlation depends on the full
  carrier tuple.

Accepted compact Sandwurm proof `pair.iiuhmhy0` runs source revision
`a00147722899300fc5ba76f769c5dad21b6e0a50` and binary SHA-256
`ad3ffc663ea0ded7a7d849d73de991af338b8be08b267d4f417ca7818984fa04`. One native primary
authority session selects route keys
`13E3E4EFA78A92E3A1B41AFF31BE596496903F83383566E1BDD15C02BE7ADC10` and
`478CD68E0D2035CD1B63CC07558070EBEA7897DAB135896115BB85B524E23C1A` in class `tox/tor`.
Both carriers use local `friend=0`; their worker IDs are distinct. Carrier A commits one 272-byte
object; carrier B commits five objects and 4,194,560 bytes. All four availability queries receive
results, the exact 4 MiB artifact and HEAD verify, and activation remains explicit.

Both guests use Tor 0.4.8.11 and the reviewed public Tox TCP record
`205.185.115.131:33445`. Each host-side Tor process reaches 100% bootstrap and records four
successful guest-source streams. TAP captures retain 4,782/5,473 proxy packets and zero
unexpected-context packets. Raw and compact roots pass the independent verifier; the compact root
contains 21 secret-free files and allocates 14,811,136 bytes. See
`../evidence/2026-08-31-sandwurm-sync-content-same-source-multi-route.md`.

One non-accepted diagnostic run also distributed positive objects across both paths before an exact
Tor carrier disappeared. IoTox committed four of five requested objects (2,097,680 bytes), then
failed the whole job with `exact auxiliary content carrier went offline`, no activation, and no
reassignment. This corroborates the deterministic loss boundary but is not retained as an accepted
compact proof.

## Consequences

IoTox can now distribute immutable objects from one stable source across multiple independently
authenticated logical carriers while retaining one source identity and one HEAD authority session.
This closes the roadmap's same-source auxiliary-path construction gate and gives later bottleneck
science a truthful per-path accounting surface.

It does not establish byte striping, useful speedup, automatic carrier count, proportional load
balancing, route independence, separate Tor circuits or exits per carrier, physical-link or host
diversity, transparent failover, I2P content-v2, anonymity, availability, or fleet policy. Both
device-side workers in the accepted cell share that guest's one Tor process and one public relay
target. The default content lane cap remains one, and no framing changes.
