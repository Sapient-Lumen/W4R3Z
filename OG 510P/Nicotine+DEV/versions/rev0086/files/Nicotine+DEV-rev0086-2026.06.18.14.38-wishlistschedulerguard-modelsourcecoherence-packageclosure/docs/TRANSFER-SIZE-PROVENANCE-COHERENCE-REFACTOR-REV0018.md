# TRANSFER-SIZE-PROVENANCE coherence refactor — rev0018

The higher-order question in this pass was whether U-69, U-107, and U-198 form one coherent report or three separate ones.

## Refactor decision

```text
TRANSFER-SIZE-PROVENANCE-01 = U-69 + U-107 + U-198 as an audited-backlog packet.
No strict promotion in rev0018.
```

The best maintainer-facing packet is one hardening cluster, not three separate reports.

## Coherence map

### Keep together

```text
U-107 + U-198
```

These combine into the clearest consequence: a file opened by current path at F init can differ from the one represented by earlier path/database checks, and the sender can then read beyond the old advertised size because reads are not clamped to remaining bytes.

### Keep adjacent, but not identical

```text
U-69
```

U-69 is download-side. It shares the same “transfer size provenance” theme, but not the same opened-file/inode root. The fix should avoid silently trusting unlimited peer size changes, but it should not be welded to upload read-clamping mechanics.

### Keep separate for now

```text
U-248 — share rescan cache provenance
U-251 — upload EOF/short-read lifecycle
U-226/U-230/U-250 — incomplete-download file-entry/provenance family
```

These may later join a broader file-provenance program, but rev0018 did not prove them under the same root. Keeping them separate prevents the cube from accumulating fake coherence.

## Anti-regression guidance

A patch that only validates the path before queueing upload is incomplete. A patch that only clamps reads is also incomplete. The coherent minimum is:

```text
- clamp upload reads to remaining advertised bytes;
- close/finish safely when >= advertised size;
- revalidate current opened file metadata at F init, or hold a stable opened handle from authorization to transfer start;
- decide a bounded policy for download-side size changes from peer TransferRequest;
- preserve legitimate Soulseek large-file/resume compatibility.
```
