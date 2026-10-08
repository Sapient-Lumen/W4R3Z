# F-CONN-FRAME-01 maintainer report skeleton — audited backlog, not strict-front in rev0015

## Summary

The F-connection input path consumes partial fixed-width `FileTransferInit` and `FileOffset` frames instead of buffering until the full 4-byte or 8-byte frame is available. This can break transfers under normal TCP fragmentation and can resynchronize remaining bytes plus later peer-controlled suffix bytes into a different token or offset.

## Current behavior witness

```text
maintainer_artifacts/f-conn-frame-01/test_f_connection_fixed_frame_fragment_reproducer.py
```

Observed result:

```text
github-tag-3.3.10: 22 passed
github-branch-3.3.x: 22 passed
github-branch-master: 22 passed
```

## Boundary

Peer-driven transfer robustness / availability / state-confusion hardening. Not code execution and not standalone file disclosure.

## Suggested regression direction

- Buffer until `len(in_buffer) >= 4` before parsing `FileTransferInit`.
- Buffer until `len(in_buffer) >= 8` before parsing `FileOffset`.
- After a valid offset is accepted, preserve existing behavior that clears unexpected post-offset input.
- Add split-position tests for 1..3 and 1..7 bytes.

## rev0015 presentation decision

Keep in audited backlog. Do not use as a strict/front-lane report unless a stronger current-master consequence is later proven.
