# Sandwurm selected actual-Tor content-worker loss — 2026-08-30

## Claim

One selected auxiliary Tor worker disappeared after positive complementary-source content progress.
The original atomic job failed whole, transient staging and authority effects stayed fenced, no
source moved to native or another worker, the exact signed route recovered under a new worker
incarnation, and only a distinct explicit pull converged and activated.

This is the qualification record for ADR 0260. It is a bounded fail-closed mechanism result, not an
anonymity, availability-SLA, physical-path-diversity, or performance claim.

## Construction

The topology is ADR 0259's two simultaneous Sandwurm Cloud Hypervisor guests. The client guest runs
one subscriber Agent with a native protected route and two exact `tox/tor` bulk workers. The device
guest runs two publisher Agents, each with an independently authenticated native authority session;
their complementary CAS inventories serve one writer-signed HEAD through distinct Tor worker
identities. Two host Tor processes provide the guests' SOCKS endpoints and use one pinned public Tox
target.

The subscriber Agent was started with the lab-only seam:

```text
--qualify-route-stop-after-bytes 65536
--qualify-route-stop-worker 478CD68E0D2035CD1B63CC07558070EBEA7897DAB135896115BB85B524E23C1A
```

The first `sync-pull-multi-route` job had already committed valid immutable objects when a file
receive on that route crossed the threshold. IoTox stopped only the selected in-process worker. It
did not kill either Agent, either Tor process, either VM, or either native primary session.

## Invocation

```sh
python3 tools/run-sandwurm-pair.py direct-udp \
  sync-content-multi-route-actual-tor-loss \
  --tor-node \
  144.217.167.73:33445:7E5668E0EE09E19F320AD47902419331FFEE147BB3606769CFBE921A2A2FD34C

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/lab/pairs/pair.w31xqgd_

python3 tools/export-sandwurm-pair.py \
  .sandwurm/lab/pairs/pair.w31xqgd_ \
  .sandwurm/exports/pairs/pair.w31xqgd_

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.w31xqgd_
```

## Accepted observations

- scenario `sync-content-multi-route-actual-tor-loss`, route mode `direct-udp`, status `passed`;
- selected route
  `478CD68E0D2035CD1B63CC07558070EBEA7897DAB135896115BB85B524E23C1A`;
- stopped worker `2197901807973525542`, recovered worker `17674373597288179784`;
- 72,663 exact-carrier bytes at the fault, above the 65,536-byte threshold;
- first job `9581108307482772732`, replacement job `6950339517546930232`;
- two committed immutable objects and 528 fetched bytes before failure;
- failure detail `exact auxiliary content carrier went offline`;
- one carrier loss, zero reassignment, one affected job, and one worker recovery;
- empty transient staging, no accepted HEAD, and no activation after the failed job;
- native primary and secondary authority epochs both remained `1`;
- replacement pull contributed four primary-source and three secondary-source objects, accepted HEAD
  last, and activated explicitly;
- artifact SHA-256
  `844dbd0270ee58cf1e1b8062460e6b5f24b974a24fd482e861689d65e81598a7`;
- manifest SHA-256
  `f8637c280348a3af9685afdbb53a0351236ec52e26abb146ec8f3a20c39c9b66`;
- accepted HEAD-record digest
  `5418cf893bf66afe955edf1b855e9e72c4069693d245fef9a579f8917c02141c`;
- two actual Tor 0.4.8.11 instances at 100% bootstrap with three-hop circuit observations;
- five successful client-guest and three successful device-guest Tor source streams;
- client TAP: 4,035 proxy packets, 3,080 native UDP packets, zero unexpected-context packets;
- device TAP: 4,969 proxy packets, 4,255 native UDP packets, zero unexpected-context packets; and
- identical source-linked binary SHA-256
  `efc0b415f4198a67949ab7fce70b5c30f83c6cff3c6b69d4262b46ba9674fa04`
  in both receipts.

## Verification and retention

The independent verifier accepted the raw proof root and the compact export. The host manifest's
staging-clean and head-fenced role counts were mechanically rebuilt from the already-complete two
guest receipts after the verifier exposed a runner-side scenario allowlist omission; no VM receipt,
checkpoint, capture, or protocol artifact changed. ADR 0261 subsequently centralizes every common
multi-source-loss manifest field on one frozen scenario set.

- compact pair-manifest SHA-256:
  `1dd63aafa24b316e3a471e7947117f800706b8e885f5007c39fae8306934ce80`;
- compact-export record SHA-256:
  `5da3c2f2329a33aaf294857853346c5143a10235c42ff51cdb2b670837f79a8e`;
- client receipt SHA-256:
  `17c3a37850d1ec988816974f197a3d7683bbb248c5de19c855cf7879800c11e8`;
- device receipt SHA-256:
  `cab1c54bdeaef31ec5277b00448f4d883ad98d9df89e6b237288883066ecc2da`;
- client capture SHA-256:
  `dbc69325ddd2c823a1c8ffb2711515c0b54a81a167b36756bc2e186a284f11b7`;
- device capture SHA-256:
  `8e0f48f3a0ecba02350fbd76a947fd25054ceb0a107fab1a3d4326777dc279a6`;
- compact allocated bytes: 15,958,016; files: 23.

The compact export retains both receipts, strict loss/recovery/carrier checkpoints, the pair
manifest, authenticated Tor bootstrap/circuit/control evidence, TAP captures and logs, and both
Sandwurm chain records. It omits private writable guest disks. The raw 2.4 GiB root is disposable
after compact verification.

## Limits and next gate

Both publisher authority sessions stayed native, and the two device-side workers share one device
Tor process. This cell does not establish per-source Tor circuits, independent network bottlenecks,
anonymity, transparent same-job continuation, byte-prefix resume, same-source striping, or a
throughput win. ADR 0262 subsequently qualifies bounded two-object scheduling on one source/session;
comparative lane-count science and same-source route/byte striping remain open. Safety and
attribution must remain stronger than any performance claim.
