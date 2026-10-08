# State API

GlassTTY needs a structured browser state API shared across official surfaces.

## State families

### surface
Identity and coarse classification of the current browser surface.
Example fields:
- `surface_key`
- `display_name`
- `url`
- `route_hint`
- `is_supported`
- `adapter_version_hint`

### session
Session-level metadata.
Example fields:
- `session_id`
- `tab_id`
- `window_id`
- `frame_context`
- `browser_lane`

### navigation
Route and browser-history continuity state.
Example fields:
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
The current compose/interaction target.
Example fields:
- `receiver_id`
- `role`
- `kind`
- `is_primary`
- `resolution_reason`
- `resolution_confidence`
- `candidate_count`

### composer
Prompt-draft state.
Example fields:
- `text`
- `char_count`
- `is_empty`
- `is_editable`
- `placeholder_hint`
- `selection_range`

### generation
Current response-generation status.
Example fields:
- `status`
- `can_stop`
- `progress_hint`
- `last_transition_at`

### conversation
Conversation-level identifiers and metadata when available.
Example fields:
- `conversation_id`
- `title_hint`
- `turn_count_hint`
- `is_new_conversation`

### turn
A structured read of one conversation turn.
Example fields:
- `turn_id`
- `speaker`
- `ordinal`
- `text`
- `block_kinds`
- `is_partial`
- `is_latest`

### selection
Selection or highlighted-subtree state when available.
Example fields:
- `selection_text`
- `range_hint`
- `origin_family`
- `is_collapsed`

### diagnostics
Health and explainability state.
Example fields:
- `worker_health`
- `native_connection`
- `coverage_audit`
- `receiver_audit`
- `warnings`
- `active_experiments`

### support
Current support-truth classification.
Example fields:
- `surface_tier`
- `workflow_statuses`
- `last_verified_at`
- `evidence_refs`

### evidence
Pointers to durable artifacts.
Example fields:
- `artifact_kind`
- `artifact_path`
- `capture_id`
- `capture_time`
- `comparison_ref`

### action_outcome
Standard result shape for meaningful actions.
Example fields:
- `action_id`
- `action_kind`
- `target`
- `attempted`
- `result`
- `reason`
- `evidence_refs`

## Degradation rules

- Unknown is better than fake precision.
- Nullability should be explicit and expected.
- Surfaces may implement core families before secondary families.
- Structured state should preserve why a value is missing where possible.

## Where the field contract lives

Use `docs/state-contracts.md` for:
- required vs optional fields
- family-level invariants
- timestamp and reference expectations
- navigation-truth and transient-cue guidance
- guidance for mapping current outputs into the future schema

## Important consequence

Future features should prefer extending these families over inventing surface-specific blobs that cannot be compared across adapters.
