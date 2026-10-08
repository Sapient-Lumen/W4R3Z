# TRANSFER-EOF-01 / U-251 — upload short-read/EOF lifecycle — rev0019

Status: **verified audited-backlog hardening packet; not strict-promoted**.

Lead row:

```text
U-251 — Upload sender treats EOF-before-advertised-size as non-fatal, leaving short/growing/replaced shared files stuck until idle timeout.
```

## What rev0019 proved

A maintainer-style current-behavior witness now exists at:

```text
maintainer_artifacts/transfer-eof-01/test_upload_eof_before_advertised_size_reproducer.py
```

It passed against all archived source lanes:

```text
github-tag-3.3.10:   4 passed
github-branch-3.3.x: 4 passed
github-branch-master: 4 passed
```

The witness proves four current behaviors.

### 1. EOF before advertised size is not terminal

When the upload file object returns data shorter than the advertised `UploadFile.size`, and then returns `b""`, `_process_upload()` does not emit `upload-file-error`, does not close the F connection, and keeps the upload in `_file_upload_msgs`.

Probe shape:

```text
advertised size: 64 bytes
first read:      16 bytes
second read:     EOF / b""
observed:        upload remains active, sentbytes=16, out_buffer empty
observed:        no upload-file-error
observed:        no completion file-upload-progress event
```

### 2. The eventual closure is idle-path behavior, not short-read handling

After the local file can no longer supply bytes, the upload remains active until the generic idle connection check closes it. The test intentionally separates the moment of EOF from the later `_check_connections()` idle closure path.

That matters for fix design: a patch should not rely on connection idle cleanup to detect that the opened file does not match the advertised size. The sender knows earlier that it cannot currently satisfy the advertised transfer.

### 3. Later file growth is accepted after an earlier EOF

The current send loop will keep trying. A scripted file that returns:

```text
b"ABC", then b"", then b"DEF"
```

can still enqueue `b"DEF"` later without restarting or revalidating the transfer. That means the observed behavior is not simply “EOF means fail”; it is “EOF means no bytes now, keep the transfer state alive.”

This could be compatibility-tolerant for a growing file, but it is unsafe as an unbounded default for a stable short/replaced file.

### 4. Sent-byte overshoot misses exact completion

If earlier sender behavior has already queued more bytes than the advertised remaining size, `_process_upload()` increments `sentbytes` beyond `size`, but completion is gated on:

```text
offset + sentbytes == size
```

not:

```text
offset + sentbytes >= size
```

Probe shape:

```text
advertised size: 8 bytes
reported sent:   16 bytes
observed:        sentbytes=16 > size=8
observed:        no completion file-upload-progress event
observed:        upload state remains active
```

This is why rev0018's read-clamp finding and rev0019's EOF/completion finding must be fixed coherently. A read clamp prevents overshoot. A completion/error invariant prevents an upload from staying alive when the local file cannot deliver exactly the advertised byte count.

## Source-shape summary

All three archived source lanes keep the same relevant structure in `pynicotine/slskproto.py`:

```text
- `_process_upload()` reads when `total_read_bytes < size`.
- A `read()` returning `b""` is appended to `out_buffer` with no special case.
- Only `OSError` and `ValueError` emit `upload-file-error`.
- Upload completion uses exact equality: `offset + sentbytes == size`.
- Otherwise `_process_upload()` returns True and leaves the connection active.
- Generic `_check_connections()` later handles idle closure.
```

The full line-by-line trace is in:

```text
evidence/rev0019-transfer-eof-source-trace.md
```

## Public-overlap assessment

Classification:

```text
candidate no direct exact public match found / public upload-stuck-completion adjacent
```

Public material exists for uploads that appear complete locally while recipients see aborts near 99%, uploads that are cancelled/stuck, and release-note history around stuck/cancelled transfer states. That is enough to prevent a clean novelty claim.

Targeted exact searches did not find a direct public report of this narrower invariant:

```text
opened upload file returns EOF before advertised size
+ `_process_upload()` treats EOF as non-terminal
+ exact `== size` completion gate
+ upload remains active until idle/close path
```

## Why this is not strict-promoted

U-251 is real and verified, but it does not become the fourth strict report-candidate in rev0019 because:

```text
- strongest practical paths depend on a local/sync/archive/container-volume/shared-folder mismatch,
  file shrink/replacement after scan/queue, or remote-assisted download-into-shared-folder workflow;
- it overlaps public stuck/cancelled/99%-completion symptoms;
- it is a hardening and correctness issue in the upload lifecycle, not a peer-only confidentiality or code-execution issue;
- it is better presented as part of a coherent transfer-send invariant after U-107/U-198 fixes are specified.
```

## Fix shape

Do not fix U-251 as a lone “close on read()==b''” patch without considering legitimate filesystems and compatibility. The coherent minimum is:

```text
1. Clamp upload reads to advertised remaining bytes.
2. Treat offset+sentbytes >= advertised size as locally complete for completion accounting.
3. When read() returns b"" before advertised size:
   - re-stat/fstat the opened handle;
   - if stable EOF is confirmed below advertised size, emit a local file/size mismatch failure and close;
   - if a growing-file grace policy is intentionally preserved, make it bounded by time/read attempts and status-visible.
4. Pair this with U-198 stable-handle or fstat/stat provenance checks at F-init.
5. Add tests for short file, growing file, replaced file, overshoot, offset near EOF, and normal exact-size completion.
```

## Decision

```text
U-251: verified audited backlog; not strict-promoted.
U-107: remains required support/regression sibling.
U-198: remains file-provenance input that can create the mismatch.
U-269: kept separate; it assumes advertised bytes were sent and the peer keeps the socket open.
```
