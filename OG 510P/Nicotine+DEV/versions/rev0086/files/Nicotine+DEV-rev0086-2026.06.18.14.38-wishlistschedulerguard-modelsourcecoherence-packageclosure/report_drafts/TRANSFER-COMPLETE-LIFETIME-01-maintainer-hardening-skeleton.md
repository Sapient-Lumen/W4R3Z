# TRANSFER-COMPLETE-LIFETIME-01 / U-269 maintainer hardening skeleton

This is not a production-ready disclosure text. It is a maintainer-oriented hardening note and regression-test scaffold.

## Summary

After an upload has sent exactly the advertised number of bytes, the network thread currently reports progress but keeps the upload active until the downloader closes the F socket or generic idle cleanup closes the connection. If the downloader sends small post-completion bytes before each idle timeout, those bytes are discarded after `FileOffset` has already been received, but they refresh `conn.last_active` and keep the completed upload slot active.

## Reproducer

```text
maintainer_artifacts/transfer-complete-lifetime-01/test_completed_upload_socket_lifetime_reproducer.py
```

Observed current behavior across `3.3.10`, `3.3.x`, and `master`:

```text
5 passed per lane
```

## Expected hardening invariant

```text
Once the uploader has locally sent the advertised byte count and the final queued bytes have been accepted by the socket, the upload should move to a bounded completion/close/retire state that is not extended by arbitrary post-completion receiver input.
```

## Suggested implementation shape

```text
- Treat offset + sentbytes >= size as local advertised-size completion.
- Ensure final buffered bytes are flushed before forced close.
- Release upload slot/file handle at local completion or after a short, non-refreshable drain timer.
- Ignore or close on post-FileOffset input once completion has been reached.
- Preserve UploadFailed/finished notification semantics and avoid double-finish on later close.
```

## Compatibility cautions

```text
- Do not close before the OS has accepted the final buffered bytes.
- Do not break slow legitimate downloads before advertised-size completion.
- Coordinate with U-107 read-clamp and U-251 short-read handling; otherwise completion and EOF semantics can remain inconsistent.
```
