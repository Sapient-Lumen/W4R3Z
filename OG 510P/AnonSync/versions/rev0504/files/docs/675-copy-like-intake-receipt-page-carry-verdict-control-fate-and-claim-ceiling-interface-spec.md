# Copy-like intake receipt page — carry verdict, control fate, and claim ceiling interface spec

## Purpose

This receipt is the durable proof for copy-looking intake decisions.
It exists so later operators do not have to rediscover the meaning from hidden files, support lore, or damage symptoms.

## Receipt must prove

- what tree/path was reviewed
- the carry verdict at decision time
- the winning identity/world basis
- whether the action preserved continuity, created a successor, created a clean branch, quarantined the tree, or blocked the action
- the fate of hidden controller state
- the strongest rejected sentence

## Required fields

- `copy_like_intake_receipt_id`
- `tree_ref`
- `carry_verdict`
- `identity_basis`
- `winning_lane`
- `continuity_result`
- `control_state_fate_summary`
- `exported_witness_refs[]`
- `rejected_stronger_sentence`
- `created_at`

## Example summary lines

- `Reviewed as same managed subject; local spine matched active world; continuity preserved.`
- `Reviewed as copied payload branch; hidden controller state detached after witness export; no same-subject claim remains.`
- `Blocked as foreign managed carry; contradictory spine ownership remained unresolved.`

## Design test

If a later operator still has to inspect hidden `.sync` state or old support notes to learn whether this tree was treated as a same subject or a clean copy, the receipt failed.
