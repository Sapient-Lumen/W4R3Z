# rev0122 — Receipt Journal Alias Seal

## Mission fit

MTGSim's trusted-transition mission needs the receipt row to be as explicit as the immediate `TransitionResult`: a chosen action must identify the action-body journal boundary before the receipt appends itself. rev0121 exposed that post-action/pre-receipt sample on `TransitionResult`; rev0122 moves the same clarity into `ActionReceiptRecord` itself so persisted receipt rows no longer depend on the ambiguous legacy field name `journal_hash_after`.

## What changed

`ActionReceiptRecord` now carries explicit post-action aliases:

- `journal_hash_after_action`
- `journal_entries_after_action`

The existing `journal_hash_after` and `journal_entries_after` fields remain as compatibility aliases for the same post-action/pre-receipt sample. `append_action_receipt(...)` writes both names from the same sampled staged journal boundary.

## Guard behavior

`ActionReceiptRecord::has_post_action_journal_seal()` proves that the receipt has a nonzero pre-action journal hash, a nonzero post-action journal hash, matching explicit and legacy post-action aliases, and a nondecreasing post-action journal entry count.

`transition_receipt_matches_result(...)` now compares both receipt names against `TransitionResult::journal_hash_after_action` and `TransitionResult::journal_entries_after_action` before staged adoption. The validator also rejects alias drift through `action_receipt.post_action_journal_hash_alias_mismatch`, `action_receipt.post_action_journal_count_alias_mismatch`, and `action_receipt.post_action_journal_seal_missing`.

## Audit/refactor value

This is intentionally a small refactor/audit slice. It removes a naming ambiguity without changing `ActionTrace.v16`: receipts keep their historical fields, while strict transition callers and validators can use the explicit after-action names. The final post-receipt journal hash remains a `TransitionResult` surface, not a self-inclusive receipt field.

## Tests and audit

`test_action_receipt_post_action_journal_alias_is_validated` verifies that legacy `apply_action(...)` receipts carry the explicit aliases and that validator catches hash/count alias drift. The existing transition journal tests now require the causal receipt's explicit aliases to match the `TransitionResult` post-action seal.

The datacube audit now probes the receipt alias fields, helper, validator codes, C++ test, docs, and rules-ledger hooks so future refactors cannot collapse the explicit after-action receipt seal back into an implicit legacy name.

## Next seam

The semantic priority remains paid-cast or activated-ability staging: mode/target/cost locks, payment, stack placement, and exactly one causal receipt after every staged phase succeeds.
