# TRANSFER-COMPLETE-LIFETIME-01 / U-269 — completed upload sockets remain active if the receiver keeps the F connection alive

Status in rev0022: **verified audited-backlog lead**, **not promoted strict**.

## Claim now supported

When an upload has already sent exactly the advertised number of bytes, the network thread emits upload progress but does not locally retire the upload, close the F socket, or release the upload slot. The upload remains in `_file_upload_msgs` until remote close, generic idle cleanup, or another close path.

The rev0022 witness adds the missing distinction from rev0009:

```text
silent completed receiver:
  completed upload remains active, then generic idle timeout closes it.

receiver sending post-completion bytes:
  any nonempty post-completion recv refreshes conn.last_active;
  the bytes are discarded because FileOffset was already received;
  the completed upload remains active past the idle window.
```

This means a peer that has already received the advertised bytes can keep the uploader-side upload slot/socket/file state active with tiny invalid post-completion F-input before each idle timeout.

## Maintainer-grade witness

```text
maintainer_artifacts/transfer-complete-lifetime-01/test_completed_upload_socket_lifetime_reproducer.py
```

Run output captured in:

```text
evidence/rev0022-transfer-complete-lifetime-pytest-run.txt
```

Result:

```text
github-tag-3.3.10:   5 passed
github-branch-3.3.x: 5 passed
github-branch-master: 5 passed
```

## Proven invariants

```text
exact_advertised_size_write_leaves_completed_upload_active: true
silent_completed_upload_idle_timeout_closes: true
post_completion_peer_trickle_keeps_upload_active_past_idle_window: true
post_completion_peer_bytes_discarded_after_file_offset_without_cleanup: true
control_close_retires_slot_non_timeout: true
```

## Source shape

The relevant current source shape is stable across the three checked lanes:

```text
pynicotine/slskproto.py::_process_upload
  - increments file_upload.sentbytes;
  - emits file-upload-progress when offset + sentbytes == size;
  - returns True rather than closing/retiring the upload.

pynicotine/slskproto.py::_process_file_offset_message
  - after offset is set, later F-input is discarded by returning len(in_buffer).

pynicotine/slskproto.py::_read_data
  - every nonempty recv updates conn.last_active.

pynicotine/slskproto.py::_check_connections
  - closes inactive established connections only when last_active is older than CONNECTION_MAX_IDLE.

pynicotine/slskproto.py::_close_connection
  - removes _file_upload_msgs and decrements _total_uploads only on close.
```

Detailed line-level source trace:

```text
evidence/rev0022-transfer-complete-lifetime-source-trace.md
data/rev0022_transfer_complete_lifetime_source_trace.csv
```

## Impact boundary

This is **not** code execution, file disclosure, or a peer-only identity spoofing issue. The peer must already be receiving an upload it is allowed to download. The likely impact is upload-slot/socket/file-handle retention and queue fairness/resource availability after the peer has already received all advertised bytes.

The issue is nevertheless meaningful because it removes the silent-peer bound: a tiny post-completion trickle can refresh connection activity while the completed upload remains active.

## Why not strict-promoted

U-269 remains outside the strict/front document because:

```text
- it is availability/slot-lifetime hardening, not a stronger integrity/confidentiality flaw;
- public upload completion/stuck/incorrect-stat symptoms are adjacent;
- legitimate transfer completion semantics need care so the uploader does not close before final bytes are flushed;
- the fix is coherent but should probably be included in a transfer-lifecycle patchset, not presented as a fourth high-priority disclosure candidate.
```

## Fix shape to test

A coherent fix should make completion local and explicit without racing the final write:

```text
1. Treat `offset + sentbytes >= size` as local advertised-size completion.
2. Stop accepting/ignoring arbitrary post-FileOffset input as useful liveness for a completed upload.
3. After the final queued bytes are accepted by the OS, either:
   - actively close the F connection; or
   - transition to a short post-completion drain/close timer that is not refreshed by peer input.
4. Release upload slot/file state once local completion is recorded, while preserving finished-upload plugin/stat events.
5. Keep U-251/U-107 fixes compatible: clamp reads to remaining bytes and handle short reads explicitly.
```

## Regression-test value

This is a strong backlog regression test even if maintainers choose not to treat it as a security issue. It documents the desired invariant clearly:

```text
A peer should not be able to keep a completed upload slot active indefinitely merely by keeping the F socket open and sending invalid post-completion bytes.
```
