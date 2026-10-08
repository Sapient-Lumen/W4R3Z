# U-123 session-identity coherence refactor — rev0036

## Refactor decision

U-123 is now modeled as a **transfer-session identity** issue, not as a broad transfer subsystem or peer-connection election issue.

## Keep inside U-123

```text
- same-user/same-token duplicate download TransferRequest acceptance;
- active_users[username][token] overwrite by a later Transfer object;
- stale timeout/deactivation callback for the earlier Transfer object;
- deletion of the shared username+token map without object identity;
- FileTransferInit/progress/close callback routing through that map;
- availability/session-integrity impact boundary.
```

## Keep outside U-123

```text
- PB-01 direct/indirect PeerInit primary-election and secondary promotion;
- SEARCH-RESP-01 search response token/source/scope and parser-budget ordering;
- U-269 upload-complete lifetime after bytes are sent;
- U-271 transfer-control virtual-path budget;
- U-138 and other media-parser memory-budget rows;
- any protocol-wide change to token semantics.
```

## Compatibility split

The U-123 draft should discuss compatibility only where it affects the local transfer-session lifecycle:

```text
- delayed queued transfer becoming ready;
- retry/requeue/resume of the same transfer object;
- duplicate FileTransferInit on an already-active socket;
- stale request timers and user-watch lifetime.
```

The draft should not try to solve primary-connection replacement, distributed child promotion, search source binding, or media parser materialization. Those remain separate cube families.

## Linter result

Manual coherence linter for rev0036: no structural errors. The active queue has one U-123 production-draft packet, two held strict/front candidates, and one deferred media-parser row. No source bundles are embedded in the compact cube.
