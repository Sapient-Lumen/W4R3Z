# Sandwurm actual-Tor multi-source content qualification — 2026-08-30

## Claim

Two independently authorized content-v2 publishers contributed complementary immutable objects to
one frozen signed HEAD while their primary writer/HEAD sessions remained native direct UDP and each
source's content lane used a distinct exact `tox/tor` route-worker identity. One explicit atomic pull
verified the complete 4 MiB paged fabric, accepted HEAD last, and activated it with zero pull
failure.

This is the qualification record for ADR 0259. It is not an anonymity, physical-path-diversity, or
performance claim.

## Construction

The host runner launched two simultaneous Sandwurm Cloud Hypervisor guests. The client guest ran one
subscriber Agent with a native protected route and two Tor bulk workers. The device guest ran two
publisher Agents: the primary owned one native protected route plus the first Tor worker, and the
secondary owned a separate native protected route plus the second Tor worker. Both publishers proved
the same foreign-writer HEAD and `sync.publish` authority on their native primary sessions. Their CAS
inventories were complementary.

The client invoked:

```text
iotox sync-pull-multi-route PRIMARY sandwurm-file tox/tor SECONDARY
```

The product exposed one strict per-source carrier checkpoint after convergence. The verifier bound
the primary principal to route
`13E3E4EFA78A92E3A1B41AFF31BE596496903F83383566E1BDD15C02BE7ADC10`, the secondary principal to
route `478CD68E0D2035CD1B63CC07558070EBEA7897DAB135896115BB85B524E23C1A`, required the routes to be
distinct, sorted them, and recomputed carrier-set SHA-256
`e4cc6e4fb61f9710713cb8201b5ff54c9f04ba830ffb7cad5f3d859bb0f82505`.

The host used two actual Tor 0.4.8.11 processes, one for each guest, and the pinned numeric Tox target
shown by the retained manifest. The device-side publisher workers share the device Tor process; this
cell does not assign or prove a distinct Tor circuit per source.

## Invocation

```sh
python3 tools/run-sandwurm-pair.py direct-udp \
  sync-content-multi-route-actual-tor \
  --tor-node \
  144.217.167.73:33445:7E5668E0EE09E19F320AD47902419331FFEE147BB3606769CFBE921A2A2FD34C

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/lab/pairs/pair.j0z04_2i

python3 tools/export-sandwurm-pair.py \
  .sandwurm/lab/pairs/pair.j0z04_2i \
  .sandwurm/exports/pairs/pair.j0z04_2i

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.j0z04_2i
```

## Accepted observations

- scenario `sync-content-multi-route-actual-tor`, route mode `direct-udp`, status `passed`;
- two independently authorized sources and two distinct exact auxiliary carriers;
- five objects supplied by the primary source and one by the secondary;
- four availability requests and four availability results;
- one initial pull attempt, zero initial pull failures, and atomic-pull evidence from both roles;
- artifact SHA-256
  `844dbd0270ee58cf1e1b8062460e6b5f24b974a24fd482e861689d65e81598a7`;
- manifest SHA-256
  `f8637c280348a3af9685afdbb53a0351236ec52e26abb146ec8f3a20c39c9b66`;
- accepted HEAD-record digest
  `5418cf893bf66afe955edf1b855e9e72c4069693d245fef9a579f8917c02141c`;
- two actual Tor instances, both at 100% bootstrap, with three-hop circuit observations;
- four successful client-guest Tor source streams and three successful device-guest streams;
- client TAP: 3,063 proxy packets, 2,420 native UDP packets, zero unexpected-context packets;
- device TAP: 4,642 proxy packets, 3,668 native UDP packets, zero unexpected-context packets; and
- identical source-linked binary SHA-256
  `c54bab1a7c52ca241bfa46b1ce1894e6476a0afaa544456d85e80e3816bf736f`
  in both receipts.

The first bounded attempt failed before authority readiness because CLI preflight ignored an exact
worker TCP-relay replacement while validating strict Tor. The retained local reproduction produced
the precise error. `apply_worker_network_override` now supplies one shared effective-topology
transformation to preflight and runtime construction, with owned-registry coverage. The accepted run
contains the corrected binary.

## Verification and retention

The independent verifier accepted the raw proof root and the compact export:

- raw manifest SHA-256:
  `320b1bf7e056d85e87afadf585317d38cfa1ab37534de9a321e628dbfa967c94`;
- compact manifest SHA-256:
  `9530cc90b2809d99c9a159f979dbbb0528f4e457fe4aa3ee3ef22f047539f05b`;
- compact-export record SHA-256:
  `9bfb5a281e517aa88da7d599b8a394acb330e21dc699285564d4813be6eb2a7a`;
- client receipt SHA-256:
  `7eeb27dbae3c3708272a9fcc25c14056f01d975b04e4ca1f8f5b123a0431b0d2`;
- device receipt SHA-256:
  `f8b25155d9e6514d0fd3477d5e57f4a3223a0ad8434f5cd9db781295d58818c2`;
- client capture SHA-256:
  `8d0235b46aae8ec268678372b310fb54cbf76e2aa0fcc43bb54a704e109867ae`;
- device capture SHA-256:
  `45033fe9dd89838881c459a216534f0f27d7dd9f9f730d0c353be54750f4ec00`;
- compact allocated bytes: 14,680,064.

The compact export retains the receipts, strict carrier checkpoint, manifest, Tor bootstrap/circuit/
control evidence, TAP captures, capture logs, and Sandwurm chain records. It omits private writable
guest disks. The raw 2.5 GiB root is disposable after compact verification.

## Limits and next gate

This same-computer cell proves the mechanism across two isolated VMs, not two physical hosts. Both
Tor processes used one public Tox target in one time window. The evidence does not prove per-source
Tor circuit separation, relay diversity, independent bottlenecks, anonymity, resistance to traffic
analysis, performance improvement, or byte-level striping.

The next safety gate will kill one selected Tor content worker after positive complementary-source
progress. The current job must fail closed with no native downgrade and clean staging; only an
explicit fresh pull after exact worker recovery may converge. Multi-lane throughput science follows
that destructive boundary.
