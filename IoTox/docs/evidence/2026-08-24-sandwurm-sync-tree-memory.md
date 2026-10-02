# Sandwurm synchronization process peak-memory evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests independently passed the same maximum-entry directory
memory gate over observed direct UDP and forced TCP. Both cells used one production binary, stable
reused test identities, the pinned local c-toxcore 0.2.23 bootstrap/relay fixture, and Linux `VmHWM`
from each long-lived IoTox PID.

After generation 1 converges and activates, the publisher adds twelve deep directories, one 3 MiB
file, and 109 small files. The linked generation-2 tree reaches the configured 128-entry ceiling with
15 directories, 113 files, 7,340,226 content bytes, and a 7,616,908-byte artifact. Both cells publish,
transfer two immutable objects, accept the signed HEAD last, explicitly activate, expose the complete
deep tree, and leave staging empty while both process high-water values remain below 65,536 KiB.

## Accepted compact cells

| Route | Compact proof | Span | Pair peak | Maximum delta | Binary SHA-256 | Source manifest SHA-256 |
|---|---|---:|---:|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.4ndi9yq_` | 243,914,597,210 ns | 12,924 KiB | 1,024 KiB | `5c790e6dd179247f2e5c77d84bfb3658e2be507694d43108d9f9d3b466ec2e9f` | `bfea651bd677fe82b5132c5895a857cf67cc3803613750c351dd7c491862b85d` |
| forced TCP | `.sandwurm/exports/pairs/pair.vbb7zli3` | 381,760,465,102 ns | 13,132 KiB | 1,152 KiB | `5c790e6dd179247f2e5c77d84bfb3658e2be507694d43108d9f9d3b466ec2e9f` | `f38901367f99436b1333ae9c5ee017a06b13554d821ad444e8f12b3ddaa5d799` |

Each compact export independently verifies, contains no secrets or guest disks, and allocates 110,592
bytes. The compact export-manifest SHA-256 values are
`e709759ed4349474ce3ccda5a267dc51091312bc30634dfecffce145be6d1501` for UDP and
`b14b3b95b0f5f68cd35f0d60a6f13c66ecda396e9d8e6a557fe085f3dec3a958` for TCP.

Both cells bind the same generation-2 HEAD
`466c4fd7d5220519cdb8ae9d18a38580c925e23ad15a0b03d15dea0cd1854161`, artifact
`f51b82f1c7e7c6a5e56585023010d7acd87f5747e1c3eeebb755d85682a84c0b`, and manifest
`e4713ff1d5eafdb1b651142ed7c11b1b874364b7f8f12d501acf693383f52086`.

## Phase observations

| Route/role | Post-generation-1 baseline | Post publication/pull | Final peak | Delta |
|---|---:|---:|---:|---:|
| UDP publisher | 11,924 KiB | 12,436 KiB | 12,436 KiB | 512 KiB |
| UDP subscriber | 11,900 KiB | 12,924 KiB | 12,924 KiB | 1,024 KiB |
| TCP publisher | 11,772 KiB | 12,284 KiB | 12,412 KiB | 640 KiB |
| TCP subscriber | 11,980 KiB | 13,004 KiB | 13,132 KiB | 1,152 KiB |

The UDP client/device receipt SHA-256 values are
`3e2e85ae2c1dc3c595885537c99028914b698713e380fdbd64179af2ee02e632` and
`08f829cba4a414ad3cad8946e4f2adcc0d12a44daf054e70ab65391c65993e3f`;
the TCP values are
`51071a683d17e664245d00af35f8c51f4151ce42a0192e5b922709e0c0ad6114` and
`4889b9058ccaa426b3a29ed2935cfc367603e694c14de4652b84368299210222`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-memory
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-memory

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.4ndi9yq_ \
  --route direct-udp --scenario sync-tree-memory
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.vbb7zli3 \
  --route forced-tcp --scenario sync-tree-memory
```

The private source proofs contained writable guest disks and injected test identities. They were
verified before compaction and are intentionally not the durable distribution surface. The compact
exports contain only the verifier allowlist and bind their source manifests.

## Exact nonclaims

This is per-process Linux lifetime resident-set high-water evidence for one publisher, one subscriber,
one 128-entry/7.6 MiB successor, and two carrier cells on this construction kernel. `VmHWM` includes
resident anonymous, mapped-file, and shared pages; it is not heap-only, ordinary filesystem page
cache, whole-VM demand, or a hard limit. The 64 MiB threshold is a test acceptance ceiling, not a
namespace quota or runtime enforcement mechanism. The cells do not prove all allocator schedules,
concurrent namespace/peer/lane maxima, maximum supported artifact or manifest sizes, multi-source or
multi-host behavior, target-fleet kernels, content-v2, automatic OTA, or safety-critical actuation.
ADR 0144 freezes the interpretation.
