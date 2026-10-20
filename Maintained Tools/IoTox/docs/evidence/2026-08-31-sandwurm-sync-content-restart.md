# Sandwurm multi-lane content restart — 2026-08-31

## Claim

Two independent source-linked Sandwurm guests pass an unclean subscriber-daemon restart while exact
content-v2 caps two and four have several immutable-object receives live. The complete matrix passes
over observed direct UDP and forced TCP. Each run preserves only verified complete CAS objects,
removes c-toxcore transport-owned staging residue, fences the old signed attempt set, re-establishes
authority in both directions, and converges plus explicitly activates only through a distinct fresh
pull.

This is not partial-byte resume. It is a strict durable-object/fresh-job restart contract.

## Frozen construction

Every cell uses the reused immutable private test-key baseline and the same source-linked IoTox
binary. The publisher generates artifact SHA-256
`6d85b492f8385941c8af029d21d2e9783df212550046f4dc1f4f397936934e5f`, exactly
8,388,608 bytes, 24 high-entropy chunks, one manifest page, and 26 physical content objects. The
namespace signs `maximum-lanes` and `maximum-outstanding-requests` to the scenario cap; the client
process uses the same exact ceiling. Root discovery remains one serial lane.

The live checkpoint requires an active job with exactly cap non-root lane rows, all admitted, one
source, distinct request IDs and FileIds, and two through cap exact private transport temporaries
with positive bytes. The host then sends `SIGKILL` only to the client IoTox process. Publisher,
guest, bootstrap fixture, and TAPs stay live.

At the crash boundary:

- `CTA1` exists and is signed;
- accepted HEAD and activation are absent;
- canonical content partials are zero;
- exact transport temporaries and their aggregate bytes are recorded; and
- every complete CAS file is rehashed into a sorted inventory commitment.

Startup must reproduce that complete inventory exactly, commit zero additional objects, remove all
exact transport temporaries, leave zero canonical partials, and clear/fence old active attempts. A
host barrier releases the replacement pull only after the publisher and subscriber independently
observe the recovered authorized session. The replacement job ID must differ from the interrupted
job ID.

## Invocation and replay

```sh
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-restart-cap-2
./tools/iotox-sandwurm-lab.sh up-pair \
  direct-udp sync-content-restart-cap-4
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-restart-cap-2
./tools/iotox-sandwurm-lab.sh up-pair \
  forced-tcp sync-content-restart-cap-4

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.8j7v2irm sync-content-restart-cap-2
./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.9q9hsx40 sync-content-restart-cap-4
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.8ulddb9t sync-content-restart-cap-2
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.ol5goyug sync-content-restart-cap-4
```

Each compact root contains 11 secret-free files, allocates 180,224 bytes, and independently returns
`status=passed`. All four bind binary SHA-256
`531dfb224e133b3fc0735455f1a5d077c02dbf6a6c2a91b0e0d85f766321d5b6`.

## Exact restart observations

| Proof | Route | Cap | Lane-set SHA-256 | Transport files/bytes | First job | Second job |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| `pair.8j7v2irm` | UDP | 2 | `72764420beaaf72fe81b85fb5c88bf713226c7ece22948a530125bff3623a531` | 2 / 219,360 | 3286988830952371647 | 15825641667615943920 |
| `pair.9q9hsx40` | UDP | 4 | `ea69a78a67b9bf6e309855b2decee285c34c4802a7d166cd14b8a21d1aab1335` | 4 / 356,460 | 9332066832300386041 | 16504223831534933649 |
| `pair.8ulddb9t` | TCP | 2 | `6e787ad5404020b003a9d17de54a5acdc704bf78ec8e7e9edc9e083da3fc7ef1` | 2 / 204,279 | 16421115767339188272 | 13305916070886629055 |
| `pair.ol5goyug` | TCP | 4 | `6c7b2fdb72bf2883ff5100ade161e0fcae7860265f596e9aec494e986460931b` | 4 / 311,217 | 6857613268926155544 | 14986451225914423607 |

Every crash inventory contains exactly two verified objects totaling 1,328 bytes and hashes to
`a77184f53e12f91e9790d5e16ec84ca5147bcae1c8f6f8cadceba17d1ae08a07`. Every
post-start inventory has the same object count, byte count, and digest, with recovery delta zero.
Every post-start transport-file and canonical-partial count is zero. All final completions bind 24
chunks, one page, 26 objects, signed HEAD-last acceptance, and explicit activation.

## Compact bindings

| Proof | Client receipt SHA-256 | Device receipt SHA-256 | Pair manifest SHA-256 | Compact export SHA-256 |
| --- | --- | --- | --- | --- |
| `pair.8j7v2irm` | `730f00fc055ff4bb1fbe4816f250c669189a29bdb917f9d95297a8c96ad84ba6` | `0f9363569bc0ac04c1637c7e0fd51fab1a9f95eb9bca92e1c2481e7f997eff47` | `9ee04e774421e0d9c460abb19ee48f407c5e775c5accb7e879ec0bc2999d7902` | `645495a98f5c31e278669d4e98e9e9379135217ed440e115a0c775b5d77bff6d` |
| `pair.9q9hsx40` | `512216546c1e774330fa1e3b7c19fd4f6f8c8c66990bc666809181e3422bc401` | `53af3db8265eccaed5991fea4006689272e5dfcf8db268c8358d6b0b2d6892bb` | `be285d5c8b176756b1bc5b6c54eb933722734138308e1e10e43e64b6a8938e77` | `5e41b85cbc8ce17921e8a695a920f53a52bc4d66a9cefe9667e93c3336540cda` |
| `pair.8ulddb9t` | `a202a0361ba450106b0edeed69f72f6111323cb33e768f5976b5079fe29f985d` | `6bcc17fc704b6139555e72487db4f7609db238cfde014681328f90b9cbe16955` | `f468ffb68806c0a3c844453b61d5d9bc42354d111deafa84f668781ad39570e3` | `02d4da7af340fb59d0cd217d3c1e2cd08dfdeef3e04a5e1fdac0b7077eaabef5` |
| `pair.ol5goyug` | `6c2dc460d2d2175ffc046326f8336d7f211ef05fb6f5964cb6c9f394df1d4390` | `767a56cffaa5758f4894e33a238a74fa56c56ad901c133cf1c266bb0b2c76fcf` | `79c968bcedff7f2a3d76fcfec1cb1266aad3064fe2ad5256ae45e229951a1b0b` | `c622e0839eb258b6576077c29043be0a13f9b7a358ba7b22ca62d8839036a103` |

## Rejected attempts and discoveries

Several pre-acceptance roots did useful falsification work but are not evidence for the claim:

- a zero-filled artifact deduplicated most chunks and could not exercise the intended lane shape;
- separate `files` and scheduler snapshots were not atomic enough to require simultaneous transport
  rows, so the gate moved to one coherent scheduler snapshot plus exact on-disk temporary count;
- the live runs showed that c-toxcore writes `.iotox-...part.part-XXXXXX` files rather than the
  canonical `CTA1` pathname before completion, exposing the orphan-residue product bug fixed by ADR
  0267;
- an inherited flat-v1 admission predicate read the namespace aggregate instead of content-v2 lane
  rows and was removed from this scenario; and
- rejected forced-TCP root `pair.bsx3je60` issued the replacement HEAD request after requester-local
  authorization but before the publisher consumed the reciprocal proof. The publisher returned a
  permission denial as designed. The final harness waits for both independent recovery markers
  before releasing the pull.

No rejected root contributes a measurement or accepted binding above.

## Nonclaims

These four local two-VM cells do not prove a physical power cut, arbitrary filesystem durability,
hostile same-owner safety, a resumable partial object, same-job continuation, Tor/I2P content
restart, Internet behavior, physical-path diversity, same-source auxiliary distribution, byte
striping, or an interactive Ratox SLA. Default lane cap one remains unchanged. See ADR 0267.
