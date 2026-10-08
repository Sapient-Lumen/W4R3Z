# rev0121 — Transition Action Journal Seal

## Mission fit

The transition mission is not merely "state changed"; it is a trusted transaction: an explicit choice produces one valid next StateCore and typed evidence explaining exactly where that transition crossed the journal boundary. rev0120 ensured a staged state is adopted only after its causal receipt matches the immediate `TransitionResult`. rev0121 tightens that evidence by exposing the post-action/pre-receipt journal seal that was previously implicit in the receipt row.

## What changed

`TransitionResult` now carries two journal-boundary fields:

- `journal_hash_after_action`
- `journal_entries_after_action`

These fields are sampled after the staged legal action mutation succeeds and before `append_action_receipt(...)` appends the causal receipt. The existing `journal_hash_after` and `journal_entries_after` fields remain the final post-receipt, post-adoption journal surface.

The resulting sequence is explicit:

1. `journal_hash_before` / `journal_entries_before`: source journal before mutation.
2. `journal_hash_after_action` / `journal_entries_after_action`: staged journal after the action body, before receipt persistence.
3. `journal_hash_after` / `journal_entries_after`: staged/adopted journal after the receipt row is appended.

## Guard behavior

`transition_receipt_matches_result(...)` now checks:

- `receipt.journal_hash_after == result.journal_hash_after_action`
- `receipt.journal_entries_after == result.journal_entries_after_action`
- `receipt.journal_entries_after + 1 == result.journal_entries_after`

The receipt still records the action-body journal sample, not a self-inclusive receipt hash. The `TransitionResult` now exposes both sides of that boundary, so immediate callers do not need to infer it by reading the latest receipt.

## Helpers

`has_post_action_journal_seal()` proves the receipt row is exactly one journal entry after the action-body journal sample.

`committed_with_action_journal_seal()` combines the atomic adoption guard with a distinct post-action versus post-receipt journal hash. `committed_with_atomic_adoption_guard()` now includes the post-action journal seal as part of its public postcondition.

## Tests and audit

`test_commit_action_transition_carries_post_action_journal_seal` verifies that a committed transition exposes the post-action journal seal, that the final result journal hash matches the adopted state, and that the causal receipt carries exactly the same post-action hash/count.

The datacube audit now probes the new fields, helpers, staged sampling point, receipt comparison, test, docs, and rules-ledger hooks so future refactors cannot collapse the journal boundary back into an implicit receipt-only detail.

## Next seam

This still wraps the existing action body. The next semantic kernel step should move the same transaction structure into a multi-step action such as paid casting: lock choices and costs, perform mana/tap/sacrifice payment, place the spell, and emit one causal receipt only after every staged phase has succeeded.
