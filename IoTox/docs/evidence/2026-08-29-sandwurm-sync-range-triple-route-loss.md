# Sandwurm three-loss bounded-range continuation evidence

Date: 2026-08-29

Status: accepted direct-UDP and forced-TCP qualification

## Claim

Two simultaneous source-linked IoTox guests continued one signed native `available`-policy range
through three sequential authenticated auxiliary-carrier deaths. The subscriber preserved and
resumed an exact private prefix at every handoff, fenced every stale terminal generation, recovered
each stopped identity, exhausted one route's signed two-restart budget without losing readiness,
and converged on the exact signed artifact. Direct UDP and forced TCP passed with one identical
production binary.

## Fixture and acceptance

The subscriber first pulls and explicitly activates a deterministic 4,194,304-byte generation-1
basis. Generation 2 changes one aligned 1,048,576-byte region, reuses 3,145,728 verified bytes, and
fetches that one range under the exact 786,496-byte manifest.

The default-off laboratory controls select only that concrete range and permit exactly three
faults:

```text
--qualify-route-stop-after-bytes 262144
--qualify-route-stop-file-bytes 1048576
--qualify-route-stop-count 3
```

The selected range is shaped at 256 kbit/s. After losses one and two, a bounded qualification-only
request hold waits for the exact stopped worker identity to recover before releasing the reassigned
request. Only this named cell gives both signed bulk members a two-restart budget and admits the
five scheduler-attempt records needed by one manifest plus four range incarnations. Ordinary
product scheduling, framing, authority, and one-fault behavior are unchanged.

Acceptance requires exactly three qualification faults, carrier losses, reassignments, stale
terminals, recoveries, retained attempts, resumed attempts, and aggregate worker restarts. Retained
and resumed byte totals must match, discard/fallback/final partials/range retries must remain zero,
and the bounded hold queue must finish empty after exactly two releases. Attempts must advance from
4 through 7; the final carrier must differ from the initially stopped carrier; that stopped route
must finish ready at `restarts=2 restart-budget=2 restart-budget-remaining=0`; both bulk routes must
remain ready; full artifact verification and signed-HEAD-last acceptance must precede explicit
activation.

## Accepted cells

| Route | Source revision | Compact proof | Last fault | Retained = resumed | Pair span |
|---|---|---|---:|---:|---:|
| direct UDP | `461adf54e2f16b9c531d4af5aaf52a62e08c6a34` | `.sandwurm/exports/pairs/pair.3iufekzy` | 301,620 | 862,359 | 415,242,179,509 ns |
| forced TCP | `461adf54e2f16b9c531d4af5aaf52a62e08c6a34` | `.sandwurm/exports/pairs/pair.zleebk2k` | 304,362 | 871,956 | 444,238,694,013 ns |

Both cells report product revision `rev0045`, binary SHA-256
`294655ac8990967b822a92593f31f2f6d73ab22c40330b7323e60f9e5d6613c3`, attempts 4 through 7,
three complete lifecycle events, zero final retained partials, zero discarded bytes, zero fallback,
zero deferred frames, and two deferred-frame releases. Their common final identities are:

- artifact SHA-256: `a9c0a0a26d2c01cf541e0d959cf3e8bed2f4aefcafaa713b5d1c104903a7a715`;
- manifest SHA-256: `575e41d269c20e5669d7d873999a9e7fdaf455eac3420f41e2b1b94273d7db93`;
- signed HEAD record: `d33125d9c857dfc7ddb855e093e2768312c6f1a1aeba5ee1ffc8d8c7988fd253`.

The direct client/device receipt digests are
`1ea811ec2a78859ddfe241410c359d7e8a85ae88e00817a926857cbaf0dd78df` and
`61297a26b3cc567b7901b91b302acfd4b8973c46020b32d44f619e7b645f259e`.
The forced-TCP digests are
`c7e3618ffd0981b0daa0e73c2d995a81680c2e73bc3d514284d7a828bc0fc682` and
`e29e2fa7be49afd9f2036b47703ea48d5d37ee7eaaae6f1597fa7ccd36219638`.

Each compact root allocates 176,128 bytes and independently passes strict verification. Direct
pair-manifest/compact-export SHA-256 values are
`9865f3cfd9ff3cbfb44edfcacfa0fa49eef60c97a81e4150e68547e40e9f2f50` and
`3ef0d412c69885a2c748f412541410d936e354ccf94f3537f2a5ade6f2928a61`.
Forced-TCP values are
`8ff45ec2d24247d7cd353f5e983c42c67c20c10ab7be3cacd940312de5807c1e` and
`90e01b0815b53632e22752294cb544f594e032b4882e3019ceccfaaf7ad15f18`.

## Scientific corrections retained

Rejected diagnostics successively exposed the inherited restart/deadline ceiling, a missed
recovery-level rearm, an application handshake enqueue/observation race, a hidden four-record
scheduler fence ceiling, and ambiguity between signed restart policy and remaining capacity. ADRs
0236 through 0238 close the last three without changing wire or authority formats. A later baseline
stall occurred before the fault gate despite complete artifact bytes on stopped-disk inspection;
the triple fixture now emits content-free live status/routes snapshots on bounded baseline failure.
Successful runs remove those transient baseline snapshots. None of the diagnostic roots is
acceptance evidence.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-file-range-triple-route-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-file-range-triple-route-loss

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.3iufekzy sync-file-range-triple-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.zleebk2k sync-file-range-triple-route-loss
```

The raw accepted roots are removable only after compact export and independent strict
verification. The compact forms retain manifests, launch/chain commitments, content-free pair
receipts, and progress/final-postcondition checkpoints; they contain no guest disk or injected
secret.

## Exact nonclaims

This evidence does not prove four-plus losses, repeated late or final-chunk races, randomized fault
timing, daemon/guest restart continuation of a range, I2P/Tor continuation, concurrent multi-source
striping, two physical hosts, performance improvement, or automatic activation. The
qualification-only request hold is not an advertised product scheduling behavior.
