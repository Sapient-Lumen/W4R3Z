# rev0298 field execution risk burndown

| Risk | rev0298 control | Residual boundary |
|---|---|---|
| Ready-for-real-packet stalls before activation receipt | `owner-activation-live-window-brief` prepares a one-screen same-source activation handoff | Human must supply the same real owner-reviewed SRC2+ source packet and record the activation receipt |
| Ready-for-real-packet is mistaken for live-window authority | Ready brief emits no `owner-live-window-card` command | Live-window card still requires active_change after activation receipt |
| Active-change ticket is mistaken for an already-started window | Active brief emits bounded live-window card command skeletons and preserves stop/rollback controls | Human must choose and record the actual card; the brief records no window |
| Safe-local helper stops too early after post-decision ticketing | `owner-field-work` now handles bridge prep through activation/live-window entry brief | It still refuses human send, route block, contact status, intake, review, decision, ticket, receipt, card, custody, claims, lifecycle movement, and closure |
| Local artifacts masquerade as field evidence | New brief is `NOT_ACCEPTED` / `not_evidence` and scratch-local | Real SRC2+ owner-reviewed packet remains absent |

The highest priority after this revision is still external: run the next emitted
human-owned command from real field material, not another registry or doctrine
expansion.
