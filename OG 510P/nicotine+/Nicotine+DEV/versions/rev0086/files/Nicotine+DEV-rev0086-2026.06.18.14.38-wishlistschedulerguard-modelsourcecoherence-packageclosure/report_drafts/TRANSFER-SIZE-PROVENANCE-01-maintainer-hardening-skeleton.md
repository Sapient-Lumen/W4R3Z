# TRANSFER-SIZE-PROVENANCE-01 maintainer hardening skeleton

Status: audited-backlog hardening packet, not strict/front-lane report.

## Summary

Three transfer-size/opened-file invariants were reproduced across 3.3.10, 3.3.x, and master:

1. A positive peer-supplied `TransferRequest.filesize` can replace the locally queued download size and drive the expected `DownloadFile.leftbytes`.
2. The upload network loop reads from the file object using an adaptive read length without clamping that read to the advertised remaining transfer size.
3. Upload authorization/readability/size checks are path/database based, while the F-connection later opens the current filesystem path; if that path is replaced before F init, the opened file can differ from the one represented by the prior checks.

## Boundary

This is primarily transfer integrity/availability and local/sync-race hardening. It is not presented as peer-only code execution or an automatic file disclosure bug. The strongest demonstrated consequence combines U-198 and U-107: a replacement file opened at F init can feed bytes beyond the old advertised size into the socket out buffer because the read is not clamped.

## Fix sketch

- Clamp upload reads to `max(0, advertised_size - (offset + sentbytes + len(out_buffer)))`.
- Treat upload completion as `>= advertised_size` and close/finish deterministically.
- Re-stat/fstat opened upload handles against the previously authorized path metadata, or open a stable handle before advertising the transfer.
- Add compatibility tests for legitimate file growth/shrink, replaced path, offset near EOF, and Soulseek large-file resume quirks.
