# Reconnect-vs-merge receipt page — proof class, divergence verdict, and preservation decision interface spec

## Purpose

This receipt exists so later operators do not have to reconstruct meaning from a connected row, a same-name folder, or memory of a warning dialog.

It answers:

> was this event a proven same-lineage reconnect, a guarded merge into a non-empty target, a preserve-first adopt, or a blocked attempt?

## Core decision

Every reviewed non-empty-target connect/adopt flow must emit one first-class **Reconnect-vs-merge receipt**.

This receipt is separate from generic bind receipts because it preserves the exact claim ceiling for the overloaded `reconnect` / `add anyway` seam.

## Receipt fields

### Required top-level fields

- `reconnect_vs_merge_receipt_id`
- `subject_ref`
- `seat_ref`
- `target_path`
- `remembered_path`
- `proof_class`
- `divergence_verdict`
- `preservation_decision`
- `commit_outcome`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `completed_at`
- `acted_by`

### Allowed `proof_class` values

- `proven_same_lineage_reconnect`
- `guarded_same_lineage_candidate`
- `non_empty_merge_reviewed`
- `blocked_conflicting_target`
- `abandoned_before_commit`

### Allowed `divergence_verdict` values

- `no_same_path_divergence_found`
- `merge_non_overlapping_only`
- `guarded_same_path_divergence`
- `conflicting_material_blocked`
- `comparison_not_completed`

### Allowed `preservation_decision` values

- `not_needed`
- `copy_aside_before_commit`
- `quarantine_before_commit`
- `side_branch_instead_of_merge`
- `declined_after_review`
- `not_reached`

## Fixed receipt order

1. **Outcome strip**
2. **Proof used**
3. **Divergence result**
4. **Preservation decision**
5. **Safe language**
6. **Next handoff**

### 1) Outcome strip

Show:

- proof class
- target path
- commit outcome (`connected`, `connected-guarded`, `blocked`, `stopped`)
- strongest warning that remained true afterward

### 2) Proof used

Show the strongest evidence rows behind the reconnect claim:

- remembered path
- lineage marker or hidden-state match
- prior receipt
- conflicting evidence if any

### 3) Divergence result

Show:

- class counts or summary
- strongest divergence verdict
- chronology/authority confidence when relevant

### 4) Preservation decision

Show:

- whether preservation was offered
- which option was chosen
- whether later cleanup/recovery work was created

### 5) Safe language

Always show both:

- strongest safe sentence
- stronger rejected sentence

Example:

- `This share was connected to a non-empty target after reviewed comparison and preserve-first copy-aside.`
- `This receipt does not prove the old directory was fully restored without merge.`

### 6) Next handoff

Show:

- later merge receipt if any
- later side-branch review if any
- later cleanup obligation if any

## Result

A good reconnect-vs-merge receipt prevents five failures:

- `connected` becoming the only remembered fact
- proven reconnect and guarded merge being indistinguishable later
- preservation decisions disappearing from audit history
- same-lineage proof being overstated after the fact
- support and future operators having to infer meaning from filesystem fallout
