# Source hierarchy, conflict, refresh, and current-law ladder

## Question in one sentence

How should the archive maintain source quality as law, guidance, data, and implementation facts change?[S59][S594]

## Companion routes

Use this memo with:

- [`../10-framework/source-hierarchy-conflict-refresh-and-current-law-routing.md`](../10-framework/source-hierarchy-conflict-refresh-and-current-law-routing.md)
- [`../10-framework/decision-procedure.md`](../10-framework/decision-procedure.md)
- [`cube-lifecycle-pruning-route-retirement-and-evidence-refresh-ladder.md`](cube-lifecycle-pruning-route-retirement-and-evidence-refresh-ladder.md)

## Option scan

| Option | Shape | Archive verdict |
|---|---|---|
| A — primary source refresh | statute, regulation, treaty, official notice, agency guidance, or court decision. | Default for current-law claims. |
| B — authoritative data refresh | official statistics, administrative data, audited reports. | Use for incidence, scale, and performance. |
| C — news marker | reporting that identifies an event or controversy. | Use as pointer, not operative law. |
| D — scholarship/mechanism source | academic or expert analysis. | Use for mechanism and debate. |
| E — speculative frontier marker | explicitly uncertain future-facing inference. | Use with review trigger and no finality. |

## Ten-gate ladder

1. **claim gate** — state whether the sentence is current law, empirical fact, mechanism, judgment, or speculation.
2. **primary gate** — for legal status, prefer primary or official sources over summaries.
3. **date gate** — record effective dates, proposal/final status, and implementation dates.
4. **conflict gate** — when sources disagree, name the disagreement rather than averaging it.
5. **staleness gate** — classify unchanged doctrine, changed facts, or obsolete implementation.
6. **load-bearing gate** — remove sources that do not support a necessary proposition.
7. **trace gate** — keep enough local source IDs for offline archive use.
8. **frontier gate** — label speculation and assign a review trigger.
9. **pruning gate** — merge routes when evidence refresh does not change routing output.
10. **review gate** — reopen on legal change, source staleness, conflicting authority, or broken link.
11. **currentness-promotion gate** — before adding a source to `source_currentness_refs`, state the current claim and review reason; if no such claim exists, keep the source as an ordinary citation only.
12. **registry-use gate** — every source-currentness registry entry must be tracked by at least one route, or it is release clutter rather than currentness control.

## Default settings

| Posture | Instrument | Guardrail |
|---|---|---|
| legal status | primary/official refresh | effective date included and currentness claim recorded. |
| performance fact | authoritative data | uncertainty stated. |
| recent event | news plus official follow-up | do not treat news as law. |
| speculative forecast | frontier marker | review trigger required. |

## Accountability capsule

Authoritative assignment: route `source_hierarchy_conflict_refresh_current_law` in [`actor-accountability-profiles.json`](../00-meta/actor-accountability-profiles.json).

- Duty owner: `archive_maintainer_source_reviewer_or_current_law_owner_with_primary_source_hierarchy_and_conflict_resolution_control`.
- Rent/benefit trace: `archive_user_public_body_or_downstream_policy_evaluator_saved_from_stale_lower_authority_or_laundered_current_law_claims`.
- Bottleneck/evidence: `source_hierarchy_rule_and_primary_source_inventory; conflict_note_and_authority_rank_log +2 more`; evidence starts with `primary_source_rank_effective_date_and_legal_status_record; conflicting_authority_comparison_and_resolution_note +4 more`.
- Fallback duty: `archive_maintainer_must_preserve_fallback_conflict_notes_source_hierarchy_links_and_nonreliance_warning_when current_law is volatile_or_unresolved`.


## Source IDs only

[S59][S594]

[S59]: ../../SOURCES.md#S59
[S594]: ../../SOURCES.md#S594
