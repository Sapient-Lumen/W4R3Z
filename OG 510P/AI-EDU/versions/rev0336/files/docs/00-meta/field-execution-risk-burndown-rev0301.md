# rev0301 field execution risk burndown

| Risk | rev0301 control | Residual boundary |
|---|---|---|
| Terminal aggregate readout is mistaken for closure | Router now emits `PREPARE-POST-READOUT-ACTION-BRIEF` instead of treating the readout as sufficient | Human must still record the dispatch |
| Readout jumps directly to owner-action completion or recheck | Action brief emits only `owner-post-readout-action` command skeletons | Recheck still requires an action dispatch and due/recheck date |
| Dense dispatch command causes operator drop-off | `owner-post-readout-action-brief` preserves lane mapping, source truth, due date, and firebreak flags in a one-screen handoff | Human must choose/record the dispatch |
| Safe-local helper stops too early after readout | `owner-field-work` now handles bridge prep through post-readout action brief | It still refuses dispatch, owner action, recheck, context receipt, custody, claims, lifecycle movement, and closure |
| Local artifacts masquerade as field evidence | New brief is `NOT_ACCEPTED` / `not_evidence` and scratch-local | Real SRC2+ owner-reviewed packet remains absent |

The highest priority after this revision is still external: run the next emitted
human-owned command from real field material, not another registry or doctrine
expansion.
