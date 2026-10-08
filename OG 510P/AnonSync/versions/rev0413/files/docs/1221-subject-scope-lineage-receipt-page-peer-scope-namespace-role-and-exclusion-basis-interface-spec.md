# Subject-scope lineage receipt page — peer scope, namespace role, and exclusion basis

## Purpose

After any serious ignore dispute, hidden-file confusion, service-artifact deletion scare, or `why is share size different here?` event, a later operator must be able to answer:

> what role did this pathname have here at the time — ordinary user subject, peer-excluded subject, UI-hidden subject, service artifact, metadata sidecar, temp residue, or invalid-name block — and what stronger sentence was explicitly rejected?

This receipt exists so scope truth does not dissolve into `ignored`, `hidden`, `not syncing`, or `safe to delete` folklore.

## Receipt fields

### Identity

- `receipt_id`
- `subject_ref`
- `path_ref`
- `created_at`

### Role truth

- `namespace_role` (`ordinary_user`, `peer_excluded`, `ui_hidden_only`, `service_critical`, `transfer_temp`, `metadata_sidecar`, `invalid_name_blocked`, `unresolved`)
- `visibility_class` (`ui_visible`, `ui_hidden_only`, `disk_visible_not_shown`, `not_materialized`, `unresolved`)
- `scope_membership_class` (`indexed_in_scope`, `ignore_excluded`, `name_invalid_excluded`, `service_owned_excluded`, `temp_excluded`, `metadata_lane_separate`, `unresolved`)

### Counting and divergence

- `count_participation_class` (`counted`, `structurally_known_not_counted`, `not_indexed_not_counted`, `service_only`, `unresolved`)
- `peer_divergence_class` (`peer_local_only`, `shared_policy`, `role_local_bytes_shared`, `potential_divergence_unchecked`, `unresolved`)
- `retroactivity_class` (`pre_scan`, `post_scan_structural_survivor`, `rule_not_yet_re_read`, `not_applicable`, `unresolved`)

### Handling truth

- `manipulation_safety_class` (`ordinary_user_handling`, `review_before_delete`, `service_do_not_touch`, `temp_residue_review`, `invalid_name_repair_first`)
- `repair_cost_grade`
- `next_proof_action` nullable

### Claim ceiling

- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `reopen_conditions[]`

## Required behavior

The receipt must be emitted whenever:

- a pathname is excluded by IgnoreList or other scope policy after a scope dispute;
- hidden-file UI policy materially affects an operator conclusion;
- `.sync`, `Streams`, `IgnoreList`, or `.!sync` artifacts are reviewed for deletion or diagnosis;
- peer-local ignore divergence plausibly explains size or object-count mismatch;
- an unsupported name is diagnosed as the true reason a subject is not behaving like an ordinary file.

## Forbidden simplifications

The receipt must never flatten the event into:

- `ignored`
- `hidden`
- `service file`
- `temp file`
- `not syncing`
- `safe to delete`

unless the structured role, scope, divergence, safety, and blocked-sentence fields remain inspectable alongside that summary.

