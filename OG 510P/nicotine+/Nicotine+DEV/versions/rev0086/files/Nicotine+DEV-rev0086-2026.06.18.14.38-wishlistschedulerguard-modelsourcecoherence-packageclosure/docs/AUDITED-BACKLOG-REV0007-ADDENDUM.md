# Audited backlog rev0007 addendum

## Main queue movement

- **U-123** is promoted within the backlog from “next dynamic-repro target” to **top strict-candidate holding pen**. It is not in the strict document yet.
- **U-169** remains technically higher-severity if the FileTransferInit binding question proves exploitable, but it now depends on the same transfer-session integrity evidence. It should be filed with U-123 or after U-123, not as an isolated report.
- **U-158** is linked but not solved by the U-123 fix shape because UploadFailed/UploadDenied do not carry the transfer token.
- **U-269/U-270** remain high-risk next candidates, but rev0007 deliberately avoids splitting attention before closing U-123's remaining proof gap.

## Why U-123 is still not strict

The rev0007 probe is handler-level. It proves peer-message handler behavior and stale timer impact across all three source lanes. It does not yet show the final socket-level consequence after an F connection tries to attach, so it remains one gate short of a high-quality report.

## Machine-readable files

- `data/rev0007_ranked_audit_queue.csv`
- `data/rev0007_queue_delta.csv`
- `data/rev0007_u123_handler_timer_probe.csv`
- `data/rev0007_transfer_lifecycle_coherence.csv`
- `data/rev0007_public_overlap_u123.csv`
