# State contracts

This file defines the field-level expectations that make the state API useful across surfaces.

## General rules

1. Every state payload should identify its `surface_key` and `browser_lane` either directly or through linked families.
2. Missing data should be represented honestly with null or `unknown`, not guessed.
3. Artifact references should be stable enough for a future implementer to inspect.
4. Timestamps should be included when the value is meaningfully time-sensitive.
5. A family may be absent, partial, or complete; that difference should be visible.

## Required core fields by family

### surface
Required:
- `surface_key`
- `is_supported`

Optional:
- `display_name`
- `url`
- `route_hint`
- `adapter_version_hint`

### session
Required:
- `browser_lane`

Optional:
- `session_id`
- `tab_id`
- `window_id`
- `frame_context`

### navigation
No field is always guaranteed.
Useful optional fields:
- `url_before`
- `url_after`
- `route_hint_before`
- `route_hint_after`
- `history_length_before`
- `history_length_after`
- `history_length_delta`
- `same_document_navigation_likely`
- `modal_or_overlay_state`
- `back_restored_prior_state`
- `forward_restored_prior_state`

### receiver
Required when present:
- `candidate_count`

Optional:
- `receiver_id`
- `role`
- `kind`
- `is_primary`
- `resolution_reason`
- `resolution_confidence`

### composer
Required when present:
- `is_empty`
- `is_editable`

Optional:
- `text`
- `char_count`
- `placeholder_hint`
- `selection_range`

### generation
Required when present:
- `status`

Optional:
- `can_stop`
- `progress_hint`
- `last_transition_at`

### conversation
No field is always guaranteed.
Useful optional fields:
- `conversation_id`
- `title_hint`
- `turn_count_hint`
- `is_new_conversation`

### turn
Required when present:
- `speaker`
- `is_partial`
- `is_latest`

Optional:
- `turn_id`
- `ordinal`
- `text`
- `block_kinds`

### diagnostics
No universal required field.
Useful optional fields:
- `worker_health`
- `native_connection`
- `coverage_audit`
- `receiver_audit`
- `warnings`
- `active_experiments`

### support
Useful optional fields:
- `surface_tier`
- `workflow_statuses`
- `last_verified_at`
- `evidence_refs`

### evidence
Required when present:
- `artifact_kind`

Optional:
- `artifact_path`
- `capture_id`
- `capture_time`
- `comparison_ref`

### action_outcome
Required:
- `action_kind`
- `attempted`
- `result`

Optional:
- `action_id`
- `target`
- `reason`
- `evidence_refs`

## Cross-family invariants

- `composer-write` should usually produce both `composer` and `action_outcome` updates.
- `turn-submit` should usually produce `action_outcome`, at least one post-submit `generation` read, and `navigation` when route continuity could have changed.
- `latest-turn-read` should not claim full success without a `turn` family instance.
- transient UI cues should not be the only basis for a successful `turn-submit`, `generation-read`, or `latest-turn-read` claim.
- `support-capture` should emit at least one `evidence` reference.
- `receiver` confidence should not be silently ignored when writing or submitting.

## Mapping guidance for current code

Current outputs from bridge, probe, proof, native-host, and attempt tooling should be gradually translated into these family contracts. The first goal is not perfect normalization; it is making the mapping visible and stable enough that future implementers do not start over.
