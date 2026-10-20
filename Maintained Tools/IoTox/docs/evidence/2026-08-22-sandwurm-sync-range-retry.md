# Sandwurm synchronization partial-range retry evidence

Date: 2026-08-22

Status: accepted discard baseline plus accepted exact-prefix optimization

## Claim

Two simultaneous source-linked IoTox guests continued one signed successor pull after a deliberate
partial range-transfer failure. The gate passed over observed direct UDP and forced TCP with the same
production binary, revision identities, policy, and authority ordering.

For each carrier, the subscriber first pulled and explicitly activated a deterministic 4 MiB
generation 1. The publisher changed one 1 MiB region to nonzero bytes and published its exact
parent-linked generation 2. The host rate-limited the subscriber TAP to 4 Mbit/s. After the first
incoming range transfer reported a positive position smaller than its size, the guest used the
public `iotox file-control ... cancel` entrance. The subscriber then:

1. removed the first attempt's staging bytes, finished signed active-attempt truth, and fenced its
   scheduler reservation;
2. retained generation 1 as the accepted and activated authority;
3. emitted the identical HEAD-bound range plan under a fresh attempt, message ID, and Tox FileId;
4. fetched the complete 1 MiB range again, reusing 3 MiB only from the verified generation-1 basis;
5. reconstructed and verified the complete generation-2 artifact SHA-256;
6. accepted the signed HEAD last and explicitly activated its exact token.

Both guest receipts agree on the first and second FileIds, discarded byte count, one retry, one
range, reused/fetched byte accounting, and final revision identities.

## Subsequent exact-prefix qualification (2026-08-29)

ADR 0230 preserves ADR 0138's one-retry bound and fresh attempt/message/FileId identities but
supersedes its unconditional byte discard when an exact seek-capable private prefix exists. Initial
range receives now use the canonical attempt inode in place from byte zero. After a local
file-control cancellation, the subscriber revalidates the exact positive prefix, finishes and
fences the old signed attempt, atomically hands the inode to a fresh attempt, and seeks the new Tox
transfer to that byte count before receiving only the suffix.

Both current cells use clean source revision
`93a8a20614a7d69b91180c233920f048bcbec77e` and binary SHA-256
`2d8dc95b6363458b8ecd69fcfc450624f75eaf0317d04e3c053f06850c05e089`:

| Route | Compact proof | Span | Retained bytes | Resumed bytes | Discarded | Fallbacks |
|---|---|---:|---:|---:|---:|---:|
| direct UDP | `.sandwurm/exports/pairs/pair.cj5y5vgt` | 286,693,076,623 ns | 15,081 | 15,081 | 0 | 0 |
| forced TCP | `.sandwurm/exports/pairs/pair.qeb99i4o` | 436,728,451,016 ns | 24,678 | 24,678 | 0 | 0 |

Both converge on the same generation/artifact/manifest/HEAD and 1 MiB fetched plus 3 MiB basis
accounting listed below. The UDP FileId changes from
`c54604d2510db4a9746257e501662c11223e28d85791004d0c463512fe6ad00e` to
`5a55ca88194cebcf645e8e66f105b5458b5a03164a4a8739c0607fdd8963556e`; TCP changes from
`fc1d422e04873b11a04101a55fecfcc32107bb206d7eff2dc3fe65ec520d7963` to
`154fdb3d08b0a310524e5c521c7ae10e276b9154b75d09b2e4fc4f74baa4d938`.
The 155,648-byte compact exports independently pass the strict verifier. Their pair-manifest
SHA-256 values are `87e7164deb7127109c569fe282baab0a4ec4414e094e073a69ccc63130b99746`
and `39e811bfb57a18570eb0d6a85b8380221877accfaee36b2deff3da40b01708b0`;
their compact-export SHA-256 values are
`abbed79524e119609d424b54907ab577a16d0b21e132c9f509a5a67f001a9fc5` and
`2842224406f5a534cce5d509bc6354c05a1732be89a88851ebad8e4546270731`.

## Accepted cells

| Route | Raw private proof | Compact proof | Span | Discarded bytes | Binary SHA-256 |
|---|---|---|---:|---:|---|
| direct UDP | removed after verified compaction | `.sandwurm/exports/pairs/pair.phkpgx90` | 153,251,884,629 ns | 91,857 | `144089849bdc414af7ff56aa51015dcd73bd57b95590a5fe0ab038260bf5015f` |
| forced TCP | removed after verified compaction | `.sandwurm/exports/pairs/pair.4r5xzja_` | 181,651,509,574 ns | 32,904 | `144089849bdc414af7ff56aa51015dcd73bd57b95590a5fe0ab038260bf5015f` |

Both cells converged on:

- generation: `2`;
- artifact bytes: `4,194,304`;
- artifact SHA-256: `a9c0a0a26d2c01cf541e0d959cf3e8bed2f4aefcafaa713b5d1c104903a7a715`;
- manifest SHA-256: `575e41d269c20e5669d7d873999a9e7fdaf455eac3420f41e2b1b94273d7db93`;
- signed HEAD record: `d33125d9c857dfc7ddb855e093e2768312c6f1a1aeba5ee1ffc8d8c7988fd253`;
- range count/reused/final-fetched bytes: `1 / 3,145,728 / 1,048,576`;
- range-observing roles: `2`;
- retry-observing roles: `2`.

The UDP FileId changed from
`493d0b8b79d9445b7fca83016541a346df1d0ceda3ee4befdb366b101586129a` to
`3374e462e50e95732128229c73b01e2f58457de359b3e5e615ba4cdadc050c4d`.
The forced-TCP FileId changed from
`bac97c71ef23f65d7a816096ee30e7e6afd10d8ea9a84dca4bdefc4ffd0ba260` to
`fe53f01548ddca5a52b34908302a98214b5c103ac34d111617f8bff1dfbf46b7`.

The compact UDP and TCP proofs allocate 110,592 bytes each and independently pass the ordinary pair
verifier. Their pair-manifest SHA-256 values are respectively
`d32557c7b8b1a927b7b23c2e96c81a7c188b43e1a84ef37745d8d571ed4d1796` and
`0f2c48916a45fbf8be84ddeab4f77d8759ffa118555261c5bfcb82ce6e42849d`.

## Rejected scientific runs

- Failed run `pair.0bquuywm` did not create generation 2 because the first fixture wrote
  zero bytes over a region that was already zero. The publication correctly remained an exact
  generation-1 duplicate. The fixture now writes `0xa5` bytes and proves a new signed revision.
- Failed run `pair.qy9ytuf0` exposed a product bridge defect: local `file-control cancel`
  removed manager state but did not deliver a terminal event to the sync subscriber. The Agent now
  sends locally initiated cancel truth through the same bounded terminal-work path as toxcore events.
- Failed run `pair.kdrmtave` stopped before synchronization because both forced-TCP guests
  missed v3 authority establishment. No range-retry claim is drawn from it. A clean repeat produced
  the accepted forced-TCP cell above.
- Failed run `pair._zg7bukg` was the first live exact-prefix qualification from commit `772655b`.
  It completed the retry safely but reported zero resumed bytes: the initial range still used the
  transport's publish-on-completion temporary inode, so no exact canonical attempt prefix existed to
  hand off. The subscriber correctly fell back to discard. Commit `93a8a20` moves initial
  seek-capable range receives into the canonical empty attempt inode and adds deterministic
  receive-ceiling deferral coverage before the two accepted current cells.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-file-range-retry
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-file-range-retry

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.phkpgx90 \
  --route direct-udp --scenario sync-file-range-retry
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.4r5xzja_ \
  --route forced-tcp --scenario sync-file-range-retry
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.cj5y5vgt \
  --route direct-udp --scenario sync-file-range-retry
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.qeb99i4o \
  --route forced-tcp --scenario sync-file-range-retry
```

The two accepted raw roots were removed after their compact proofs independently reverified. The
three rejected raw roots were removed after the defects and exact nonclaims above were recorded; no
claim depended on their private disks. All raw cells are recoverable only by rerunning their fixture.

After the current compact roots independently reverified, guarded cleanup removed exactly raw
`pair._zg7bukg`, `pair.cj5y5vgt`, and `pair.qeb99i4o`, reclaiming 6.9 GiB. A second dry-run reported
zero candidates, and both compact proofs reverified again. The raw private disks are now recoverable
only from an external machine snapshot or by rerunning the fixtures; no accepted claim depends on
them.

## Exact nonclaims

The original cells prove the safe full-discard baseline. The subsequent cells prove one bounded
same-process, same-job, same-carrier, same-authenticated-epoch retry of an unchanged plan using one
strict prefix under fresh attempt/message/FileId identities. They do not resume a Tox handle, move
this retry across carriers, reuse it for an explicit fresh job, survive daemon/guest restart or
disconnect, retry indefinitely, combine sources, repair
corrupt target objects, prove power-loss/filesystem-fault behavior, enable automatic activation, or
prove two-physical-host behavior. ADR 0231 separately qualifies one native available-policy
cross-carrier range continuation; ADR 0228's failed I2P prefix remains discarded.
