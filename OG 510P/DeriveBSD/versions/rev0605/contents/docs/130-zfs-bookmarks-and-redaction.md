# ZFS bookmarks and redaction bookmarks (GC-friendly increments, sanitized replication)

DeriveBSD’s ZFS-native posture makes `zfs send`/`zfs recv` an attractive transport.
Two underused OpenZFS features are especially “greenfield-friendly” if we standardize them early:

- **Bookmarks**: incremental-send anchors that survive snapshot GC.
- **Redaction bookmarks**: “data subsetting” for replication streams.

## 1) Bookmarks: incremental replication without keeping snapshots forever

OpenZFS describes bookmarks as marking the point in time a snapshot was created and being usable as the incremental source for `zfs send`. (ref: `zfs-bookmark(8)` https://openzfs.github.io/openzfs-docs/man/master/8/zfs-bookmark.8.html ; also FreeBSD man page: https://man.freebsd.org/cgi/man.cgi?query=zfs-bookmark&sektion=8)

### DeriveBSD mapping

- Every host generation snapshot and microVM base snapshot SHOULD have a corresponding **bookmark**.
- GC policy MAY destroy older snapshots but SHOULD retain bookmarks required for planned incremental distribution.

### v1 invariants

- Bookmark names are derived from the generation/artifact digest (stable, collision-safe).
- Promotion to “distributable stream” requires:
  - stream digest + signature(s)
  - closure proof
  - policy decision record
- Receivers MUST treat bookmark-based incrementals the same as snapshot-based streams (quarantine → verify → promote).

## 2) Redaction bookmarks: a controlled “sanitized send” lane

OpenZFS documents redaction as creating a *redaction bookmark* that records blocks containing sensitive information; when used with `zfs send`, the stream omits those blocks and emits REDACT records, and the receiver creates a redacted dataset. (ref: `zfs-redact(8)` https://openzfs.github.io/openzfs-docs/man/master/8/zfs-redact.8.html)

### Why it’s interesting for DeriveBSD

This gives a kernel/filesystem-level primitive for:
- sharing “almost everything” for debugging/forensics without shipping specific blocks
- producing sanitized replicas for analysis environments

### DeriveBSD stance (tight and conservative)

- **Not for normal artifacts** (host generations, microVM bases) in v1.
- Allowed only as an explicit **diagnostic export** lane, policy-gated and clearly labeled.

### v1 invariants

- A redacted stream MUST carry an explicit `redaction` record in its provenance/manifest (not implicit).
- Redaction inputs (the redaction snapshots/bookmark) MUST be recorded as evidence.
- Redacted datasets MUST NOT be eligible for “promote to bootable generation” unless an explicit policy exception exists.

## Where this plugs in

- Transport lane: `docs/126-zfs-send-distribution.md`
- Verification rules: `docs/92-verification-matrix.md`

Last updated: 2026-02-23
