# Branch-family index and refactor map

Rev0225 adds a retrieval and refactor layer for the branch-history tail without moving historical files.

The audit found 100 branch-history surfaces under `docs/20-governance` whose filenames begin with `first-`, `portable-`, or `late-relapse-`. They remain valid historical surfaces, but they should no longer be treated as the main navigation path for new work. The machine index is [`BRANCH_FAMILY_INDEX.json`](../../BRANCH_FAMILY_INDEX.json).

## Why this exists

The cube already has a compression rule for serial repair and terminal dewatch. The remaining problem is retrieval: old branch-history files are numerous enough that maintainers can scan `docs/20-governance` and mistake a local continuation family for the canonical policy spine.

This map gives branch history a stable access layer while preserving path compatibility. It is a refactor, not a retirement.

## Family inventory

| Family | Count | Entry | Description |
|---|---:|---|---|
| `hot_exam_recipient_followup_shells` | 50 | [`preferred`](../../docs/20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md) | Long serial branch history for hot-exam recipient follow-up, repair, rewatch, dewatch, route stability, standing, migration, and residue cases. |
| `packet_maintenance_envelopes` | 11 | [`preferred`](../../docs/20-governance/portable-defaults-for-predeclared-packet-maintenance-envelopes.md) | Portable and late-relapse branches for packet-maintenance envelopes, promotion, cooldown, breach, and ordinary restoration. |
| `after_hours_service_truth_profiles` | 8 | [`preferred`](../../docs/20-governance/portable-quantitative-bands-for-promoted-after-hours-service-truth-profiles.md) | Portable and late-relapse branches for after-hours service-truth profiles, missed-window handling, repair, republishing, and return sensitivity. |
| `hot_exam_closure_reopen_reclosure` | 6 | [`preferred`](../../docs/20-governance/first-proof-mismatch-and-reopen-defaults-for-hot-exam-closure-fields.md) | Hot-exam proof mismatch, authoritative-update, reopen, reclosure, and official-disposition branches. |
| `hot_exam_delivery_request` | 4 | [`preferred`](../../docs/20-governance/first-request-status-and-submission-state-defaults-for-hot-exam-bounded-request-shells.md) | Hot-exam bounded request, fulfillment, recipient confirmation, and delivery-evidence surfaces. |
| `hot_exam_family_children` | 4 | [`preferred`](../../docs/20-governance/first-modality-child-splits-and-fallback-defaults-for-hot-exam-family-shells.md) | Hot-exam family, modality, phase-band, and shared-publication child surfaces. |
| `hot_exam_status_notice` | 4 | [`preferred`](../../docs/20-governance/first-status-vocabulary-and-escalation-crosswalk-defaults-for-hot-exam-notice-shells.md) | Hot-exam timing, notice, status vocabulary, transfer proof, and fulfillment status surfaces. |
| `override_child_branches` | 4 | [`preferred`](../../docs/20-governance/profile-hardening-application-rows.md) | Override-row and child-branch splits for direct production, writing, protected access, and local hardening. |
| `other_branch_history` | 3 | [`preferred`](../../docs/00-meta/branch-family-index-and-refactor-map.md) | Remaining branch-history surfaces that are still valid but should route through the family index before spawning siblings. |
| `hot_exam_late_outcomes` | 2 | [`preferred`](../../docs/20-governance/first-contestability-and-learner-facing-remedy-defaults-for-official-hot-exam-late-outcomes.md) | Official hot-exam late-outcome contestability, inspection, and learner-remedy surfaces. |
| `hot_exam_modality_children` | 2 | [`preferred`](../../docs/20-governance/first-route-failure-staffing-and-publication-minima-for-hot-exam-modality-children.md) | Hot-exam modality-child route failure, staffing, protected exposure, and incident-routing surfaces. |
| `recovery_authority_branches` | 2 | [`preferred`](../../docs/20-governance/portable-owner-facing-handback-packet-fields-for-recovery-authority-families.md) | Portable recovery-authority handback, review-window, substitute-path, and publication branches. |

## Use rule

Before adding another branch-history surface:

1. Search `BRANCH_FAMILY_INDEX.json` for the closest family.
2. Read the family entry and its preferred surface.
3. Check [`serial-repair-cycle-compression-and-terminal-dewatch-defaults.md`](../20-governance/serial-repair-cycle-compression-and-terminal-dewatch-defaults.md) if the case is serial, ordinal, relapse, repair, rewatch, dewatch, or residue-shaped.
4. Add a sibling only when the new case has a genuinely new material pattern that cannot be represented by family-level compression, existing terminal disposition, or route-native handling.

## Refactor posture

All indexed families currently use `archive_in_place_with_family_index`. That means:

- do not move the historical files yet;
- do not retire them merely because they are numerous;
- do not put them back into first-read paths;
- use the index and `SURFACES.json` for retrieval;
- prefer summary/compression rows over new ordinal shells.

Physical migration into a subdirectory should wait for a named maintenance failure, because it would require heavy link, audit, surface, and changelog churn.

## What not to infer

This map does not close `FT-0181`, does not prove any service works, and does not convert branch history into portable policy. It only makes the branch tail easier to scan and harder to extend accidentally.
