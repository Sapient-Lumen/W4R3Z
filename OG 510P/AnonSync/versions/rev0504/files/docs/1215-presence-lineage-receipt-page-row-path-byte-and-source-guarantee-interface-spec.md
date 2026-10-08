# Presence lineage receipt page — row, path, byte residency, and source guarantee

## Purpose

After any serious availability, placeholder, ghost-file, or delete-authority event, a later operator must be able to answer:

> what exactly existed here at the time — only a row, a bound path, placeholders, local bytes, or a proven source — and what stronger sentence was explicitly rejected?

This receipt exists so presence and fetchability do not dissolve into `connected`, `available`, or `removed` folklore.

## Receipt fields

### Identity

- `receipt_id`
- `subject_ref`
- `path_ref` nullable
- `created_at`

### Presence truth

- `presence_class` (`row_only`, `bound_path_unresolved`, `placeholder_only`, `mixed`, `fully_materialized`)
- `local_byte_coverage`
- `placeholder_count` nullable
- `materialized_count` nullable

### Source truth

- `source_guarantee_class` (`local_self_sufficient`, `live_remote_proven`, `remote_known_offline`, `source_unproven`, `ghost_namespace`)
- `source_dependency_class` (`none`, `parent_share`, `remote_peer`, `mixed`, `unresolved`)
- `source_proof_time` nullable

### Gesture authority

- `reviewed_gesture` nullable
- `gesture_authority_class` (`residency_only`, `materialize_allowed`, `shared_delete_allowed`, `shared_delete_blocked`, `manual_review_required`)
- `safety_rail_flags[]`
- `blast_radius_grade`

### Claim ceiling

- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `reopen_conditions[]`

## Required behavior

The receipt must be emitted whenever:

- an object is shown in UI without full local byte residency;
- placeholder-backed content is presented as available for on-demand use;
- a no-source or ghost-file warning materially changes fetchability truth;
- a delete-like gesture is reviewed on placeholder-backed content;
- a child or local share depends on a parent source for byte materialization.

## Forbidden simplifications

The receipt must never flatten the event into:

- `available`
- `connected`
- `synced`
- `placeholder`
- `removed`

unless the structured presence, source, authority, and blocked-sentence fields remain inspectable alongside that summary.
