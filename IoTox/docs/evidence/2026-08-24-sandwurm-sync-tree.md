# Sandwurm deterministic-directory synchronization evidence

Date: 2026-08-24

Status: accepted construction evidence

## Claim

Two simultaneous source-linked IoTox guests converged and explicitly activated the same deterministic
directory revision over observed direct UDP and forced TCP. Both cells used the same product binary,
stable test identities, namespace policy, treepack artifact, canonical range index, and signed HEAD.

The publisher tree contains three directories and three regular files. Its 4,194,389 content bytes
include a deterministic 4 MiB payload, an executable probe, a text record, a nested directory, and an
empty directory. Publication produced a 4,194,601-byte canonical treepack plus a 786,568-byte range
index. The subscriber accepted the signed HEAD only after both objects committed, then activated only
the exact operator-supplied HEAD token. Each guest verified the atomic relative `current` pointer,
file contents, entry counts, absence of symlinks, `0500` executable/directory modes, `0400`
non-executable modes, and an idempotent exact activation retry.

## Accepted cells

| Route | Raw private proof | Compact proof | Span | Binary SHA-256 |
|---|---|---|---:|---|
| direct UDP | removed after verified compaction | `.sandwurm/exports/pairs/pair.qf7x57c7` | 325,109,963,224 ns | `13c79d46607f31dbb49cfd47075b5df0f6c69759a30a8a2675357d4684989732` |
| forced TCP | removed after verified compaction | `.sandwurm/exports/pairs/pair.kjr7ksxw` | 206,137,384,579 ns | `13c79d46607f31dbb49cfd47075b5df0f6c69759a30a8a2675357d4684989732` |

Both cells retained:

- generation: `1`;
- tree directories/files/content bytes: `3 / 3 / 4,194,389`;
- treepack artifact bytes: `4,194,601`;
- range-index bytes: `786,568`;
- payload SHA-256: `374921f176ff69a68f433edce6fcd97f8f103229f5572060675f061f48bf0a0e`;
- artifact SHA-256: `a079be557aba734548322fa95ab91825c01735adf4bf0028f6b2dca4a458d93e`;
- manifest SHA-256: `f9483c05ea4d93ec6e7c191a334d854d26d84db8f04c85c8ae5cac2b4f8d8bb7`;
- signed HEAD record: `ac21e81c8f3fc365e47c7e7fcf82c78a9b32c029af6cafc411063584e6f7cfa9`;
- materialization-observing roles: `2 / 2`.

The raw pair-manifest SHA-256 values are
`108847cd07b541c7bd82fad80f3ff0069cd19bf9d2a17dec21767e194e7fe4cb` for UDP and
`aa08133dd0f231c3f3396c11e3b974c7c38a123fe60a6af6dc982d85f3245037` for TCP. Each independently
verified compact export allocates 110,592 bytes.

## Reproduction and verification

```sh
./tools/iotox-sandwurm-lab.sh up-pair direct-udp sync-tree
./tools/iotox-sandwurm-lab.sh up-pair forced-tcp sync-tree

python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.qf7x57c7 \
  --route direct-udp --scenario sync-tree
python3 tools/verify-sandwurm-pair.py \
  .sandwurm/exports/pairs/pair.kjr7ksxw \
  --route forced-tcp --scenario sync-tree
```

One preceding forced-TCP attempt timed out before either guest created any rendezvous or receipt file.
Both VMMs were running, but neither guest service reached the shared workspace. No authority,
publication, transfer, or activation observation existed, so this is recorded as a pre-product
Sandwurm guest-startup flake rather than a sync protocol result. The clean rerun above passed the
complete gate. The failure is intentionally disclosed and is not part of accepted compact evidence;
its private raw disks need not be retained.

The raw roots contained writable guest disks and injected private test identities. They were removed
after both compact exports independently passed the ordinary strict verifier; rerunning the fixture
is the recovery path. Compact exports contain only the verifier allowlist.

## Exact nonclaims

This proves one bounded one-source directory revision, whole-object transfer, explicit activation,
atomic projection, modes, contents, and exact retry on ext4-backed Sandwurm guest disks. Deterministic
tests additionally reject unsafe source entries and artifact overflow, commit signed activation
before a retryable projection, recover exact abandoned staging, reject ambiguous cleanup state, and
retain only the current derived projection. It does not prove directory-range reconstruction,
multi-source convergence, conflict merging, sparse files, ACL/xattr preservation, disk-full behavior,
power loss at every projection syscall, hardware monotonic rollback resistance, automatic OTA,
two-physical-host behavior, or safety-critical actuation.
