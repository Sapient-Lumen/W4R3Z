# Sandwurm repeated bounded-range carrier-loss evidence

Date: 2026-08-29

Status: accepted direct-UDP and forced-TCP qualification

## Claim

Two simultaneous source-linked IoTox guests continued one signed native `available`-policy range
through two sequential authenticated auxiliary-carrier deaths. The client preserved and resumed an
exact private prefix at both handoffs, used three fresh attempt/FileId identities, fenced both stale
terminal generations, recovered both stopped savedata identities, and converged on the exact signed
artifact. Direct UDP and forced TCP passed with one identical production binary.

## Fixture and acceptance

The client first pulls and explicitly activates a deterministic 4,194,304-byte generation-1 basis.
Generation 2 changes one aligned 1,048,576-byte region. It reuses 3,145,728 verified bytes and
fetches one 1,048,576-byte range under a 786,496-byte manifest.

The default-off laboratory controls select only that concrete range and permit exactly two faults:

```text
--qualify-route-stop-after-bytes 262144
--qualify-route-stop-file-bytes 1048576
--qualify-route-stop-count 2
```

After the first loss, a bounded qualification-only request hold waits for the exact stopped worker
identity to recover before releasing the reassigned request. This removes the completion/recovery
timing race while leaving ordinary product and one-fault paths unchanged. The range path is shaped
at 256 kbit/s. Acceptance requires exactly two qualification faults, losses, reassignments, stale
terminals, recoveries, prefix retentions/resumptions, and aggregate worker restarts; cumulative
retained/resumed equality; zero discard/fallback; an empty qualification queue with one release;
final-carrier equality with the initially stopped carrier; full artifact verification; signed HEAD
acceptance last; and explicit activation.

## Accepted cells

| Route | Source revision | Compact proof | Last fault | Retained = resumed | Pair span |
|---|---|---|---:|---:|---:|
| direct UDP | `8a71517711c92e835b5bbcb8314082102d0d5f4b` | `.sandwurm/exports/pairs/pair.le38qcl5` | 278,313 | 542,916 | 470,693,993,820 ns |
| forced TCP | `935a39a423a04b5b651575a48e3f91f4fcad721a` | `.sandwurm/exports/pairs/pair.8u14ddcy` | 289,281 | 564,852 | 601,510,872,772 ns |

Both cells report product revision `rev0045`, binary SHA-256
`88093a006d9a9e0bedb7af6be5ed3efb47399279a289c7b7c44eb86748257bca`, two retained and resumed
attempts, zero final retained partials, zero discarded bytes, zero fallback, zero deferred frames,
and one deferred-frame release. Their common final identities are:

- artifact SHA-256: `a9c0a0a26d2c01cf541e0d959cf3e8bed2f4aefcafaa713b5d1c104903a7a715`;
- manifest SHA-256: `575e41d269c20e5669d7d873999a9e7fdaf455eac3420f41e2b1b94273d7db93`;
- signed HEAD record: `d33125d9c857dfc7ddb855e093e2768312c6f1a1aeba5ee1ffc8d8c7988fd253`.

The direct client/device receipt digests are
`ef81bad72ca108c6c88bb71aaed45ed65e83a8519fd57b63c33709df01551c30` and
`ecc48100122150327fe6b001cf624ed6eeb673ece46bf1fc12ada11bbee188da`.
The forced-TCP digests are
`44b2482be3eab272c59217f67b900472dcb84ff9968258252f2a6a4e3f98070b` and
`2d38003be950ebcaabf109dbb345d903511dc8638c723f207b4504a1b651fe52`.

Each compact root allocates 163,840 bytes and independently passes strict verification. Direct
pair-manifest/compact-export SHA-256 values are
`ce0eac4a38bfe20496bcad6e10bcf65af9431189c2183bd0cb3240905b906e13` and
`4ca6e51db6bee3c0b76e0a174edad83a9f48bc12669ade50b5b651077d27eb90`.
Forced-TCP values are
`e40912df4cb735b5e279a8a8ad0f9ccb7ec59bb05ed552dcd04aea3dc671b513` and
`f3c377bbf9eae2088f988588533f0c98d7e240a29b00cc9aed1503d8c7429c3c`.

## Scientific corrections retained

An attempted host packet-size classifier was rejected: shaping the selected transfer could also
starve status observations until continuous data completed. The accepted gate instead uses an exact
protocol-semantic recovery barrier visible in content-free counters. Earlier diagnostic roots also
found and fixed a guest shell assignment that executed a numeric restart count as a command, and a
compound topology predicate that failed to terminate after otherwise valid postconditions. No
acceptance claim was drawn from those roots.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp \
  sync-file-range-repeated-route-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp \
  sync-file-range-repeated-route-loss

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.le38qcl5 sync-file-range-repeated-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.8u14ddcy sync-file-range-repeated-route-loss
```

The raw accepted roots were removed only after compact export and independent strict verification.
The compact forms retain manifests, launch/chain commitments, content-free pair receipts, and the
mid-flight progress/final postcondition checkpoints; they contain no guest disk or injected secret.

## Exact nonclaims

This evidence does not prove three-or-more or very-late faults, process/guest restart continuation,
primary disconnect recovery, explicit-new-job prefix reuse, fail-closed or cross-route-class
migration, I2P/Tor continuation, concurrent multi-source striping, randomized timing, two physical
hosts, performance improvement, or automatic activation. The qualification-only request hold is not
an advertised product scheduling behavior.
