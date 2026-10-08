# Audited backlog addendum — rev0024

## TRANSFER-CONTROL-PATH-BUDGET-01 / U-271 + U-274 + U-256

**Status:** verified audited backlog.  
**Strict document:** not promoted.  
**Public overlap:** candidate no direct exact match found, but public-adjacent.

rev0024 confirms that transfer-control virtual-path strings cross several parser/handler boundaries before any shared semantic path/component budget is applied:

- `QueueUpload(file)`
- legacy `TransferRequest(direction=download, file)`
- `PlaceInQueueRequest(file)`
- `FolderContentsRequest(dir)`

The strongest behavior is the matching `PlaceInQueueRequest` and `FolderContentsRequest` response echo: a queued upload path can be echoed in `PlaceInQueueResponse`, and an unmatched folder request can still produce a compressed `FolderContentsResponse` carrying the requested directory prefix.

The recommended backlog framing is one shared transfer-control virtual-path parser/policy and bounded response echo behavior, not separate one-off caps.

## Queue/refactor impact

```text
U-271 = canonical transfer request lead.
U-274 = PlaceInQueueRequest subcase.
U-256 = FolderContentsRequest echo subcase.
U-272 = alias of U-256 only.
U-47  = older support context only.
```
