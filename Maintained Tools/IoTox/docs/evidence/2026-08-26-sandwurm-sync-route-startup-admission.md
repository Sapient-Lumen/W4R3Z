# Sandwurm degraded-route startup admission evidence

Date: 2026-08-26

Status: accepted Gate 4 controlled-startup row

## Claim

After a clean same-state subscriber Agent restart, one exact authenticated auxiliary bulk route is
ready for ten consecutive observations while its peer is held for 20,000 ms. Two new adaptive,
two-object, 16 MiB tree pulls are admitted to that sole route and consume four signed work units.
When the delayed route joins, both jobs are still live and both retain their original carrier. Both
revisions commit and activate, selection remains exactly two with zero reassignment, work drains
four-to-zero, and 40 protected Ratox probes remain below 250 ms.

## Accepted compact cells

| Route | Compact proof | Duration | Ready bulk | Stable | Live / preserved at join | Selections / activations / work | Ratox p50 / p95 / max | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.46f6td4j` | 103,748 ms | 1→2 | 10 | 2 / 2 | 2 / 2 / 4→0 | 14.875 / 22.673 / 23.540 ms | 461,852,247,210 ns | `9f3da60a1cf216242687fe6b890220b42fa0807ccf2b24b7890f365fdd6e67ea` | `d35412e81f3d780284bf6ea98087a946e599cd1d1edd9fdb412b967b4e66fc96` |
| forced TCP | `.sandwurm/exports/pairs/pair.2gvkqs6b` | 126,919 ms | 1→2 | 10 | 2 / 2 | 2 / 2 / 4→0 | 92.317 / 102.257 / 129.184 ms | 542,474,335,703 ns | `c60fe329f8a935824375d29d6101a8d16539f443f733c7ed552019855e5d2c8a` | `5dd550e9d4bdf9c571a867033fb946760a1f265daf12e5e210b5e033077a14da` |

Each compact export allocates 249,856 bytes. Both bind source revision
`d255fdddf86c6f4dad8371cc1f5b0f10990b7db7-dirty`, binary
`db64c1eb64ba0896690f12910b5af6fcee85ec66ef6c3fbb133a275d8fac2fbc`, the same
16,777,283-byte per-job artifact family, a 20,000 ms hold, one clean subscriber restart, two jobs,
two adaptive selections, two activations, and zero reassignment.

The direct-UDP client/device receipt hashes are
`235973ce6cce498e37e2f3096de35351faf1c73be20dd85dfc37508c0ca6648c` and
`a63cf451c4626a5c871f4c2889ecbe8905e494bebf593b87ea3f3f5c2be67131`.
The forced-TCP hashes are
`2a111cfd1549ea3adb6207aa4d24668c984f654de7f3ad5961fe12a9e2fb52b6` and
`0a116fdcec4189920a6125730fa4b11acc9a711eab8a4bedf87abcb1d153c416`.
Resource-interval digests are
`e4c52d97688521bbd519003b7687e366491e5ab25344df25b75d60f350567c99` for UDP and
`ff89645a4ed383136000ddbf3d2eba46219423f9e5db26876767e7233424d9ff` for TCP. During those
intervals the client process high-water resident set reached 17,024 KiB and 17,196 KiB,
respectively; those are observations, not enforced ceilings.

## Rejected observation

The first direct-UDP fixture root `pair.gfm0c268` reached the new restart dispatcher and failed
under `set -u` before route admission because the Sandwurm route-worker array is deliberately
one-indexed while the new branch selected index zero. The fixture now names `route_worker_key[1]`.
This rejected root supports no protocol claim. A following launch root, `pair.namvo3gh`, never
started a guest because the manually interrupted prior runner left its local bootstrap fixture
holding port 33445; it likewise supports no product claim.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-startup-admission
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-startup-admission

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.46f6td4j \
  sync-tree-route-startup-admission
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.2gvkqs6b \
  sync-tree-route-startup-admission
python3 tools/verify-sandwurm-pair.py --self-test
```

Each raw root passed strict verification before export. Each compact root passed independently
after export. The compact allowlist retains only content-free receipts, launch chains, route and
Ratox status/timestamps, process-resource intervals, and their exact hashes.

## Exact nonclaims

The readiness hold begins after a clean restart of the IoTox Agent inside an already-running guest
and preserves the signed route inventory. It deterministically delays one application-ready route;
it does not remove a physical interface, stop an independent relay, reboot either VM, or boot the
machine with a path absent. The 103.748/126.919-second values are single-cell observations, not UDP
versus TCP throughput distributions. This row does not qualify random delay distributions,
startup concurrent with a route fault, more-worker partial orders, common-link priority, relay
diversity, or automatic production recovery.
