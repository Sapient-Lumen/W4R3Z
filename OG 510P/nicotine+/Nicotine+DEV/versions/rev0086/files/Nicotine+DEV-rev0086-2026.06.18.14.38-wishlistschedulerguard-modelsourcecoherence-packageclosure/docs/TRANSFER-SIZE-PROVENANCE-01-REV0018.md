# TRANSFER-SIZE-PROVENANCE-01 — rev0018

Status: **verified audited-backlog hardening packet; not strict-promoted**.

Lead rows:

```text
U-69  — Peer-controlled transfer-start filesize can expand queued download.
U-107 — Upload sender reads are not clamped to advertised remaining transfer size.
U-198 — Upload authorization/readability checks are path-based and not bound to the opened inode.
```

## What rev0018 proved

A maintainer-style current-behavior witness now exists at:

```text
maintainer_artifacts/transfer-size-provenance-01/test_transfer_size_and_file_provenance_reproducer.py
```

It passed against all archived source lanes:

```text
github-tag-3.3.10:   3 passed
github-branch-3.3.x: 3 passed
github-branch-master: 3 passed
```

The witness proves three concrete current behaviors.

### U-69 — peer-declared download size replaces queued size

A locally queued download with a known size can receive a peer `TransferRequest` for the same claimed username/path/token. If the peer supplies a positive `filesize`, the download object adopts that value and marks `size_changed`. When the F connection starts, `DownloadFile.leftbytes` is calculated from that mutated size.

Probe shape:

```text
queued download size: 1024 bytes
peer TransferRequest.filesize: 64 MiB
observed: download.size == 64 MiB
observed: DownloadFile.leftbytes == 64 MiB
```

This is real transfer provenance behavior, but it is compatibility-sensitive because the Soulseek flow expects clients to store a transfer filesize during negotiation.

### U-107 — upload network read is not clamped to advertised remaining size

`slskproto.NetworkThread._process_upload()` calculates an adaptive `num_bytes_to_read`, but it does not clamp the file read to:

```text
advertised_size - (offset + sentbytes + len(out_buffer))
```

Probe shape:

```text
UploadFile.size: 10 bytes
file object length: 4096 bytes
observed first _process_upload cycle: 4096 bytes read into conn.out_buffer
```

### U-198 + U-107 — replacement path can feed bytes beyond the previously advertised size

The strongest rev0018 consequence combines the opened-file provenance issue with the unclamped network read. The upload transfer can be authorized/activated using one path state, but the F-init path later opens the current filesystem path. If that path is replaced between activation and F init, `UploadFile.size` can still reflect the old advertised size while the opened handle points at the replacement file. Because U-107 does not clamp the read, replacement bytes beyond the advertised size can enter the socket out buffer.

Probe shape:

```text
initial path content: ORIGINAL        # 8 bytes
activated upload.size: 8
path replaced before F init with: REPLACED-SECRET-BEYOND-ORIGINAL-SIZE
observed: F init opens replacement path
observed: UploadFile.size remains 8
observed: _process_upload buffers the full replacement content, including bytes after byte 8
```

## Why this is not strict-promoted

This cluster is important hardening, but it did not displace the current strict/front-lane items:

- U-69 is a real peer-controlled download-size mutation, but the protocol itself stores transfer size during the transfer flow and clients need compatibility with legitimate size changes and large-file quirks.
- U-107 is a clean code-level clamp bug, but the most serious impact requires an advertised-size/opened-file mismatch.
- U-198 has a local/sync/archive/container-volume/shared-folder race precondition. It is not a peer-only unauthenticated disclosure on its own.

The combined result deserves regression tests and a coherent fix. It does not yet deserve to become the fourth high-priority/high-quality report-candidate.

## Fix shape

Do **not** fix this as three unrelated one-line changes. The safer shape is:

```text
1. Clamp upload file reads to the remaining advertised transfer size.
2. Treat upload completion/close logic as >= advertised size, not only == advertised size.
3. Revalidate opened upload handles at F init using fstat/stat metadata, or open a stable handle before advertising the transfer.
4. Keep the download-side positive size-change behavior compatible, but add a bounded/generation-aware policy for large unexpected changes.
5. Add tests for replacement path, grown file, shrunk file, offset near EOF, size increase after queueing, and large-file resume quirks.
```

## Decision

```text
U-69: verified audited backlog; not strict-promoted.
U-107: verified audited backlog; not strict-promoted standalone.
U-198: verified audited backlog; not strict-promoted.
```
