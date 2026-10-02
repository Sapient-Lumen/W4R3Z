# Sandwurm eight-job route-population-loss evidence

Date: 2026-08-26

Status: accepted Gate 4 multi-job same-carrier loss row

## Claim

Eight independent signed tree pulls fill two auxiliary routes under fixed selection. One exact route
is stopped only after positive aggregate receive progress and a 750 ms hold. The four nonterminal
jobs assigned to it are remembered explicitly, fenced, and reassigned as complete remaining
two-object work sets. All eight revisions commit and activate, stale old-worker terminals cannot
change truth, signed work drains from 16 to zero, the stopped savedata identity recovers once, and a
40-sample protected Ratox probe remains below 250 ms.

This row exercises the corrected full-work selector, bounded transient unavailable-result retry, and
the split auxiliary event/carrier service architecture in one genuine two-guest campaign.

## Accepted compact cells

| Route | Compact proof | Duration | Fault position | Affected / loss / reassignment / stale / recovery | Fixed selections / activations / work | Ratox p50 / p95 / max | Whole-VM span | Pair manifest SHA-256 | Compact index SHA-256 |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.j19_uhjj` | 39,681 ms | 152,181 bytes | 4 / 1 / 4 / 4 / 1 | 12 / 8 / 16→0 | 13.722 / 19.471 / 26.792 ms | 548,897,409,561 ns | `abc63a7a50c796ea245e13adfcba109911467c6c8e19ba04f440e27cb5bf213e` | `eee7961152af3673c67e4e77c7b08dadeaaa5d09484ad8db72cd03e0264dcc68` |
| forced TCP | `.sandwurm/exports/pairs/pair.rfnsjtqb` | 42,322 ms | 122,019 bytes | 4 / 1 / 4 / 8 / 1 | 12 / 8 / 16→0 | 102.749 / 143.370 / 156.251 ms | 1,007,797,616,669 ns | `4027b922dce94e3643459a10f791ec725c3ee0d2099ed2df813ae3a9154e9de8` | `5b00b37dd8e7e093a05dfa915800eaee4dbc7521e6706f04225b3b27e349bb85` |

Each compact export allocates 245,760 bytes. Both bind source revision
`ed5f4d8457adbfa84d0f9f685105ae15208f8ccb-dirty`, source manifest
`da574515552e8d08e2ce3029aa5efd8445227cfb42b0f8cf0812c030ae7e3192`, and binary
`b401bbbb34259aeeaaa9b0934aadebff22388c6a1e6713957518520330955ed4`.

The direct-UDP client/device receipt hashes are
`dba08162364d0cac01ac719b13c546ee9ccd09f9fff2fabb5fec0db74bab9361` and
`10ddd8bc008005da84a9e71977059910d518af95a95d594031a495019ff971c4`.
The forced-TCP hashes are
`d36ae408a503d3e2e1674f831f62ec7e504473e8e3bc00cad03e20e3970709ed` and
`a8b4ea4b2c0c8a76c7cdc86a5f30cb700f55fe6056289e04e57ca9136c25f00a`.

Both cells bind the same 524,355-byte tree artifact, content bytes 131,157, artifact digest
`1561fd522b8dae36ba428a6c4a4decb12636bc9118d781ff5f58ff82349baf16`, manifest digest
`0e8cf5710cd6c7145281252f9f9b0c9971d0e0e84d8eba64d011fc6f95b7e2cf`, signed HEAD
`a918fa4320008a845322d396f7169fe2687c268af06f5dbda1af9358a0a709d6`, and initial carrier
pattern `00001111`. Their resource-interval digests are
`37e41578b058d7feba7d064cd8e4933450b70f62fa0660bddc330baafd4354a1` for UDP and
`3448e5df8a87c13d21b1f8866de391375b2b7708e5228c480fb120d8eadfd50a` for TCP. Both primary
Agent status records end with zero required-event backpressure.

The corrected source also passes the ordinary 30-entry CTest lane, the complete 45-entry Clang
ASan+UBSan lane, and the complete 45-entry GCC ThreadSanitizer lane. The five private-cgroup tests
remain named capability skips where the construction environment lacks a writable delegated
cgroup-v2/PSI hierarchy; no sanitizer or race diagnostic was reported.

## Defects exposed before acceptance

The forced-TCP campaign was intentionally not summarized as one green retry.

- One fully converged attempt failed the independent Ratox gate at 263.770 ms. It proved sync
  convergence but did not qualify protected latency.
- Another attempt terminally reported publisher refusal for one migrated immutable object. The
  receiver-signed route capacity had transiently led the provider's outgoing-attempt ledger. This
  selected the bounded fresh message/FileId retry for pre-offer `unavailable` only.
- Repeated attempts then stopped advancing one or more migrated transfers and made local
  `sync-status` wait indefinitely. The auxiliary supervisor was retaining its snapshot mutex while
  its sole event consumer synchronously serviced carrier controls. Splitting event and carrier
  service repaired that liveness dependency without dropping required events.
- Selector inspection found a separate partial-admission defect: replacement eligibility checked
  one work unit for a job that still needed two. The selector now requires the complete remaining
  work set before choosing a route.

These failed raw roots contained private guest disks and were reclaimed after their content-free
outcomes were recorded. They are not accepted evidence and their timing is not averaged into the
passing cells.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-tree-route-population-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-tree-route-population-loss

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.j19_uhjj \
  sync-tree-route-population-loss
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.rfnsjtqb \
  sync-tree-route-population-loss
python3 tools/verify-sandwurm-pair.py --self-test
```

Each raw root passed strict verification before export. Each compact root passed independently after
export. The compact allowlist retains only content-free receipts, status/counter evidence, Ratox
timestamps, resource intervals, launch chains, and their exact hashes.

## Exact nonclaims

This is one deterministic fixed-policy population, one selected four-job carrier loss, one 750 ms
post-progress hold, two native carrier classes, and one local relay topology. It does not estimate a
failure probability, exhaust thread schedules, qualify random delay distributions, start new jobs
during the fault, prove more than two routes, reuse byte prefixes, stripe one object, guarantee
physical queue priority, distinguish independent relays, or authorize automatic production restart.
Larger-object/common-link science and Gate 5 long-running policy remain separate.
