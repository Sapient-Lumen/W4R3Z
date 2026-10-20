# ADR 0259: Qualify multi-source content over exact actual-Tor workers

Status: accepted, 2026-08-30

## Context

ADR 0258 separated content authority from content carriage. Its deterministic gate proved that two
independently authorized sources could be frozen onto two auxiliary identities, and its first
genuine Sandwurm gate proved one native-authority/Tor-content lane. It did not prove that two live
publishers could contribute complementary content through distinct actual-Tor workers in one
atomic pull.

The old forced-TCP construction was not the right next experiment. It required one subscriber Tox
identity to retain two publisher friendships and repeatedly failed at durable second-session
rendezvous before content work. Route workers remove that incidental prerequisite: every publisher
keeps an independently authenticated native primary session for writer authority and HEAD proof,
while a separately keyed reciprocal worker carries only already-authorized content-v2 traffic.

Before this qualification, aggregate `sync-status` could show that a pull used auxiliary content
but could not independently prove which source principal used which worker. A successful transfer
would therefore be insufficient evidence of distinct-carrier contribution.

## Decision

Expose a bounded owner-private source-carrier record for every live content pull source. Each
`content-source-job=` status record binds:

- the job and source identifier;
- the source's primary friend/epoch, stable principal, and authority route;
- primary or auxiliary carrier class;
- the exact carrier route key, worker incarnation, auxiliary friend/epoch, remote coordinator,
  remote route generation, and primary authority epoch.

This changes no peer framing, scheduling, authority, or persistence. It makes the already-frozen
source/carrier decision inspectable without content bytes or paths.

Accept the Sandwurm `sync-content-multi-route-actual-tor` gate as the first genuine routed
multi-source qualification. Its topology is:

- subscriber primary, publisher-primary, and publisher-secondary Agents on two Sandwurm guests;
- independently authorized native direct-UDP primary sessions for both publishers;
- one exact reciprocal `tox/tor` worker pair per publisher;
- two host Tor processes, one per guest, and one pinned public Tox target;
- one atomic `sync-pull-multi-route PRIMARY sandwurm-file tox/tor SECONDARY` invocation.

The gate must prove before acceptance that both auxiliary workers negotiate content-v2, both source
principals are bound to their expected distinct route keys, both sources answer availability and
contribute at least one object, the original primary alone supplies the signed HEAD, the complete
CAS fabric verifies, HEAD acceptance remains last, and activation is explicit. Packet captures must
show mixed native/proxy use with zero unexpected context packets. The independent verifier must
recompute the sorted carrier-set commitment from the strict checkpoint rather than trust receipt
counters alone.

The first run exposed an independent startup-preflight defect: strict worker validation evaluated
the primary transport endpoint lists before applying exact worker bootstrap/TCP-relay replacements.
CLI preflight and runtime construction now share `apply_worker_network_override`, so both validate
the same effective topology. Empty worker endpoint lists still inherit the primary template;
nonempty lists replace it exactly.

## Evidence

Accepted compact proof `pair.j0z04_2i` records:

- two source principals and two distinct auxiliary route keys;
- carrier-set SHA-256
  `e4cc6e4fb61f9710713cb8201b5ff54c9f04ba830ffb7cad5f3d859bb0f82505`;
- five primary-source objects and one secondary-source object;
- four availability requests and four availability results;
- one pull attempt, zero pull failures, and one atomic activated revision;
- two actual Tor instances with 100% bootstrap, three-hop circuit observations, and seven
  successful guest source streams in aggregate;
- zero unexpected-context packets in both TAP captures; and
- identical source-linked binary SHA-256
  `c54bab1a7c52ca241bfa46b1ce1894e6476a0afaa544456d85e80e3816bf736f`
  in both guest receipts.

The separate verifier accepts both the raw root and its 14,680,064-byte compact export. See
`../evidence/2026-08-30-sandwurm-sync-content-multi-route-actual-tor.md`.

## Consequences

IoTox now has a genuine-provider result for complementary multi-source content with native
authority and distinct Tor-routed Tox identities. The failed single-identity forced-TCP rendezvous
is no longer a prerequisite for this product shape.

This is a same-computer, two-VM, one-public-Tox-target, one-time-window mechanism result. The two
device-side workers share the device guest's Tor process. It proves exact Tox worker identity,
source attribution, Tor confinement, complementary contribution, integrity, and activation
ordering. It does not prove per-source circuit diversity, independent physical paths, anonymity,
traffic-analysis resistance, throughput gain, byte striping, source discovery, transparent
same-job failover, I2P content-v2, or behavior across physical hosts.

The next destructive gate is exact selected Tor-worker loss after positive multi-source progress.
It must fail and clean the whole job without moving that source to native, then require an explicit
fresh pull after the same signed worker recovers. Comparative multi-lane performance belongs after
that safety result.
