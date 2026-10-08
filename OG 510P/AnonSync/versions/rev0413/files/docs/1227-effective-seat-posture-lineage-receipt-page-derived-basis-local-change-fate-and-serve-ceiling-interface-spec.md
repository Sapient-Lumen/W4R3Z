# Effective-seat-posture lineage receipt page — derived basis, local-change fate, and serve ceiling

## Purpose

After any serious permission dispute, narrow-seat local edit, linked-device breakout, local-share downshift, or encrypted-node overclaim, a later operator must be able to answer:

> what posture did this seat really have here at the time — direct writer, narrow observer, owner, linked-family default owner, inherited local derivative, or encrypted hard-wired observer — and what stronger sentence was explicitly rejected?

This receipt exists so seat truth does not dissolve into `read only`, `owner`, `shareable`, or `can help peers` folklore.

## Receipt fields

### Identity

- `receipt_id`
- `seat_ref`
- `subject_ref`
- `created_at`

### Posture truth

- `grant_label_class` (`read_only`, `read_write`, `owner`, `encrypted_hardwire`, `derived_local_share`, `unresolved`)
- `effective_posture_class` (`direct_writer`, `narrow_observer`, `delegating_owner`, `linked_owner_default`, `inherited_local_share`, `encrypted_hardwired_observer`, `unresolved`)
- `derivation_class` (`direct_grant`, `linked_family_default`, `local_share_inheritance`, `encrypted_family_hardwire`, `unresolved`)

### Capability truth

- `mutation_authority_class` (`publish_full_mutations`, `local_mutation_no_publish`, `suspends_on_known_file`, `auto_heal_from_source`, `mixed_by_action`, `unresolved`)
- `serve_right_class` (`serve_approved_bytes`, `serve_parent_source_only`, `no_beyond_local_service`, `unresolved`)
- `delegation_authority_class` (`share_and_revoke`, `share_narrow_family_only`, `cannot_share`, `unresolved`)

### Local divergence truth

- `rename_fate_class`
- `delete_fate_class`
- `content_edit_fate_class`
- `local_add_fate_class`
- `overwrite_heal_status` (`enabled`, `disabled`, `unavailable`, `hardwired`, `unresolved`)
- `selective_sync_ceiling` (`none`, `blocks_overwrite_heal`, `not_supported_here`, `unresolved`)

### Handling truth

- `source_authority_needed` boolean
- `repair_rung_if_contested`
- `next_proof_action` nullable

### Claim ceiling

- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `reopen_conditions[]`

## Required behavior

The receipt must be emitted whenever:

- a supposedly read-only seat mutates locally and the result is surprising;
- a peer serves bytes despite narrow mutation rights and an operator questions why;
- a linked-family seat is broken out into a narrower posture;
- a local share inherits or downshifts its rights from a source seat;
- an encrypted node is being treated like ordinary restore or republish authority.

## Forbidden simplifications

The receipt must never flatten the event into:

- `read only`
- `owner`
- `cannot sync back`
- `will overwrite changes`
- `can share`
- `backup peer`

unless the structured posture, derivation, capability, local-fate, and blocked-sentence fields remain inspectable alongside that summary.
