# rev0007 U-123 handler/timer proof

## Executive result

U-123 moved from a local `_activate_transfer()` overwrite microprobe to a handler-level peer-message reproduction.

For each current/future source lane (`github-tag-3.3.10`, `github-branch-3.3.x`, and `github-branch-master`), the rev0007 probe constructs two legitimate queued downloads from the same username, feeds two peer-style `TransferRequest(direction=UPLOAD, token=4242, file=...)` messages through `Downloads._transfer_request()`, and then fires the stale timeout for the first transfer.

The result is consistent across all lanes:

| lane | both TransferRequests allowed | second overwrote first active map entry | stale first timer removed active mapping | second transfer left tokened but unindexed |
|---|---:|---:|---:|---:|
| github-tag-3.3.10 | True | True | True | True |
| github-branch-3.3.x | True | True | True | True |
| github-branch-master | True | True | True | True |

## Why this is stronger than rev0006

rev0006 only proved that `_activate_transfer()` can overwrite an existing `active_users[username][token]` mapping when called twice with the same token.

rev0007 proves the overwrite through the download `TransferRequest` handler, which is closer to the real peer flow:

1. A download is queued locally for `alice\Music\a.mp3`.
2. A second download is queued locally for `alice\Music\b.mp3`.
3. The peer sends `TransferRequest` for `a.mp3` with token `4242`; Nicotine+ accepts and stores `active_users['alice'][4242] = a.mp3`.
4. The peer sends `TransferRequest` for `b.mp3` with the same token; Nicotine+ accepts and stores `active_users['alice'][4242] = b.mp3`, leaving the first transfer with a live timeout but no active-map entry.
5. The stale first timeout calls `_deactivate_transfer(first)`; `_deactivate_transfer()` sees token `4242` in `active_users['alice']` and deletes it without checking that the mapped object is still `first`.
6. The second transfer remains in a limbo state: `Getting status`, `token=4242`, `timer-2`, but no active-map entry for future FileTransferInit/progress/close lookup.

## Source invariant

The compact source trace is in `evidence/rev0007-u123-source-trace-handler-timer.md`.

The critical invariant is not merely duplicate-key overwrite. It is the combination of:

- peer-supplied token accepted from `TransferRequest`;
- active transfer map keyed only by `username + token`;
- no duplicate-key guard in activation;
- no object identity check in deactivation;
- later FileTransferInit/progress/close paths also look up by `username + token`.

## Public overlap status

Current status: **candidate no direct public match found, but public transfer-lifecycle adjacent**.

Captured searches found public transfer-token/connection-timing and connection-state material, but not a direct report of the duplicate peer-supplied download token + stale timer active-map deletion invariant. The exact public-overlap notes are in `data/rev0007_public_overlap_u123.csv` and `evidence/rev0007-web-public-overlap-u123.md`.

## Coherent fix shape

The safest fix shape is a small transfer-session integrity patch, not an isolated dictionary tweak:

```text
1. In _activate_transfer() or the download TransferRequest handler:
   - if active_users[username][token] exists and is not the same transfer/session,
     reject or quarantine the newer request instead of overwriting the active entry.

2. In _deactivate_transfer():
   - only delete active_users[username][token] if the mapped object is exactly the
     transfer being deactivated.
   - if the key maps to a different transfer, clear only the stale transfer's local
     timer/token state and log the generation mismatch.

3. In FileTransferInit/progress/close handling:
   - preserve the existing username+token lookup for compatibility, but ensure the
     resulting transfer is still in the expected pending generation and socket state.
```

This fix is coherent with U-169/U-170. It is **not** a complete fix for U-158/UploadFailed/UploadDenied, because those status messages do not carry this transfer token in the current protocol shape.

## Strict-document decision

Not promoted. U-123 is now the top strict-candidate holding-pen item, but it still needs either:

- a socket-level F-connection harness showing the limbo state blocks or misbinds FileTransferInit/progress/close handling; or
- a maintainer-grade unit test accepted as sufficient for the transfer-session invariant.
