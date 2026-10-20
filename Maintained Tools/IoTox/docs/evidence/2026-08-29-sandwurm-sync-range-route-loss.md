# Sandwurm bounded-range carrier-loss resume evidence

Date: 2026-08-29

Status: accepted direct-UDP and forced-TCP qualification

## Claim

Two simultaneous source-linked IoTox guests retained one exact private prefix of a live bounded
range after its authenticated auxiliary carrier was stopped, reassigned the unchanged signed job to
the other ready native carrier under fresh attempt and FileId identities, received only the suffix,
and converged on the exact signed artifact. Direct UDP and forced TCP passed with the same binary.

This is `available`-policy, same-process, same-job continuation. It does not change fail-closed I2P
loss semantics.

## Fixture and acceptance

Each client first pulls and explicitly activates a deterministic 4,194,304-byte generation-1 basis.
The publisher changes one aligned 1,048,576-byte region and publishes parent-linked generation 2.
The successor uses one 786,496-byte range manifest, reuses 3,145,728 verified basis bytes, and needs
one exact 1,048,576-byte range bundle.

The client Agent starts with two authenticated native bulk workers and the default-off fault seam:

```text
--qualify-route-stop-after-bytes 262144
--qualify-route-stop-file-bytes 1048576
```

The exact-size selector prevents the 4 MiB basis or either manifest from consuming the one-shot
fault. The gate requires a concrete range lane and captures its attempt/carrier before loss. After
loss it requires a distinct attempt and carrier, exact positive retained/resumed equality, no range
retry, no discard or retention fallback, one stale terminal fence, one carrier reassignment, full
route recovery, final artifact verification, HEAD-last acceptance, and explicit activation.

## Accepted cells

Both cells use source revision `21c9814af7e59ddf9699fa909928403ecf5808ef`, product revision
`rev0045`, and binary SHA-256
`e79a4388fc967b082ff743bf62bf49483688af3546afbd44f777afedc40bd82e`.

| Route | Compact proof | Fault position | Retained | Resumed | Discarded | Fallbacks | Span |
|---|---|---:|---:|---:|---:|---:|---:|
| direct UDP | `.sandwurm/exports/pairs/pair.urbhf0je` | 283,797 | 283,797 | 283,797 | 0 | 0 | 422,150,781,688 ns |
| forced TCP | `.sandwurm/exports/pairs/pair.n76biwao` | 293,394 | 293,394 | 293,394 | 0 | 0 | 495,698,530,166 ns |

Each client receipt additionally records one carrier loss, one reassignment, one stale terminal, one
recovery, one stopped-worker restart, two logical objects requested and committed, zero range
retries, one 1 MiB fetched range, and 3 MiB verified basis reuse. Both roles bind the same generation
2 identities:

- artifact SHA-256: `a9c0a0a26d2c01cf541e0d959cf3e8bed2f4aefcafaa713b5d1c104903a7a715`;
- manifest SHA-256: `575e41d269c20e5669d7d873999a9e7fdaf455eac3420f41e2b1b94273d7db93`;
- signed HEAD record: `d33125d9c857dfc7ddb855e093e2768312c6f1a1aeba5ee1ffc8d8c7988fd253`.

The compact roots allocate 155,648 bytes each and independently pass strict verification. UDP
pair-manifest/compact-export SHA-256 values are
`2120373bce52fe31ee3e395239541ba5a8a65175addfa87c496c2631efc502aa` and
`38c2d9bab7e01d1536c25704d765b936a1c4e97a12d0a7854a660db1cf473185`.
TCP values are `5749a9a2469c8c646e4b921ebda53281753754882c25b213edd52414cadf88f4` and
`16e249a02a05b36761a5164ffd2cb83d8a1825cadc8d3e4679f97625b27979da`.

## Rejected scientific run

Initial direct-UDP root `pair.k65z1d2x` armed the generic 256 KiB fault only after restarting the
client. Generation 2 still had to fetch its 786,496-byte manifest first, so that prerequisite was
eligible to consume the fault; the host timed out without a bounded-range convergence marker. No
range-prefix claim is drawn from it. The exact-size selector was added, the restart removed, and
both accepted cells above prove that the 1 MiB range itself is the faulted transfer.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-range-route-loss
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-range-route-loss

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.urbhf0je sync-file-range-route-loss
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.n76biwao sync-file-range-route-loss
```

The accepted raw roots and rejected diagnostic root were removed only after both compact roots
independently reverified. They are recoverable from an external machine snapshot or by rerunning the
fixture; no accepted claim depends on private guest disks.

## Exact nonclaims

This evidence does not prove same-handle continuation, daemon/guest restart continuation, primary
disconnect recovery, explicit-fresh-job prefix reuse, fail-closed or cross-route-class migration,
I2P/Tor continuation, concurrent multi-source striping, repeated loss, randomized fault timing,
two-physical-host behavior, performance improvement, or automatic activation.
