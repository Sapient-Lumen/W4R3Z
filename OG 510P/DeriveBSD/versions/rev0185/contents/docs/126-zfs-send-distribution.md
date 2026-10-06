# ZFS send/recv as a distribution lane (artifact transport)

DeriveBSD is ZFS-native: generations and microVM bases already live as datasets/snapshots.
A natural (optional) transport is **ZFS replication streams** (`zfs send`/`zfs recv`) treated as *signed artifacts*.

This is not a new idea: FreeBSD’s `poudriere-image` can emit `zfs+send` outputs described as a “full ZFS replication stream … including the boot environment” to be received with `zfs-recv(8)`. (reference: https://man.freebsd.org/poudriere-image)

ZFS itself documents `zfs-send(8)` and `zfs-receive(8)` as the underlying stream mechanism. (references: https://man.freebsd.org/zfs-send , https://man.freebsd.org/zfs-receive)

## Why it fits DeriveBSD

- **Efficient**: send incremental snapshot streams; move “only what changed”.
- **Verifiable**: stream digest is stable; post-receive dataset hashes can be checked against store object digests.
- **Rollback-native**: received datasets can become new BEs or base snapshots without mutation.
- **Policy-friendly**: easy to forbid secrets-in-stream; require signatures/attestations on the stream object.

## Proposed invariant set (v1)

- Treat a replication stream as an `Artifact`:
  - digest (content hash of the stream bytes)
  - signature(s)
  - provenance attestation(s)
  - policy decision record (“why allowed to ship”)

- Stream contents MUST be limited to:
  - host BE datasets (root + declared subdatasets), or
  - microVM base datasets/zvols
  - **no secret material** unless explicitly using an encrypted dataset policy lane.

Note: OpenZFS supports sending encrypted datasets “raw” so receivers need not have keys to store/replicate ciphertext. (reference: https://openzfs.github.io/openzfs-docs/man/master/8/zfs-send.8.html)

- Apply on receiver as **staged**:
  1) receive into a quarantine pool/dataset
  2) verify signature + provenance + closure proof
  3) only then “promote” into the active pool namespace

## Two underused ZFS features worth baking in

OpenZFS has a couple of niche features that map unusually well to DeriveBSD’s needs:
- **Bookmarks**: lightweight incremental-send anchors that let you GC snapshots while still enabling incremental replication.
- **Redaction bookmarks**: support for “data subsetting” in replication streams to omit sensitive blocks while keeping the stream structure valid.
- **Resumable receive**: `zfs receive -s` + resume tokens avoid “restart from zero” and make interruption handling receiptable.

See: `docs/130-zfs-bookmarks-and-redaction.md`, `docs/413-zfs-replication-resume-bookmarks-and-receipted-backups.md`.

## Open questions (kept narrow)

- How to bind dataset snapshot GUIDs to store object digests without relying on ZFS-internal IDs.
- Whether to standardize “send flags” (raw, compressed) for reproducibility.

Related: `docs/69-host-generations-bectl.md`, `docs/27-vm-storage-zfs.md`, `docs/46-cache-trust-model.md`.

Last updated: 2026-02-23
