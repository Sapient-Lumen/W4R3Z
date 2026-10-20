# Sandwurm subscriber-destination corruption evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests independently passed the same subscriber-destination
corruption and selective-retry gate over observed direct UDP and forced TCP. Both cells used the
production binary, stable reused test identities, and the pinned local c-toxcore 0.2.23
bootstrap/relay fixture.

After generation 1 is accepted and activated, the publisher signs a one-byte-changed generation 2.
The rate-shaped subscriber pauses the live artifact receive after positive progress and ten stable
samples, overwrites and fsyncs byte zero of the exact private transport temporary, then resumes that
same FileId. Tox completion does not authorize object commit: the complete staged SHA-256 mismatch
fails the job, removes corrupt staging and signed attempt truth, leaves the corrupt artifact absent,
and preserves generation-1 accepted, activated, inventory, and visible-tree truth. In both cells the
smaller manifest validly committed before the artifact failure. A fresh explicit pull proves and
reuses that manifest locally, requests/admit only the missing artifact, finishes with two verified
candidate objects, accepts the HEAD last, and activates only by the exact token.

## Accepted compact cells

| Route | Compact proof | Span | Pair manifest SHA-256 | Compact export SHA-256 |
|---|---|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.53ouy15u` | 411,319,341,946 ns | `b79d0b27425cdac8375a89dae3c32e49af20bd5399c1d995fab047529e2426df` | `878bf7d81f6258c4c3d4f3a38899ea6d26e9543501d7c3ff0b6812e7e8c72dc7` |
| forced TCP | `.sandwurm/exports/pairs/pair.nvvzvr4w` | 411,104,024,047 ns | `41b4e5a3f1f99daa7d1b3d651e26eb214fa6daf153fc172e39a9749c491ce232` | `59e229bfac2fd7af310d0d684b4b7a17bf1ccfe48fcddd95595abb98acfdf201` |

Each compact export independently verifies, contains no secrets or guest disks, and allocates
122,880 bytes. Both cells bind binary
`5f2ce692b6173164169f6c87962e9ab8c5fee84969ca198132ece993bfc645a7`, generation-2 HEAD
`219552b47044c50899a4df3cc39a38907fd14ceaacf68600c50478a91562ed75`, artifact
`01bfa7581f7a9d14a64d66f120d81430e7edf0e94c0a631a00b80832edae850e` (4,194,601 bytes), and
manifest `78dcad0974285c6c0c554a8788f7a252cb2c584220f1569caf96382c40c28961`
(786,568 bytes). The UDP corruption was observed at position 69,921 under FileId
`bf461cf7d722ccad0b322c026906c1b5959ccfd5f434c6eb23d44b9b9ff8635f`; TCP observed position
68,550 under FileId
`539b9f1a2b803cdc4008f7953f3d811fc9e7d5c9ef8868ce3ef871167836dcdc`.

The UDP client/device receipt SHA-256 values are
`9ddb4c6ede80195da83b0db60ff2b2a7b963055dc078150d0b66d82418f556e4` and
`2422eb22ca957aefeffea1122cf14c040d195dba816093830e2eeb9cd1f6bd83`;
the TCP values are
`8f799d0f8d1d90d90ca6981af18a239d1c75630001f8749819c5553afbc35ae8` and
`374317da323fd0c986c3ee33de36e26f224286cc4d16d7f3950b9b43b0fc8d3f`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-destination-corrupt
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-destination-corrupt

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.53ouy15u \
  --route direct-udp --scenario sync-tree-destination-corrupt
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.nvvzvr4w \
  --route forced-tcp --scenario sync-tree-destination-corrupt
```

The private source proofs contained writable guest disks and injected test identities. They were
verified before compaction and are intentionally not the durable distribution surface. The compact
exports contain only the verifier allowlist and bind their source manifests.

## Exact nonclaims

This is one publisher, one subscriber, one two-object directory revision, one deliberate regular-file
byte corruption per carrier, and two cells on this construction host. It proves complete destination
verification, failed-attempt cleanup, valid sibling retention, selective explicit retry, HEAD-last
acceptance, and separate activation. It does not prove arbitrary block-device/kernel faults,
periodic scrubbing, automatic retry, multiple sources, failover, two-physical-host behavior,
content-v2, OTA installation, or safety-critical actuation. ADR 0146 freezes the interpretation.
