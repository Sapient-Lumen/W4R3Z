# rev0300 field execution risk burndown

| Risk | rev0300 control | Residual boundary |
|---|---|---|
| Terminal live-window card is mistaken for finished work | Router now emits `PREPARE-LIVE-WINDOW-READOUT-BRIEF` instead of treating the terminal card as sufficient | Human must still record the aggregate readout |
| Terminal card jumps directly to post-readout dispatch | Readout brief emits only `owner-live-window-readout` command skeletons | Post-readout dispatch still requires a real readout artifact |
| Dense readout command causes operator drop-off | `owner-live-window-readout-brief` preserves counts, source truth, and no-closure flags in a one-screen handoff | Human must choose the correct aggregate disposition |
| Safe-local helper stops too early after terminal carding | `owner-field-work` now handles bridge prep through terminal readout brief | It still refuses human send, route block, contact status, intake, review, decision, ticket, receipt, card, readout, custody, claims, lifecycle movement, and closure |
| Local artifacts masquerade as field evidence | New brief is `NOT_ACCEPTED` / `not_evidence` and scratch-local | Real SRC2+ owner-reviewed packet remains absent |

The highest priority after this revision is still external: run the next emitted
human-owned command from real field material, not another registry or doctrine
expansion.
