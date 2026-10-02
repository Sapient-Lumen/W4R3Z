# Sandwurm directory rollback, fork, and ENOSPC evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests independently passed the same three-generation signed
directory adversity gate over observed direct UDP and forced TCP. Both cells used the same production
binary, stable test identities, canonical treepack fixture, namespace policy, and pinned local
c-toxcore 0.2.23 bootstrap/relay fixture.

The subscriber first accepted and explicitly activated generation 2A. The publisher then restored a
coherent generation-1 synchronization root and presented its still-valid signed HEAD. The subscriber
returned `signed HEAD refused: stale` and preserved the exact accepted record, activated record, and
visible generation-2 payload. From generation 1 the publisher signed a different generation-2 child;
the subscriber returned `signed HEAD refused: fork` with the same three preservation checks. Four
savedata-preserving publisher daemon restarts separated the coherent roots.

After restoring 2A, the publisher signed generation 3. The subscriber accepted it, filled its
dedicated loop-mounted 64 MiB ext4 namespace until 2,096,128 bytes remained, and attempted explicit
activation. Signed activation truth advanced but the derived 4,194,601-byte directory projection
could not complete; `current` remained byte-identical to 2A. Removing only the exact filler and
retrying the same HEAD returned `decision=duplicate materialized=1`, switched `current` to generation
3, retained one revision, and left no derived temporary. This causal retry distinguishes storage
exhaustion from an invalid revision: the signed revision and every other input were unchanged.

## Accepted compact cells

| Route | Compact proof | Span | Binary SHA-256 | Source manifest SHA-256 |
|---|---|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.bv44g4mm` | 914,298,040,974 ns | `8592587678efa55251cf57d24c0759bb1a80ea63e07d33d5f6173ddd47501ecf` | `910a309fa018c428b7d31e3d77c9f0cd00a354c0cf5fcc4a0e8d145f8e5a3923` |
| forced TCP | `.sandwurm/exports/pairs/pair.iuevljep` | 565,397,202,085 ns | `8592587678efa55251cf57d24c0759bb1a80ea63e07d33d5f6173ddd47501ecf` | `3a033848264c547209e647159b5a37b5d2f7030832ebae36483bce861e7a6c73` |

Each compact export independently verifies, contains no secrets or guest disks, and allocates 110,592
bytes. The compact pair-manifest/export-manifest SHA-256 pairs are
`7d3b44db200fe97e23249fdd0b8f2f4d1ba5ee467cb6050bc6602d9e5122427d` /
`0638b8d3810a8def60ae6c2d854468aaaf386ebc29e1dddace5af8e77ed262e2` for UDP and
`3b1b8994a91096fd841fa7906067ecc3d9155c5b50d5bd17aab3d1efd710597e` /
`0fd8fe7af7a9639f47fc3b878f4009dcffac086e1eac32afaf4597cb9a47d599` for TCP.

Both cells bind these exact revision identities:

| Revision | HEAD record | Artifact SHA-256 | Payload SHA-256 |
|---|---|---|---|
| generation 1, stale | `ac21e81c8f3fc365e47c7e7fcf82c78a9b32c029af6cafc411063584e6f7cfa9` | `a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e` | `374921f176ff69a68f433edce6fcd97f8f103229f5572060675f061f48bf0a0e` |
| generation 2A, accepted | `ba0a474768210498cc71af87e105707c5f3e1068369c95e598d8da679ff7fcfa` | `5bd145f3f1600b82bb953404408879ff85b660757fe99f4be0941566524675d7` | `1c5d6cab9d861de15ff4e597aa5185f04a04dcdd0efac211a49917b2e75b6aec` |
| generation 2B, refused fork | `0009c448ea10fbb1a550149a2bb1febcdea4f40267ccae22388df5bb57674ffe` | `2faec139abf3943dcf726901ddcb264931eec3122092011beda5d9517ce2bc1d` | `903a53bd83cf8344bf3aab73ad9b0ca8764587e5a747d426d8a026169628680d` |
| generation 3, recovered | `6ea55a4dd23c26272000aa9018fc4b4d8b8bf28eb9b83a26610097bc95de4c29` | `cda6ff7f9c4cfd9f42ba3a6318ac2ad52b8935d57b6c8f34e39ef8a4840e65ea` | `4317946bf89e6f42ef24d1003da5df32026ebd25717c69bd121440981b6650e6` |

Every revision is a 4,194,601-byte canonical treepack with three directories, three files, and
4,194,389 content bytes. Every range manifest is 786,568 bytes. Generation 3 uses manifest SHA-256
`018a17b5dcc81ed2bd6c1ab60ae8bd79d079dbf8311297f3dc513d1e70c7852c`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-adversity
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-adversity

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.bv44g4mm \
  --route direct-udp --scenario sync-tree-adversity
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.iuevljep \
  --route forced-tcp --scenario sync-tree-adversity
```

The private source proofs contained writable guest disks and injected test identities. They were
verified before compaction and are intentionally not the durable distribution surface. The compact
exports contain only the verifier allowlist and bind their source manifests.

## Exact nonclaims

This proves one publisher, one subscriber, one bounded directory fixture, coherent publisher-root
replacement, stale/fork refusal, real ext4 free-space exhaustion during derived projection, visible
old-tree preservation, and exact retry on this construction kernel. It does not prove abrupt power
loss during the ENOSPC transaction, hardware monotonic rollback resistance, coordinated rollback of
every signed root plus its guard, memory or worker-queue exhaustion, quota-boundary coverage,
multi-source conflict resolution, directory-range reconstruction, two-physical-host behavior,
target-fleet filesystem diversity, automatic OTA, or safety-critical actuation.
