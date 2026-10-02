# Sandwurm synchronization read-only-storage evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests independently passed the same real-filesystem
read-only-storage gate over observed direct UDP and forced TCP. Both cells used one production
binary, stable reused test identities, the canonical 4 MiB treepack fixture, a dedicated loop-backed
64 MiB ext4 subscriber namespace, and the pinned local c-toxcore 0.2.23 bootstrap/relay fixture.

Generation 1 first converges and activates. The publisher changes one payload byte and signs linked
generation 2. With the subscriber filesystem remounted read-only, pull setup fails before transport
work with `unable to secure sync transaction directory: Read-only file system`, zero requested,
admitted, or committed objects, empty staging, and byte-identical generation-1 accepted, activated,
object, pointer, and visible state. Remounting read-write and retrying the exact pull requests and
commits the two candidate objects and accepts generation 2 without activating it.

The filesystem is then remounted read-only again. Exact generation-2 activation exits with the same
typed I/O error while accepted state remains generation 2 and activated/visible state remains
generation 1. After a read-write remount, exact activation retry exposes the candidate tree and
leaves staging empty.

## Accepted compact cells

| Route | Compact proof | Span | Binary SHA-256 | Source manifest SHA-256 |
|---|---|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.pded9tmd` | 455,866,568,388 ns | `5c790e6dd179247f2e5c77d84bfb3658e2be507694d43108d9f9d3b466ec2e9f` | `71367b901c0810461cef3f7ab7584e95cd66002cfa9cc35fa239d826e3078d1f` |
| forced TCP | `.sandwurm/exports/pairs/pair.ddcbkpei` | 373,938,538,889 ns | `5c790e6dd179247f2e5c77d84bfb3658e2be507694d43108d9f9d3b466ec2e9f` | `1f27df17b919c5a4bf1a6641f1552a3d7894a106c4510b81120a4ed38631b501` |

Each compact export independently verifies, contains no secrets or guest disks, and allocates 110,592
bytes. The compact export-manifest SHA-256 values are
`6671feaf4ac773bae6b1c029ba2c314a16304275d91861f83c7063eb2a66d9e6` for UDP and
`515cbbf368556cad83dd9704626992aebf4344f063ec6e76177646f49e1f0f33` for TCP.

Both cells bind these exact revision identities:

| Revision | HEAD record | Artifact SHA-256 | Manifest SHA-256 |
|---|---|---|---|
| generation 1, initially accepted/activated | `ac21e81c8f3fc365e47c7e7fcf82c78a9b32c029af6cafc411063584e6f7cfa9` | `a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e` | `f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7` |
| generation 2, refused then retried | `f320d8db5cfc9f771f70023cd38bd66326d5ca63247ed62abacb5446dead69e3` | `e996217eb251d66a30a9e3c1c0fe0eff07631243f7ba8f7f512eacf3b09f49df` | `1cd416593d78800edd7d81d0a47800a715085d4203689318437ee82e82552b3c` |

The retained generation-1 visible payload SHA-256 before the successful activation retry is
`374921f176ff69a68f433edce6fcd97f8f103229f5572060675f061f48bf0a0e`.
The UDP client/device receipt SHA-256 values are
`a229f4cc5418bcead7a3784836acb8f0c48b8287c85fff0c3194b71015df5992` and
`24360137dbed103fd64bac01c69908214e86802dcb6481298368363c26cc0297`;
the TCP values are
`630f78d9abef3c2765a47e09defd8c130362e72fd87a0c4f2c34d08843ff4981` and
`e6bf9312210d62e8dd79bf9714ba868fbf5b0112d6421871cd47393913f3ecc2`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-read-only
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-read-only

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.pded9tmd \
  --route direct-udp --scenario sync-tree-read-only
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.ddcbkpei \
  --route forced-tcp --scenario sync-tree-read-only
```

The private source proofs contained writable guest disks, a loop filesystem, and injected test
identities. They were verified before compaction and are intentionally not the durable distribution
surface. The compact exports contain only the verifier allowlist and bind their source manifests.

## Exact nonclaims

This proves one publisher, one subscriber, a real ext4 read-only mount at operation entrance, no
transport or state effects before failed pull admission, accepted-versus-activated separation after
failed activation, and exact manual recovery on this construction kernel. It does not prove a mount
transition during an individual syscall sequence, physical-media faults, journal recovery after
power loss, every filesystem or storage errno, automatic retry, peak resident-memory limits,
multi-source or multi-host behavior, arbitrary kernel scheduling, target-fleet load, content-v2,
automatic OTA, or safety-critical actuation. ADR 0143 records the fail-closed rule.
