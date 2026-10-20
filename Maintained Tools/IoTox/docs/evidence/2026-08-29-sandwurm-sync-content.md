# Sandwurm one-source content-v2 evidence

Date: 2026-08-29

Status: accepted direct-UDP and forced-TCP qualification

## Claim

Two independent source-linked IoTox microVMs can negotiate feature bit 29 and move one genuine paged
content-v2 revision over c-toxcore. The subscriber receives the root manifest and immutable content
objects through exact FileId joins, reconstructs the byte-identical whole artifact into canonical
CAS, accepts the stable-device-signed HEAD last, and activates only after an explicit exact-token
request. The publisher observes the same terminal revision.

## Accepted cells

| Route | Compact proof | Initial pulls/failures | Pair span |
|---|---|---:|---:|
| direct UDP | `.sandwurm/exports/pairs/pair.zx3yb0dz` | 1 / 0 | 348,185,802,604 ns |
| forced TCP | `.sandwurm/exports/pairs/pair.zykym15z` | 1 / 0 | 347,668,666,608 ns |

Both cells use source revision `8934b4bdb2474820430b078b2128642062f718ce-dirty`, product revision
`rev0045`, c-toxcore 0.2.23 variant `iotox-file-rr1-tcp-connect120`, libsodium 1.0.22, and binary
SHA-256 `2495afad6f5ebd32e053449c22c30f7427ae87460f6f0a03aa8c310ee4f0f73d`.

The exact common content truth is:

- artifact: 4,194,304 bytes, SHA-256
  `844dbd0270ee58cf1e1b8062460e6b5f24b974a24fd482e861689d65e81598a7`;
- paged root manifest: 272 bytes, SHA-256
  `f8637c280348a3af9685afdbb53a0351236ec52e26abb146ec8f3a20c39c9b66`;
- fabric shape: four chunks, one manifest page, four deduplicated objects; and
- signed HEAD record SHA-256
  `5418cf893bf66afe955edf1b855e9e72c4069693d245fef9a579f8917c02141c`.

Direct client/device receipt SHA-256 values are
`58f350d320485b359b8b32e0eb13f267ef7d0699004ede066f0a92ce2686ca7f` and
`0e217de439cf5eabd9b792512de5edad342e589a5210e6d652d57971d0b37047`.
Forced-TCP values are
`9203dabb3a4234224ef7a21ba827c545b1c1e0275da8c967dc64ae168828821c` and
`4d7dddffe046451dd9e1857f2ccdfb4d43cae290687160b37dfd4a17e031438e`.

Each secret-free compact root allocates 163,840 bytes and independently passes strict replay. Direct
pair-manifest/compact-export SHA-256 values are
`be122299d37cd2e5eb61fbd55bd6fce2d497e59800643df52b727dc9b5f2b292` and
`57e3ada0ba157c9fa6ebd080d1247e25def7ced15a2ff601d82943eb7bfaecde`.
Forced-TCP values are
`04db9039d7ab1984fbb32c2b3c1a9daa216b8bf1a5d91e9b63f4eaaaf49364b8` and
`4d5bc95129deb36b5bd54399fe1520a2d19478723157f5cba164ed0f86cddd53`.

## Calibration

The first forced-TCP attempt was rejected by the host controller at 240 seconds. Its raw proof wrote
both authority-ready markers at 240.1–240.5 seconds and the complete publisher declaration at
240.4 seconds, with no failure marker. ADR 0252 therefore places this exact route/scenario in the
existing 480-second slow-authority class. The accepted rerun crossed the same content gate without
loosening transfer or total deadlines.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-content
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-content

./tools/iotox-sandwurm-lab.sh verify-pair direct-udp \
  .sandwurm/exports/pairs/pair.zx3yb0dz sync-content
./tools/iotox-sandwurm-lab.sh verify-pair forced-tcp \
  .sandwurm/exports/pairs/pair.zykym15z sync-content
```

The compact forms retain manifests, launch/chain commitments, content-free receipts, and the exact
ordered content completion record. They omit guest disks, injected identities, and runtime secrets.

## Exact nonclaims

This evidence does not prove sparse-availability consumption, complementary partial sources,
simultaneous multi-source scheduling, striping, auxiliary-route assignment, selected-source loss,
daemon or guest restart, performance superiority to whole-object/range-v1, arbitrary disk or power
faults, hostile kernels/filesystems, two physical hosts, or fleet behavior.
