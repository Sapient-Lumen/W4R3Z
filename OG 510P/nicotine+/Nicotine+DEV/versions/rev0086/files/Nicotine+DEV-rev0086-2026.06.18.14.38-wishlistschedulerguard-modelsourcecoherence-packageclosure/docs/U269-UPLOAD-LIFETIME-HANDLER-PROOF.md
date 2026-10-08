# U-269 — upload completion lifetime handler-level proof

Status in rev0009: **source-confirmed audited-backlog candidate**, not strict.

## Result

The rev0009 non-network handler probe confirmed the following across all three source lanes:

```text
uploadfile_issued: True
all_bytes_progress_keeps_transfer_active: True
no_finish_on_all_bytes_progress_alone: True
control_close_finishes: True
```

Interpretation: after `FileTransferInit`, the main-thread upload handler opens the file and issues an `UploadFile` internal message. When the network layer reports `offset + bytes_sent == size`, `_file_upload_progress()` updates transfer progress but does not finish the upload. The transfer remains active with its file handle open until `_file_connection_closed()` arrives; the close handler then finishes and cleans up if the current offset is at least the advertised size.

## Why this was not promoted

This is a real lifecycle hardening issue, but not a clean strict item yet:

```text
- public upload completion/progress/stuck-transfer history is adjacent;
- the source has a general idle timeout, so a silent peer may be bounded by connection idle cleanup;
- a stronger claim would require a full slskproto/network-loop harness showing actual slot/socket retention under peer-controlled post-completion activity;
- the fix shape is different from U-123 and should not be bundled into the duplicate-token patch.
```

## Coherent fix shape if pursued

```text
- after upload sender reaches advertised size, retire or mark complete locally without depending solely on remote close;
- actively close the F socket after final queued bytes are flushed, or set a short post-completion close timer;
- make sure the downloader has had a chance to receive final bytes before abrupt close;
- preserve average upload speed reporting and finished-upload plugin notification semantics.
```

## Next step only if reprioritized

Build a full network-loop harness around `slskproto._process_upload()` and `_check_connections()` to measure whether a peer can hold upload slot/socket state materially longer than the idle timeout or by sending post-completion input.
