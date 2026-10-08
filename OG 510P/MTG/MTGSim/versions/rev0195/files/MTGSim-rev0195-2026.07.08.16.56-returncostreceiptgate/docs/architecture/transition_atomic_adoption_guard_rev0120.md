# rev0120 — Transition Atomic Adoption Guard

## Mission fit

The mission remains trusted transitions: a state plus an explicit legal choice must produce one rules-valid next state with typed evidence. rev0119 moved `commit_action_transition(...)` onto a staged `GameState` so failed mutation work could not leak into the caller state. rev0120 tightens the adoption seam: the staged state is not adopted merely because mutation returned true. It must first carry a causal receipt that matches the `TransitionResult` evidence surface.

## What changed

`TransitionResult` now exposes three adoption-guard sentinels:

- `staged_receipt_checked` — the staged state reached receipt inspection.
- `staged_receipt_consistent` — the latest staged `ActionReceiptRecord` matched the transition result's action hash, schema versions, pre/post StateCore hashes, pre-action journal sampling, selected page proof, and APNAP queue proof.
- `staged_adoption_guard_passed` — the receipt check and selected-choice proofs passed, so the staged state may be adopted.

The helper `committed_with_atomic_adoption_guard()` now combines single-receipt commit, staged adoption, and the receipt guard.

## Implementation note

`transition_receipt_matches_result(...)` deliberately distinguishes two journal surfaces:

1. the receipt's `journal_hash_after` / `journal_entries_after`, sampled after the rule work but before the receipt appends itself; and
2. the `TransitionResult` `journal_hash_after` / `journal_entries_after`, sampled after the receipt has been appended to the staged journal.

That means the adoption guard compares the receipt's before-fields and selected proof hashes directly, checks the receipt index/count relationship, and expects the receipt's post-action journal entry count plus the receipt row itself to equal the transition result's post-commit journal entry count.

## Failure behavior

If mutation succeeds but the staged receipt guard fails, `commit_action_transition(...)` returns `Rejected` with reason `staged_receipt_guard_failed`, clears the causal receipt index, and does not adopt the staged state. The caller-visible StateCore and journal remain the original source state.

## Tests and audit

`test_commit_action_transition_checks_staged_receipt_before_adoption` checks the happy-path guard contract. Existing transition tests now assert that preflight rejection does not check or pass staged receipt sentinels, and committed transitions satisfy `committed_with_atomic_adoption_guard()`.

`audit_transition_result_wiring(...)` now probes the guard fields, helper, implementation function, failure reason, test, docs, and ledger hooks so a future refactor cannot silently bypass the adoption check.
