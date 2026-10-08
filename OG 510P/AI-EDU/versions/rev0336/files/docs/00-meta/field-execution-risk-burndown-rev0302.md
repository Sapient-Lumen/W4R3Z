# rev0302 field execution risk burndown

| Risk | rev0302 control | Residual boundary |
|---|---|---|
| A due post-readout dispatch is forgotten or treated as complete | Router now emits `PREPARE-POST-READOUT-RECHECK-BRIEF` on/after `due_or_recheck_date` | Human must still record the recheck |
| Dense recheck command causes operator drop-off | `owner-post-readout-recheck-brief` emits one-screen command skeletons for the four allowed outcomes | The brief itself is not a recheck |
| New owner context is copied into a local recheck | The new-context command requires `NEW_OWNER_CONTEXT_HELD_OUTSIDE_ARCHIVE=1` and the guard forbids raw/context/CSV shortcuts | Actual returned context must still re-enter through context receipt and intake |
| Recheck is mistaken for closure or service-record authority | All command skeletons carry no-expansion, no-public, no-service, no-lifecycle, and no-closure flags | Human action cannot bypass the context receipt/intake firebreak |
| Safe-local helper stops too early after a due dispatch | `owner-field-work` now handles bridge prep through post-readout recheck brief | It still refuses recheck recording, context receipt, custody, claims, lifecycle movement, and closure |

The highest priority after this revision remains external: when the due date arrives,
record the human recheck or route the real returned context file through the receipt
and intake path. Do not add another registry to compensate for missing field action.
