# Sandwurm publisher-source corruption evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests independently passed the same publisher-source
corruption and recovery gate over observed direct UDP and forced TCP. Both cells used the production
binary, stable reused test identities, and the pinned local c-toxcore 0.2.23 bootstrap/relay fixture.

After the subscriber accepts and activates generation 1, the publisher signs a one-byte-changed
generation 2 and fsyncs deliberate corruption into both digest-named source objects. The subscriber
requests both objects, but the publisher re-verifies them before file offer and refuses the revision;
the subscriber records `requested=2`, `admitted=0`, and `committed=0`, clears staging, and preserves
its exact generation-1 accepted, activated, object, and visible-tree truth. Explicit publisher repair
then quarantines exactly two objects and 4,981,169 bytes. Exact duplicate publication from unchanged
source reconstructs the same generation-2 objects and HEAD. A fresh pull admits and commits both
objects, accepts the HEAD last, and activates only by the exact token.

## Accepted compact cells

| Route | Compact proof | Span | Pair manifest SHA-256 | Compact export SHA-256 |
|---|---|---:|---|---|
| direct UDP | `.sandwurm/exports/pairs/pair.0yqn_jyc` | 253,214,529,860 ns | `4e58fa551affbb837be14e4080a880d8ed8aa3fc823332f7711e369e381a20aa` | `0aad27a506600267cf6d0954f9df96ab6878e05c40ee30ef7796351c3a701f37` |
| forced TCP | `.sandwurm/exports/pairs/pair.t3celhhl` | 360,471,201,919 ns | `b1d9c527cb92ad150c9eecc6009563536a50e5a6c703a3ca3cb9901770af928e` | `391a5311de31bfe1d92c12aab599b16df7ff503479da1c176b52e546e3b30ceb` |

Each compact export independently verifies, contains no secrets or guest disks, and allocates
110,592 bytes. Both cells bind binary
`5c790e6dd179247f2e5c77d84bfb3658e2be507694d43108d9f9d3b466ec2e9f`, generation-2 HEAD
`0471058960b369e5b5b00e93b9b7f248dc58ae03964fbf2dc968744d6b402319`, artifact
`100fa74e26ee9fd87ba0f3b4818e10c88cc8d44791148c2d61e6a13c7caa8d8a` (4,194,601 bytes), and
manifest `942319e2d126550f9c866c99faa69fd10a0eac04efe59d1f05deeafc650209c6`
(786,568 bytes).

The UDP client/device receipt SHA-256 values are
`02549be2b5d1ccc7c18f0f20d1b6c09bd23f83456c4659bc10b9bb3b2e204529` and
`3639fb5df2fee2ae281a49f9f7df8457f61e33d0ff5e6ccf193552989c86f484`;
the TCP values are
`a0abb8b3f769f0ef869db1f58bad68f42263d2cf1e92c41edf96ec30335c3b47` and
`c971a044c8e599a5495cccc8ecca92e4b2f11b3f8e9e0895ccae11e7ef16f596`.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree-source-corrupt
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree-source-corrupt

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.0yqn_jyc \
  --route direct-udp --scenario sync-tree-source-corrupt
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.t3celhhl \
  --route forced-tcp --scenario sync-tree-source-corrupt
```

The private source proofs contained writable guest disks and injected test identities. They were
verified before compaction and are intentionally not the durable distribution surface. The compact
exports contain only the verifier allowlist and bind their source manifests.

## Exact nonclaims

This is one publisher, one subscriber, one two-object directory revision, two deliberate regular-file
byte corruptions, and two carrier cells on this construction host. It proves request-time source
verification, explicit local quarantine/reconstruction, and explicit subscriber retry. It does not
prove periodic scrubbing, source-content recovery, multiple sources, automatic failover, simultaneous
provider loss, arbitrary media/kernel faults, multi-host behavior, target-fleet storage, content-v2,
automatic OTA, or safety-critical actuation. ADR 0145 freezes the interpretation.
