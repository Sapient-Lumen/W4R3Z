# Branch-tail freeze and pruning audit rev0267

Date: 2026-06-16
Revision: rev0267
Status: refactor/audit note; no files are removed in this revision; branch-history surfaces remain searchable but should not be first-read surfaces.

## Audit finding

The branch family plane is the largest obvious attention sink. `BRANCH_FAMILY_INDEX.json` currently detects 100 branch surfaces across 12 families. The largest family, `hot_exam_recipient_followup_shells`, contains 50 surfaces. The next largest family, `packet_maintenance_envelopes`, contains 11 surfaces.

That is not automatically wrong: those documents encode hard-won recovery patterns. The failure mode is reactivation. If historical branch files keep appearing in first-read paths, a maintainer can spend the session navigating relapse/rewatch/default shells instead of moving `FT-0181` toward a real owner packet.

## Family disposition

| Family | Count | Current disposition |
|---|---:|---|
| `hot_exam_recipient_followup_shells` | 50 | Retrieval only; do not add siblings without a live artifact failure. |
| `packet_maintenance_envelopes` | 11 | Retrieval only; use existing packet-maintenance compression before writing new defaults. |
| `after_hours_service_truth_profiles` | 8 | Retrieval only unless a real service route exposes after-hours owner ambiguity. |
| `hot_exam_closure_reopen_reclosure` | 6 | Retrieval only; current release closure remains governed by `FT-0181` evidence gates. |
| `hot_exam_delivery_request` | 4 | Retrieval only; not part of the active owner-packet lane. |
| `hot_exam_family_children` | 4 | Retrieval only; no startup-path role. |
| `hot_exam_status_notice` | 4 | Retrieval only; no startup-path role. |
| `override_child_branches` | 4 | Retrieval only; use existing override/profile surfaces first. |
| `other_branch_history` | 3 | Retrieval only; use `BRANCH_FAMILY_INDEX.json` for discovery. |
| `hot_exam_late_outcomes` | 2 | Retrieval only. |
| `hot_exam_modality_children` | 2 | Retrieval only. |
| `recovery_authority_branches` | 2 | Retrieval only unless a real owner packet raises recovery-authority ambiguity. |

## Freeze rule

No new `first-*`, `portable-*`, or `late-relapse-*` branch sibling should be created while `FT-0181` remains blocked unless all four conditions are true:

1. a real field artifact has arrived or a real bounded owner-contact attempt has failed;
2. the failure cannot be represented by the existing owner-request, triage, intake, workbench, custody, acceptance, closeout, recovery-drill, or public-claim surfaces;
3. the uncovered risk is named in one sentence; and
4. the new branch includes a compression/retirement target so it does not become permanent first-read doctrine.

If those conditions are not met, update `BRANCH_FAMILY_INDEX.json`, `SURFACES.json`, or an existing compression surface rather than adding a branch.

## Pruning without link breakage

This revision does not delete branch files because the archive already uses them for retrieval, references, and history. The safer refactor is priority demotion:

- keep branch files out of `START_HERE.md`, `AGENTS.md`, `context-pack.json`, and the first-read mission kernel;
- route branch discovery through `BRANCH_FAMILY_INDEX.json` only;
- prefer canonical compression surfaces when a family pattern is needed;
- treat branch file edits as repair-only unless a live artifact shows an uncovered risk.

## Decision for rev0267

The active kernel now points to this audit rather than to branch-history tails. This is a real refactor because it changes the maintainer's first-read path and reduces the chance that the next session spends its effort on relapse/default-shell expansion instead of owner evidence.

## Closure boundary

This audit does not close `FT-0181`, does not retire historical files, and does not prove a service claim. It only freezes the branch tail as retrieval history until field evidence creates a specific reason to reopen it.
