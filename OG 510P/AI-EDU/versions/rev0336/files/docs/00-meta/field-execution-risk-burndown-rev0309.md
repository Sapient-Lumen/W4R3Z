# rev0309 field execution risk burndown

| Risk | rev0309 control | Residual boundary |
|---|---|---|
| A post-decision ticket carries a stale decision hash while pointing at a current-looking decision file. | `owner_post_decision_change_ticket_integrity_error()` now compares `source_first_packet_decision.decision_sha256` to the referenced file's current SHA-256. | Human review is still required; no decision record is evidence or closure. |
| A live-window entry/card carries a stale ticket hash while pointing at a current-looking ticket file. | Source-ticket validation now compares `source_post_decision_change_ticket.ticket_sha256` to the referenced file's current SHA-256. | Live-window records still require a real active-change chain and remain non-evidence. |
| Hash-bearing records create false confidence near activation. | Stale-hash regressions prove that copied snapshot metadata cannot pass the relevant handoff guard. | A real owner-reviewed packet is still absent. |
| The cube spends another pass on doctrine instead of execution. | The pass changes shared guards and two validator regressions, plus focused release docs only. | Next work should continue compressing the owner-return path, not growing registries. |

`FT-0181` remains live. This pass does not contact an owner, import a real CSV,
accept `SRC2+`, authorize a real active-change window, upgrade a public claim, or
close the followthrough.
