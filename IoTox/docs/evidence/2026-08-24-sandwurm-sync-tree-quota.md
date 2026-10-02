# Sandwurm synchronization whole-store quota evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests independently passed the same whole-store byte-quota
refusal gate over observed direct UDP and forced TCP. Both cells used one production binary, stable
reused test identities, the canonical 4 MiB treepack fixture, and the pinned local c-toxcore 0.2.23
bootstrap/relay fixture.

The subscriber first converged and explicitly activated generation 1. Its exact artifact and manifest
consume 4,981,169 bytes under a 5,242,880-byte namespace store ceiling, leaving 261,711 bytes. The
publisher, whose independent local policy has a larger store ceiling, then changed one payload byte
and signed generation 2. Its 4,194,601-byte artifact and 786,568-byte manifest are each independently
larger than the subscriber's remaining budget, so carrier completion order cannot admit a partial
new object.

The subscriber transferred the candidate but ended the pull with the production detail
`sync staged commit would exceed whole-store quotas`. It retained exactly the two generation-1
objects, the exact accepted HEAD and activation records, the same `current` pointer and visible
payload, and no staging residue. Generation 2 never acquired acceptance or activation authority.

## Accepted compact cells

| Route | Compact proof | Span | Binary SHA-256 | Source manifest SHA-256 |
|---|---|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.0codwav1` | 267,168,123,504 ns | `5c790e6dd179247f2e5c77d84bfb3658e2be507694d43108d9f9d3b466ec2e9f` | `ebbb92431a30cb440bab7e45522e96b25d6604fdab0f60448e1f2f14754c9c5f` |
| forced TCP | `.sandwurm/exports/pairs/pair.b6pev5yy` | 432,971,394,959 ns | `5c790e6dd179247f2e5c77d84bfb3658e2be507694d43108d9f9d3b466ec2e9f` | `da8b4f7f885209541d8f9f9217188093034f77ceac5580496d3e74bd445b83ea` |

Each compact export independently verifies, contains no secrets or guest disks, and allocates 110,592
bytes. The compact pair-manifest/export-manifest SHA-256 pairs are
`256cc080aa8a7de550666647264e999affe1c81fc5c9427da7e21dc6056112ed` /
`be526030224a7139fa1151ce2d49a689dcb0629402f50d042b9418fda6a54128` for UDP and
`e33abd421d8fae9410725975c3458c54f693ef4628be03766c9f51194ba05d43` /
`3e525178ae2e9ee0299a85b782e22c0de4d83be45fd499a3e9f3a76b05e5fe1c` for TCP.

Both cells bind these exact revision identities:

| Revision | HEAD record | Artifact SHA-256 | Manifest SHA-256 |
|---|---|---|---|
| generation 1, retained and visible | `ac21e81c8f3fc365e47c7e7fcf82c78a9b32c029af6cafc411063584e6f7cfa9` | `a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e` | `f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7` |
| generation 2, refused by local quota | `a795f7344d7a25750384115ae1f62164d4267078d821f5c233316ead05fd5e12` | `b76a31ded55f958f4e09623d80ce97d281cf8ab0586b7460b4395449c55a82da` | `353725dcf8a878ecee6cf5fd9dd2c53971f2a744f2fbc218f76304734c6b78a4` |

The retained visible payload SHA-256 is
`374921f176ff69a68f433edce6fcd97f8f103229f5572060675f061f48bf0a0e`.
The UDP client/device receipt SHA-256 values are
`bd054ed0ee860a9002eb31b9fa4ef6ab1a125d787d55dfe5895b688cf1816157` and
`471b343adfb89545fcd985b9870b113c0245c36eda05b706ccbc4769f8d74d0b`;
the TCP values are
`8be1deb2942fddb01699bf188b123c3dc8d28d7a325836dde1721128dd2dbf8d` and
`b660e4f44c7b2e035543e6816bf12b05d076df29e19072c111cf7ced63a2a3e8`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-quota
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-quota

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.0codwav1 \
  --route direct-udp --scenario sync-tree-quota
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.b6pev5yy \
  --route forced-tcp --scenario sync-tree-quota
```

The private source proofs contained writable guest disks and injected test identities. They were
verified before compaction and are intentionally not the durable distribution surface. The compact
exports contain only the verifier allowlist and bind their source manifests.

## Exact nonclaims

This proves one publisher, one subscriber, a local whole-store byte ceiling, order-independent
candidate-object refusal, failure cleanup, and signed/visible old-state preservation on this
construction kernel. It does not prove the separate object-count ceiling on the genuine provider,
quota recovery, destructive collection, automatic eviction, read-only storage, a peak resident-memory
ceiling, multi-source or multi-host behavior, arbitrary kernel scheduling, target-fleet load,
content-v2, automatic OTA, or safety-critical actuation. IoTox currently has no purge authority; an
operator must size immutable stores with retention headroom until conservative pin/GC work is enabled.
