# Deterministic image building (mtree → makefs → mkimg)

DeriveBSD needs microVM artifacts that are **bitwise explainable**:
- same inputs + policy → same image digest (or predictable deltas)
- image can be reconstructed from a tree + manifest + toolchain digests
- artifacts do not depend on host-local filesystem quirks

## Ingredients

### mtree specification
Use `mtree(8)` as the canonical “filesystem tree description”:
- paths, types, permissions/flags/owners
- optional checksums for file content
- explicit exclusion lists

### makefs
Use `makefs(8)` to create filesystem images from:
- a directory tree, OR
- an mtree manifest (preferred for determinism)

### mkimg
Use `mkimg(1)` to assemble partitioned disk images:
- GPT/MBR layouts
- boot partitions + root partitions
- (optionally) swap

## DeriveBSD v1 pipeline (microVM)

1) **Assemble root tree** in a build jail:
- install into staging directory
- normalize timestamps/ownership where policy requires

2) **Emit mtree manifest** (deterministic):
- `mtree -c ...` with explicit keywords + exclusions

3) **Build filesystem image** (makefs):
- choose FS type (ufs/zfs/...) by policy
- use manifest as source-of-truth

4) **Assemble disk image** (mkimg):
- partition scheme + boot blocks are policy-governed
- output is content-addressed and signed

5) **Attach to bhyve** as virtio-blk:
- runtime manifest references the disk image digest

## Determinism knobs (policy)

- time normalization (SOURCE_DATE_EPOCH)
- stable uid/gid mapping
- stable directory ordering rules
- explicit file flags policy

## Reference implementations worth studying
FreeBSD’s `release` tooling (src/release) already builds sets of images and is a rich source of practical constraints.

## Non-goals (v1)
- perfect cross-host bit-identical images across differing kernel/filesystem versions (policy can tighten over time)
- supporting every filesystem/boot scheme immediately

See RFC-0051.

Last updated: 2026-02-23
