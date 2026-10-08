# Cooperation Benchmark Card Taxonomy

Generated registry for the stable compact-card identifiers that appear across inventory, heads, review, citation, next-action, and execution-lane surfaces. This prevents reason-code / action-kind / lane-id drift from becoming inheritor guesswork.

- category_count: 19
- token_count: 103

## Category summary

| category_id | tokens | field_refs |
|---|---:|---|
| `inventory_drift_reason_codes` | 8 | `freeze_receipts[].drift_reason_codes`; `delta_receipts[].drift_reason_codes` |
| `head_warning_reason_codes` | 7 | `heads.lineages[].warning_reason_codes`; `control_plane.lineages[].warning_reason_codes` |
| `citation_reason_codes` | 8 | `citation_surface.unresolved_lineages[].reason_codes`; `control_plane.lineages[].citation_reason_codes`; `handoff_pack.unresolved_lineages[].reason_codes` |
| `review_item_kinds` | 5 | `review_queue.items[].item_kind`; `macro_review_queue.groups[].item_kinds[]`; `control_plane.lineages[].review_item_kinds` |
| `review_reason_codes` | 24 | `review_queue.items[].reason_codes`; `macro_review_queue.groups[].reason_codes`; `control_plane.lineages[].review_reason_codes`; `next_action_witness.candidates[].reason_codes`; `next_action.primary_action.reason_codes` |
| `next_action_kinds` | 3 | `next_action.primary_action.action_kind`; `next_action_witness.candidates[].action_kind` |
| `next_action_priority_keys` | 7 | `next_action_witness.candidates[].priority_bucket`; `next_action_witness.candidates[].priority_label` |
| `next_action_selector_kinds` | 1 | `next_action_witness.selector_kind` |
| `next_action_selection_statuses` | 2 | `next_action.primary_action.selection_status` |
| `next_action_winner_uniqueness` | 2 | `next_action_witness.winner_uniqueness` |
| `execution_lane_ids` | 2 | `execution_lanes.lanes[].lane_id`; `next_action_witness.selected_command_ladder[].required_lane_id`; `next_action.primary_action.required_lane_id`; `next_action.primary_action.command_ladder[].required_lane_id`; `control_plane.recommended_next_command_lane_id` |
| `focus_open_target_role_codes` | 5 | `control_plane.focus_open_targets[].role_codes[]`; `next_action_witness.focus_open_targets[].role_codes[]`; `next_action.focus_open_targets[].role_codes[]` |
| `selected_command_open_target_role_codes` | 3 | `next_action_witness.selected_next_command_open_target.role_codes[]`; `next_action_witness.selected_fallback_command_open_target.role_codes[]`; `next_action_witness.selected_command_ladder[].open_target.role_codes[]`; `next_action.primary_action.target_open_target.role_codes[]`; `next_action.primary_action.fallback_open_target.role_codes[]`; `next_action.primary_action.command_ladder[].open_target.role_codes[]` |
| `handoff_pack_entry_target_role_codes` | 6 | `handoff_pack.packs[].entry_targets[].role_codes[]` |
| `focus_primary_command_target_role_codes` | 4 | `control_plane.focus_primary_verify_target.role_codes[]`; `control_plane.focus_primary_refresh_target.role_codes[]`; `next_action_witness.focus_primary_verify_target.role_codes[]`; `next_action_witness.focus_primary_refresh_target.role_codes[]`; `next_action.focus_primary_verify_target.role_codes[]`; `next_action.focus_primary_refresh_target.role_codes[]` |
| `handoff_pack_primary_command_target_role_codes` | 4 | `handoff_pack.packs[].primary_verify_target.role_codes[]`; `handoff_pack.packs[].primary_refresh_target.role_codes[]` |
| `focus_primary_command_effect_codes` | 2 | `control_plane.focus_primary_verify_effect_code`; `control_plane.focus_primary_refresh_effect_code`; `next_action_witness.focus_primary_verify_effect_code`; `next_action_witness.focus_primary_refresh_effect_code`; `next_action.focus_primary_verify_effect_code`; `next_action.focus_primary_refresh_effect_code` |
| `handoff_pack_primary_command_effect_codes` | 2 | `handoff_pack.packs[].primary_verify_effect_code`; `handoff_pack.packs[].primary_refresh_effect_code` |
| `execution_blocking_reason_codes` | 8 | `execution_lanes.lanes[].blocking_reason_codes`; `next_action_witness.selected_command_ladder[].required_lane_blocking_reason_codes`; `next_action.primary_action.required_lane_blocking_reason_codes`; `next_action.primary_action.command_ladder[].required_lane_blocking_reason_codes` |

## Category details

### `inventory_drift_reason_codes`

Fail-closed receipt drift reasons emitted by the compact-card inventory.

- field_refs: `freeze_receipts[].drift_reason_codes`, `delta_receipts[].drift_reason_codes`

| token | summary | metadata |
|---|---|---|
| `delta-new-card-missing` | The successor card path recorded in a delta receipt no longer exists. | — |
| `delta-new-card-sha-drift` | The successor card bytes no longer match the retained delta receipt hash. | — |
| `delta-old-card-missing` | The predecessor card path recorded in a delta receipt no longer exists. | — |
| `delta-old-card-sha-drift` | The predecessor card bytes no longer match the retained delta receipt hash. | — |
| `freeze-card-missing` | The card path recorded in a freeze receipt no longer exists. | — |
| `freeze-card-sha-drift` | The current card bytes no longer match the retained freeze receipt hash. | — |
| `freeze-render-missing` | The rendered markdown path recorded in a freeze receipt no longer exists. | — |
| `freeze-render-sha-drift` | The current rendered markdown bytes no longer match the retained freeze receipt hash. | — |

### `head_warning_reason_codes`

Lineage-head warnings emitted by the heads register and carried into the control plane.

- field_refs: `heads.lineages[].warning_reason_codes`, `control_plane.lineages[].warning_reason_codes`

| token | summary | metadata |
|---|---|---|
| `branch-ambiguous` | The lineage component has multiple tips or branching successors. | — |
| `latest-operational-head-freeze-drift` | The unique operational head only has drifted freeze receipts and needs a fresh guarded freeze. | — |
| `latest-operational-head-needs-freeze` | The unique operational head is claim-ready but still lacks a verified freeze receipt. | — |
| `multiple-citation-heads` | More than one frozen claim-ready latest-known card is competing to be the citation head. | — |
| `multiple-operational-heads` | More than one claim-ready latest-known card is competing to be the operational head. | — |
| `multiple-roots` | The lineage component has more than one root card. | — |
| `no-claim-ready-operational-head` | No claim-ready latest-known card can serve as the operational head. | — |

### `citation_reason_codes`

Reasons a lineage is excluded from the fail-closed citation surface.

- field_refs: `citation_surface.unresolved_lineages[].reason_codes`, `control_plane.lineages[].citation_reason_codes`, `handoff_pack.unresolved_lineages[].reason_codes`

| token | summary | metadata |
|---|---|---|
| `ambiguous-lineage-basis` | A citation-head predecessor step is not singular, so the retained lineage basis is ambiguous. | — |
| `citation-basis-drift` | A retained delta receipt exists for the lineage basis but no longer matches current card bytes. | — |
| `lineage-basis-cycle` | Walking retained delta ancestry for the citation head encountered a cycle. | — |
| `missing-lineage-delta-receipt` | A required retained delta receipt is missing from the lineage basis. | — |
| `missing-verified-freeze-receipt` | No verified freeze receipt currently binds the citation head. | — |
| `multiple-verified-delta-receipts` | More than one verified retained delta receipt claims to advance into the same card. | — |
| `multiple-verified-freeze-receipts` | More than one verified freeze receipt claims authority over the same citation head. | — |
| `no-unique-citation-head` | The lineage does not currently have one unique citation head. | — |

### `review_item_kinds`

Actionable row kinds emitted by the flat and macro compact-card review queues.

- field_refs: `review_queue.items[].item_kind`, `macro_review_queue.groups[].item_kinds[]`, `control_plane.lineages[].review_item_kinds`

| token | summary | metadata |
|---|---|---|
| `delta_drift` | Retained delta-basis evidence drifted and needs refresh. | — |
| `freeze_drift` | Retained freeze evidence drifted and needs refresh. | — |
| `freeze_needed` | Unique operational head needs a guarded freeze to regain a citation head. | — |
| `readiness_lint` | Schema-valid card still fails claim-readiness lint. | — |
| `topology_review` | Lineage topology or head state blocks a straightforward citation answer. | — |

### `review_reason_codes`

Reason codes carried by compact-card review items and grouped review lineages.

- field_refs: `review_queue.items[].reason_codes`, `macro_review_queue.groups[].reason_codes`, `control_plane.lineages[].review_reason_codes`, `next_action_witness.candidates[].reason_codes`, `next_action.primary_action.reason_codes`

| token | summary | metadata |
|---|---|---|
| `ambiguous-lineage-basis` | Citation lineage basis is not singular. | — |
| `branch-ambiguous` | Lineage topology is branch-ambiguous. | — |
| `citation-basis-drift` | Citation lineage basis depends on drifted delta evidence. | — |
| `claim-not-ready` | Card is still draft-valid rather than claim-ready. | — |
| `delta-new-card-missing` | Delta receipt successor card path is missing. | — |
| `delta-new-card-sha-drift` | Delta receipt successor card hash drifted. | — |
| `delta-old-card-missing` | Delta receipt predecessor card path is missing. | — |
| `delta-old-card-sha-drift` | Delta receipt predecessor card hash drifted. | — |
| `freeze-card-missing` | Freeze receipt points at a missing card. | — |
| `freeze-card-sha-drift` | Freeze receipt card hash no longer matches current bytes. | — |
| `freeze-render-missing` | Freeze receipt points at missing rendered markdown. | — |
| `freeze-render-sha-drift` | Freeze receipt render hash no longer matches current bytes. | — |
| `latest-operational-head-freeze-drift` | Operational head only has drifted freeze evidence. | — |
| `latest-operational-head-needs-freeze` | Operational head needs a guarded freeze. | — |
| `lineage-basis-cycle` | Citation lineage basis contains a cycle. | — |
| `missing-lineage-delta-receipt` | Citation lineage basis is missing a required delta receipt. | — |
| `missing-verified-freeze-receipt` | No verified freeze receipt currently binds the citation head. | — |
| `multiple-citation-heads` | More than one citation head candidate exists. | — |
| `multiple-operational-heads` | More than one operational head candidate exists. | — |
| `multiple-roots` | Lineage topology has multiple roots. | — |
| `multiple-verified-delta-receipts` | More than one verified delta receipt claims the same successor. | — |
| `multiple-verified-freeze-receipts` | More than one verified freeze receipt claims the same card. | — |
| `no-claim-ready-operational-head` | No claim-ready operational head exists. | — |
| `no-unique-citation-head` | Citation surface cannot name one unique citation head. | — |

### `next_action_kinds`

Top-level action kinds that can win compact-card first reentry.

- field_refs: `next_action.primary_action.action_kind`, `next_action_witness.candidates[].action_kind`

| token | summary | metadata |
|---|---|---|
| `inspect_unresolved_citation` | Inspect unresolved citation/control-plane state before inheriting claims. | — |
| `review_lineage` | Enter grouped lineage repair work before trusting citation / handoff surfaces. | — |
| `verify_ready_surface` | Verify the ready-state fused surface before proceeding. | — |

### `next_action_priority_keys`

Stable priority policy inputs for first-reentry selection.

- field_refs: `next_action_witness.candidates[].priority_bucket`, `next_action_witness.candidates[].priority_label`

| token | summary | metadata |
|---|---|---|
| `delta_drift` | Refresh retained delta-basis evidence first. | `{"priority_bucket": 0, "priority_label": "refresh-delta-basis"}` |
| `freeze_drift` | Refresh retained freeze evidence before other work. | `{"priority_bucket": 1, "priority_label": "refresh-freeze-basis"}` |
| `freeze_needed` | Guard-freeze the current head once retained evidence is current. | `{"priority_bucket": 2, "priority_label": "freeze-current-head"}` |
| `inspect_unresolved_citation` | Inspect unresolved citation state when no grouped review queue exists. | `{"priority_bucket": 5, "priority_label": "inspect-unresolved-citation"}` |
| `readiness_lint` | Finish claim-readiness work after structural issues. | `{"priority_bucket": 4, "priority_label": "finish-claim-readiness"}` |
| `topology_review` | Resolve lineage topology/head ambiguity next. | `{"priority_bucket": 3, "priority_label": "resolve-lineage-topology"}` |
| `verify_ready_surface` | Ready-state verification sits at the lowest urgency bucket. | `{"priority_bucket": 90, "priority_label": "verify-ready-surface"}` |

### `next_action_selector_kinds`

Selectors that are allowed to choose the compact-card first command.

- field_refs: `next_action_witness.selector_kind`

| token | summary | metadata |
|---|---|---|
| `priority_bucket_then_candidate_id` | Choose the lowest priority bucket, then break ties by stable candidate id ordering. | — |

### `next_action_selection_statuses`

Selection outcomes preserved on the primary next-action surface.

- field_refs: `next_action.primary_action.selection_status`

| token | summary | metadata |
|---|---|---|
| `stable-tie-break` | The chosen candidate won by stable tie-break within the winning priority bucket. | — |
| `unique-highest-priority` | The chosen candidate was the only candidate in the winning priority bucket. | — |

### `next_action_winner_uniqueness`

Witness-level uniqueness states preserved for the winning next-action bucket.

- field_refs: `next_action_witness.winner_uniqueness`

| token | summary | metadata |
|---|---|---|
| `stable-tie-break` | The winning bucket had multiple candidates and the selector chose a stable representative. | — |
| `unique-highest-priority` | The winning bucket had one candidate. | — |

### `execution_lane_ids`

Stable lane identifiers for environment-honest compact-card validation.

- field_refs: `execution_lanes.lanes[].lane_id`, `next_action_witness.selected_command_ladder[].required_lane_id`, `next_action.primary_action.required_lane_id`, `next_action.primary_action.command_ladder[].required_lane_id`, `control_plane.recommended_next_command_lane_id`

| token | summary | metadata |
|---|---|---|
| `python-integrity` | Surface-integrity lane for report build/check work. | — |
| `rust-harness` | Deeper engine / harness lane for Rust-backed validation. | — |

### `focus_open_target_role_codes`

Role codes explaining why a retained path appears in the focus-open target family.

- field_refs: `control_plane.focus_open_targets[].role_codes[]`, `next_action_witness.focus_open_targets[].role_codes[]`, `next_action.focus_open_targets[].role_codes[]`

| token | summary | metadata |
|---|---|---|
| `citation-card` | This path is the machine-readable citation head card. | — |
| `citation-rendered-markdown` | This path is the rendered markdown companion for the focus citation head. | — |
| `operational-card` | This path is the machine-readable operational head card. | — |
| `operational-rendered-markdown` | This path is the rendered markdown companion for the focus operational head. | — |
| `primary-open` | This path is the preferred first retained file to open for the focus lineage. | — |

### `selected_command_open_target_role_codes`

Role codes explaining why a retained path appears as the selected next-step or first-fallback inspect target.

- field_refs: `next_action_witness.selected_next_command_open_target.role_codes[]`, `next_action_witness.selected_fallback_command_open_target.role_codes[]`, `next_action_witness.selected_command_ladder[].open_target.role_codes[]`, `next_action.primary_action.target_open_target.role_codes[]`, `next_action.primary_action.fallback_open_target.role_codes[]`, `next_action.primary_action.command_ladder[].open_target.role_codes[]`

| token | summary | metadata |
|---|---|---|
| `selected-command-ladder-open` | This path is the retained document to open after a concrete rung in the selected command ladder completes. | — |
| `selected-fallback-command-open` | This path is the preferred retained document to open immediately after the first fallback command completes. | — |
| `selected-next-command-open` | This path is the preferred retained document to open immediately after the selected next command completes. | — |

### `handoff_pack_entry_target_role_codes`

Role codes explaining why a retained path appears in the handoff-pack entry target family.

- field_refs: `handoff_pack.packs[].entry_targets[].role_codes[]`

| token | summary | metadata |
|---|---|---|
| `citation-card` | This path is the machine-readable citation head card in the pack basis. | — |
| `citation-freeze-receipt` | This path is the verified freeze receipt that binds the pack citation head. | — |
| `citation-rendered-markdown` | This path is the rendered markdown companion for the pack citation head. | — |
| `operational-card` | This path is the machine-readable operational head card in the pack basis. | — |
| `operational-rendered-markdown` | This path is the rendered markdown companion for the pack operational head. | — |
| `primary-open` | This path is the preferred first retained file to open from the handoff pack. | — |

### `focus_primary_command_target_role_codes`

Role codes explaining what the direct focus verify/refresh command targets are for.

- field_refs: `control_plane.focus_primary_verify_target.role_codes[]`, `control_plane.focus_primary_refresh_target.role_codes[]`, `next_action_witness.focus_primary_verify_target.role_codes[]`, `next_action_witness.focus_primary_refresh_target.role_codes[]`, `next_action.focus_primary_verify_target.role_codes[]`, `next_action.focus_primary_refresh_target.role_codes[]`

| token | summary | metadata |
|---|---|---|
| `citation-surface-report` | This retained path is the citation-surface report. | — |
| `inventory-report` | This retained path is the compact-card inventory report. | — |
| `primary-refresh-target` | This retained path is the canonical machine target for the first focus refresh command. | — |
| `primary-verify-target` | This retained path is the canonical machine target for the first focus verify command. | — |

### `handoff_pack_primary_command_target_role_codes`

Role codes explaining what the direct handoff-pack verify/refresh command targets are for.

- field_refs: `handoff_pack.packs[].primary_verify_target.role_codes[]`, `handoff_pack.packs[].primary_refresh_target.role_codes[]`

| token | summary | metadata |
|---|---|---|
| `citation-surface-report` | This retained path is the citation-surface report. | — |
| `inventory-report` | This retained path is the compact-card inventory report. | — |
| `primary-refresh-target` | This retained path is the canonical machine target for the first pack refresh command. | — |
| `primary-verify-target` | This retained path is the canonical machine target for the first pack verify command. | — |

### `focus_primary_command_effect_codes`

Effect codes explaining whether the direct first focus command is read-only or state-changing.

- field_refs: `control_plane.focus_primary_verify_effect_code`, `control_plane.focus_primary_refresh_effect_code`, `next_action_witness.focus_primary_verify_effect_code`, `next_action_witness.focus_primary_refresh_effect_code`, `next_action.focus_primary_verify_effect_code`, `next_action.focus_primary_refresh_effect_code`

| token | summary | metadata |
|---|---|---|
| `in-place-report-rewrite` | This direct first focus command rewrites one retained report in place. | — |
| `read-only-check` | This direct first focus command verifies retained artifacts without rewriting them. | — |

### `handoff_pack_primary_command_effect_codes`

Effect codes explaining whether the direct handoff-pack first command is read-only or state-changing.

- field_refs: `handoff_pack.packs[].primary_verify_effect_code`, `handoff_pack.packs[].primary_refresh_effect_code`

| token | summary | metadata |
|---|---|---|
| `in-place-report-rewrite` | This direct handoff-pack first command rewrites one retained report in place. | — |
| `read-only-check` | This direct handoff-pack first command verifies retained artifacts without rewriting them. | — |

### `execution_blocking_reason_codes`

Stable blocking reasons for unavailable execution lanes.

- field_refs: `execution_lanes.lanes[].blocking_reason_codes`, `next_action_witness.selected_command_ladder[].required_lane_blocking_reason_codes`, `next_action.primary_action.required_lane_blocking_reason_codes`, `next_action.primary_action.command_ladder[].required_lane_blocking_reason_codes`

| token | summary | metadata |
|---|---|---|
| `junest-binary-missing` | The JuNest binary is unavailable in the current environment. | — |
| `junest-home-missing` | The JuNest home directory is unavailable in the current environment. | — |
| `junest-rust-toolchain-missing` | JuNest is present but does not currently expose a usable Rust toolchain. | — |
| `native-cargo-missing` | Native cargo is unavailable in the current environment. | — |
| `native-rustc-missing` | Native rustc is unavailable in the current environment. | — |
| `python-jsonschema-missing` | The Python jsonschema package is unavailable in the current environment. | — |
| `python3-missing` | Python 3 is unavailable in the current environment. | — |
| `rust-exec-missing` | The repo Rust wrapper script is missing from its expected path. | — |

