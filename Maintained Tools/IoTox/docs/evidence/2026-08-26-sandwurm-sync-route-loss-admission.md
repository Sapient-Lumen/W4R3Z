# Sandwurm admission-during-route-loss evidence

Date: 2026-08-26

Status: accepted Gate 4 degraded-admission row

## Claim

Two fixed-policy, two-object tree pulls begin on one auxiliary bulk carrier. After positive receive
progress, that exact carrier stops and both existing jobs reassign to the sole ready survivor. Two
additional pulls are then created—not queued before the fault—and both are admitted to that same
survivor while the route inventory reports exactly one ready bulk route. All four revisions commit
and activate, signed work drains from four to zero, stale old-incarnation terminal truth is fenced,
the stopped identity recovers once, and 40 protected Ratox probes remain below 250 ms.

This row also exercises two-phase auxiliary shutdown: synchronous carrier service quiesces while
the ordered event consumer continues draining required toxcore events.

## Accepted compact cells

| Route | Compact proof | Duration | Fault position | Affected / reassigned / late / ready | Stale / recovery / selections / activations / work | Ratox p50 / p95 / max | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.v3qc2kld` | 29,259 ms | 135,729 bytes | 2 / 2 / 2 / 1 | 4 / 1 / 6 / 4 / 4→0 | 15.860 / 19.149 / 19.980 ms | 400,907,193,472 ns | `5e0fc19785eddbb90cfd6141e75c567fc801255ae9f2be7a85626bd40c2712b7` | `17ffd200523b67f016154c84c488d780d755e379a132c5ee4e2db24c9aceb579` |
| forced TCP | `.sandwurm/exports/pairs/pair.djhqe3we` | 94,046 ms | 67,179 bytes | 2 / 2 / 2 / 1 | 4 / 1 / 6 / 4 / 4→0 | 89.293 / 95.741 / 103.416 ms | 682,024,330,461 ns | `6e2d055058db195663e237eff7b779babac5a0fb6323b087c49716c217c74258` | `e87bc17829693d442051cb5dea2fa66df89a4163f0b5517d400829ec87f2548c` |

Each compact export allocates 245,760 bytes. Both bind source revision
`2b56130b22913ee8c369bc7ce6a8a3bd99a72bb0-dirty` and binary
`db64c1eb64ba0896690f12910b5af6fcee85ec66ef6c3fbb133a275d8fac2fbc`.

The direct-UDP client/device receipt hashes are
`d52c2295c511269dd37ea0b046865dbb69d1a5aa1d0546a3500385ebb066bd54` and
`cdf55e17c5b812b05ca5cea9cddbaedc8770823db7e24d4fda19758ab34f4485`.
The forced-TCP hashes are
`6755604f74a1e7de938ee4f327954320ee8cbd63fa61839a2e4c9af0bb1a4d53` and
`ad8d5a9730791d122dbd399abe1547187e29c826e0bd1ef25a56894c5c35f2f1`.

Both cells bind the same 524,355-byte per-job tree artifact family, base content bytes 131,157,
initial carrier pattern `00`, exactly two affected jobs, one carrier loss, two reassignments, two
late admissions, one ready survivor at late admission, six fixed selections, four activations, four
stale terminals, one recovery, and work four-to-zero. The stopped carrier is
`13E3E4EFA78A92E3A1B41AFF31BE596496903F83383566E1BDD15C02BE7ADC10`; the observed survivor is
`478CD68E0D2035CD1B63CC07558070EBEA7897DAB135896115BB85B524E23C1A`.
Resource-interval digests are
`fcae802f501a08a6526098540ddd70b1d9df9371ebd765990ee6359568bce180` for UDP and
`f4f28d228acec6deb0918a9a4b0b5d7afa4b7966c0b079adee342ac6b65f5267` for TCP.

The corrected source passes the ordinary 30-entry CTest lane, the complete 45-entry Clang
ASan+UBSan lane, and the complete 45-entry GCC ThreadSanitizer lane. The five private-cgroup tests
remain named capability skips where the construction environment lacks a writable delegated
cgroup-v2/PSI hierarchy; no sanitizer or race diagnostic was reported.

## Rejected observations that selected the fix

- Direct-UDP `pair.jqtdnaxq` reached `phase=base-complete` and then stopped advancing during the
  clean same-state Agent restart. The event consumer had exited before synchronous carrier service
  returned. It selected the two-phase carrier-first quiescence order in ADR 0181.
- Direct-UDP `pair.lje21sp5` then completed that shutdown but passed an invalid zero-millisecond
  value to a CLI option whose frozen range is `1..60000`. The daemon rejected it exactly. The
  fixture now uses one millisecond and requires a live correlated status round trip, so a transient
  stale socket cannot conceal startup failure.

Neither root is accepted evidence. Their private guest disks are cleanup candidates after this
content-free interpretation is retained.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-loss-admission
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-loss-admission

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.v3qc2kld \
  sync-tree-route-loss-admission
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.djhqe3we \
  sync-tree-route-loss-admission
python3 tools/verify-sandwurm-pair.py --self-test
```

Each raw root passed strict verification before export. Each compact root passed independently after
export. The compact allowlist retains only content-free receipts, status/counter evidence, Ratox
timestamps, resource intervals, launch chains, and their exact hashes.

## Exact nonclaims

This is one deterministic fixed-policy row with two jobs before loss and two jobs after observed
reassignment, one one-millisecond post-threshold delay, two native carrier classes, and one local
relay topology. The 29.259/94.046-second durations are observations, not a latency distribution or a
UDP/TCP performance guarantee. This does not cold-start the daemon while a route is absent, estimate
failure probabilities, qualify random delay distributions, prove larger-object common-link fairness,
provide physical QoS, distinguish independent relays, or authorize automatic production recovery.
