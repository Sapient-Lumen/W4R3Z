# Sandwurm concurrent multi-route cancellation evidence

Date: 2026-08-25

Status: accepted Gate 4 bounded concurrent-cancellation qualification; larger common-link
interference remains open

## Claim

Two simultaneous source-linked IoTox guests each used one signed protected primary and two
separately keyed, reciprocally authenticated eight-work-unit bulk workers. The subscriber admitted
eight independent two-object tree pulls under the adaptive selector. The normalized carrier pattern
was `01010101`. Four selected jobs—two on each bulk route—were then withdrawn through four
simultaneous ordinary `sync-cancel` clients.

All four withdrawals reached terminal `cancelled` without carrier or worker drift. The four
untargeted jobs continued to exact two-object commit and explicit activation. Cancelled namespaces
retained no accepted HEAD, activation, or staging file; survivor staging was empty; both routes
remained ready; total signed work drained from 16 to zero; and the coordinator recorded eight
adaptive selections with no reassignment. The same guests then completed 40 protected-primary Ratox
samples with no render at or above 250 ms.

## Accepted compact cells

| Route | Compact proof | Artifact / job | Cancel tail | Pattern | Cancelled per route | Survivors / activations | Ratox p95 / max | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---:|---:|---|---:|---:|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.2laq038h` | 262,211 bytes | 150 ms | `01010101` | 2 / 2 | 4 / 4 | 23.560 / 61.504 ms | 404,767,662,555 ns | `78c18152936712a795b8ff9cce6885519bdc37ae302ea08387dcb3f3a259f89d` | `9ffadbeb684075a4622093c97ce9ae7fab8c300a874ce8aea49d69f4c6aa27c3` |
| forced TCP | `.sandwurm/exports/pairs/pair.rlpuyjth` | 262,211 bytes | 100 ms | `01010101` | 2 / 2 | 4 / 4 | 98.842 / 109.273 ms | 504,770,572,881 ns | `44d0ffb7b9c27a10692e93ea4b1f1883c367044e8d84cc36ec697bdac25fe535` | `b779679303513df33fb56f34b9917915f0b772b8bc9a4f341580bdcd7bdbc37c` |

Each compact export allocates 245,760 bytes and excludes guest disks, identities, bootstrap secrets,
mutable runtime state, FileIds, paths, and content. Both bind source revision
`da38cfad98245928528a5d94528a74beaf959116-dirty`, rev0039, c-toxcore 0.2.23 with
`iotox-file-rr1`, and binary
`1eb2c2cb71300252147de3da3d1a62d6d07231636f3bc2556ffa09292ae2920b`.

The direct-UDP client/device receipt hashes are
`7853108c5607a707e2dcb4b350aa173e25dd957e6210ca3a4cbd01f912eb823c` and
`e0e69ec08981c9992a71bbb4cfa4822f090b1cc9ebce64a99322dddf85418ea1`.
The forced-TCP hashes are
`9fb9367bde4e97dca277a7896bf2b18b25ea926cb0a4823798c8a0e0afd4f849` and
`b787cbaac9b7023dd484d42d92e794bb9fc04d5c0699b57d19e8bccf4b5f5df9`.

## Resource observations

| Route | Interval | CPU ticks (user + system) | `VmHWM` start → end | Descriptor start → end | Context switches (voluntary + involuntary) | Major faults | Bytes written | Transport iterations |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| direct UDP | 9.575 s | 29 + 43 | 15,168 → 15,552 KiB | 36 → 36 | 473 + 2 | 0 | 10,043,392 | 483 |
| forced TCP | 4.550 s | 22 + 31 | 14,976 → 15,488 KiB | 36 → 36 | 224 + 0 | 0 | 8,568,832 | 238 |

The exact TSVs are digest-bound compact-proof members. `VmHWM` is a process-lifetime high-water
mark, not an interval working-set measurement. The interval contains admission, cancellation,
survivor convergence, activation, and final drain; it is not cancellation-handler-only attribution.

## The 1 MiB/job negative cell

Before freezing the accepted bound, two direct-UDP instrumented cells used eight 1,048,643-byte
artifacts on the same 4 Mbit client-TAP shaping contract. Both completed the cancellation science:
pattern `01010101`, four balanced terminal cancellations in 70 ms and 140 ms, four survivor
activations, work 16-to-zero, and no reassignment. Both then missed the five-second receive deadline
for the first protected Ratox `OPENED` response.

A read-only stopped-device inspection localized the failure below IoTox's owner-command scheduler.
The device had created one live Ratox session and running helper; all three sensitive lossless calls
had been accepted; maximum interactive scheduler wait was 24 microseconds; no file transfer or
route work remained. Because all logical routes share the same shaped TAP/NIC queue, the evidence is
consistent with residual common-link FIFO queueing. That diagnosis is an inference, not a
packet-level proof. It establishes that a protected logical route is not, by itself, physical QoS.

The accepted cell therefore uses a 262,144-byte payload per job. This is large enough to keep all
eight jobs live through sequential pull admission and exercise four real concurrent withdrawals,
while leaving larger common-link interference to its own gate. The controller now also requires
three consecutive local observations of the remote Ratox capability, authority, and carrier before
issuing `OPEN`; this closes a distinct asymmetric readiness race and does not extend the five-second
terminal deadline.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-concurrent-cancel
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-concurrent-cancel

./tools/iotox-sandwurm-lab.sh export-pair .sandwurm/lab/pairs/PAIR
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.2laq038h \
  sync-tree-route-concurrent-cancel
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.rlpuyjth \
  sync-tree-route-concurrent-cancel
```

The verifier binds two ready bulk routes on both roles, the exact artifact bound, eight adaptive
decisions, exact normalized pattern, two cancelled jobs per route, four terminal withdrawals, four
survivor activations, zero reassignment/work/staging, resource-file digest, both native carrier
classes, all Ratox rows, exact receipt hashes, and every compact-file digest.

## Exact nonclaims

This is one bounded cancellation cell per carrier. It does not qualify 1 MiB/job protected latency,
cancellation during route loss, randomized cancel selection/timing, larger-object fair sharing,
physical queue isolation, DSCP or socket priority, independent relays, multi-source download, byte
striping, live migration, or long-running fleet policy. ADR 0174 freezes this interpretation.
