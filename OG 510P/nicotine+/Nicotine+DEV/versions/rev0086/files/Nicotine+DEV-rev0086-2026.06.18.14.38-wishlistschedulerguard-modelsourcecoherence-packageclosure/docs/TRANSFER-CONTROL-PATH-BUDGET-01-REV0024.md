# TRANSFER-CONTROL-PATH-BUDGET-01 — rev0024

Canonical rows: **U-271 + U-274 + U-256**.  
Continuity/support rows: **U-272** as duplicate/alias of U-256, and **U-47** as older place-in-queue amplification context.

## Decision

**Verified audited-backlog packet; not promoted to the strict document.**

The behavior is real in all checked source lanes, but the consequence is low/medium availability and transfer-control hardening. The sender must already be able to send peer messages, request bytes are proportional to the oversized path except for the compressed response echo case, and public discussion/PR material is adjacent enough that this should not be presented as clean novelty.

## What rev0024 proved

The maintainer-style witness ran against:

```text
github-tag-3.3.10:   6 passed
github-branch-3.3.x: 6 passed
github-branch-master: 6 passed
```

The witness uses a 256 KiB component path and a 4098-component deep path. It confirms:

```text
QueueUpload:
  parses and preserves the oversized virtual path;
  reaches share lookup and upload queue keying under that full path.

Legacy TransferRequest direction=download:
  parses and preserves the oversized virtual path;
  reaches legacy upload-request handling and response context.

PlaceInQueueRequest:
  parses and preserves the oversized virtual path;
  when the same path is already queued, performs queued_users lookup;
  emits PlaceInQueueResponse echoing the full requested path.

FolderContentsRequest:
  parses and preserves the oversized requested directory;
  handler emits FolderContentsResponse with the same directory and token;
  even an unmatched folder produces a compressed response containing the full path prefix.

Deep path baseline:
  transfer-control parsers preserve a 4098-component path without component-count rejection.
```

The metrics are stable across all three lanes for the 256 KiB component witness:

```text
path_utf8_bytes:                         262161
QueueUpload wire bytes:                  262165
PlaceInQueueRequest wire bytes:          262165
PlaceInQueueResponse wire bytes:         262169
legacy TransferRequest wire bytes:       262173
FolderContentsRequest wire bytes:        262169
FolderContentsResponse compressed bytes: 311
FolderContentsResponse raw bytes:        262173
```

The compressed FolderContentsResponse metric is why U-256 is retained in the same packet: the request is proportional, but the response can carry a large uncompressed peer-visible directory prefix in a highly compressed frame.

## Public-overlap result

No direct exact public report was found for the combined current-behavior invariant. However, this is **public-adjacent**:

- PR #3741 is a draft public virtual-path/component validation PR covering scan/search/folder/browse result/list surfaces.
- Discussion #1997 explicitly mentions repeated `QueueUpload` and `PlaceInQueueRequest` messages.
- U-47 already exists as older place-in-queue amplification context inside the seed corpus.

Therefore rev0024 marks the packet as **candidate no direct exact public match found / public-adjacent**, not as a clean fresh issue.

## Coherent fix shape

Do not make three or four separate ad hoc caps. The coherent fix is a shared transfer-control virtual-path policy with call-site-specific response behavior:

```text
Shared parser/policy:
  parse_transfer_control_virtual_path(raw/string, legacy=False, context=...)
  cap total bytes/characters;
  cap component count;
  cap component bytes;
  reject or sanitize C0/C1 controls and bidi controls where appropriate;
  decide how to handle leading/trailing separators/backslash sentinels and legacy clients.

QueueUpload + legacy TransferRequest:
  reject before share lookup, lowercase/backslash fallback, transfer-key construction, plugin notification, and logging;
  use a bounded denial reason that does not echo the full path.

PlaceInQueueRequest:
  reject before queued_users lookup and queue-position computation;
  do not send PlaceInQueueResponse for over-budget paths;
  if logging, log a bounded path summary.

FolderContentsRequest:
  reject before share_dbs lookup and response construction;
  do not echo over-budget directories into FolderContentsResponse;
  if compatibility requires a response, send a bounded empty/error response without the full path.
```

## Why not strict

This is worth keeping because it completes a repeated design flaw across transfer-control request paths. It is not a fourth strict candidate because the strongest result is bounded availability/resource hardening, and the public path-validation conversation is already active enough to make novelty/credit risky.
