# rev0297 field execution risk burndown

| Risk | rev0297 control | Residual boundary |
|---|---|---|
| First-packet decision stalls before bounded ticketing | `owner-post-decision-change-ticket-brief` prepares a one-screen ticket handoff and bounded command skeletons | Human must choose and record the actual post-decision change ticket |
| Readiness gets confused with active change | Brief separates ready-for-real-packet routes from active-change-after-activation-receipt route | Active change still requires a real SRC2+ packet and valid activation receipt |
| Safe-local helper remains too narrow after decision-brief prep | `owner-field-work` now handles safe bridge prep through the post-decision ticket brief | It still refuses human send, route block, contact status, intake, review, decision, ticket, custody, claims, live-window, and closure |
| Local artifacts masquerade as field evidence | All new artifacts are `NOT_ACCEPTED` / `not_evidence` and scratch-local | Real SRC2+ owner-reviewed packet remains absent |

The highest priority after this revision is still external: run the next emitted
human-owned command from real field material, not another registry or doctrine
expansion.
