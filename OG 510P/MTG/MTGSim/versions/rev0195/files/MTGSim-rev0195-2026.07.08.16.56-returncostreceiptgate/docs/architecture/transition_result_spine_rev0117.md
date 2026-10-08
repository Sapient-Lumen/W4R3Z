# rev0117 Transition Result Spine

Accessed and revised 2026-07-06 America/New_York.

## Why this slice exists

rev0116 named the mission as trusted transitions:

```text
authoritative state + explicit choice -> rules-valid deterministic next state + typed evidence
```

rev0117 turns that mission note into the first code-bearing seam. It does not replace the existing `LegalAction` surface, but it adds a public result shape around it so callers can stop treating every attempted action as a boolean with side effects.

## Added public seam

`TransitionStatus` now has three explicit outcomes:

- `NeedChoice`: a player/system choice is available but not selected yet;
- `Rejected`: a proposed action was rejected before semantic mutation;
- `Committed`: a proposed action committed and should name exactly one causal receipt.

`TransitionResult` carries the typed evidence needed to audit that outcome: the local `ChoiceRequest`, APNAP `ChoiceRequestQueue`, queue index, validation source, page-location proof, action hash/schema, StateCore hash before/after, journal hash/count before/after, action receipt count before/after, event sequence allocator before/after, and a causal receipt index when committed.

The first two public entry points are intentionally narrow:

```cpp
TransitionResult pending_transition_for_player(const GameState& game, PlayerId player_id);
TransitionResult commit_action_transition(GameState& game, const LegalAction& action);
```

`pending_transition_for_player(...)` is a pure inspection path. It exposes `NeedChoice` plus the same typed choice surface replay already binds, without appending events or receipts.

`commit_action_transition(...)` is a stricter commit path than legacy `apply_action(...)` for rejected actions. An illegal proposal returns `Rejected` with unchanged StateCore hash, unchanged journal hash/count, unchanged action receipt count, and unchanged event sequence allocator. A legal proposal commits through the existing action machinery and identifies the single `ActionReceiptRecord` caused by the transition.

## Refactor performed

The large `apply_action(...)` mutation switch is now factored into an internal `apply_legal_action_mutation(...)` helper. Both `apply_action(...)` and `commit_action_transition(...)` use the same action-family mutation body. This keeps the new result wrapper from becoming a second, drifting implementation of pass priority, paid casting, land play, mana abilities, activated abilities, loyalty abilities, combat declarations, damage ordering, and trigger placement.

## Compatibility boundary

Legacy `apply_action(...)` intentionally keeps its current audit behavior: illegal attempts still append an `illegal_action` event and an unapplied receipt so full traces can preserve rejected attempts. The new nonmutating rejection guarantee is provided by `commit_action_transition(...)`. This lets existing replay diagnostics remain stable while new callers can opt into the stricter reducer contract.

## Acceptance tests added

- `test_transition_result_exposes_need_choice_surface`
- `test_commit_action_transition_rejects_without_journal_mutation`
- `test_commit_action_transition_commits_with_single_causal_receipt`

Together they prove:

```text
NeedChoice inspection is pure
Rejected transition has no StateCore mutation and no journal/receipt mutation
Committed transition appends exactly one causal ActionReceiptRecord
```

## What is still missing

This is the spine, not the full staged transaction kernel. The next vertical slice should make one multi-step rule procedure transactional: paid casting or activated abilities. That slice should stage targets, modes, costs, mana-ability activation, source/tap/sacrifice costs, stack placement, and rollback before committing one receipt.

The larger open work remains:

- explicit reason codes instead of string reasons;
- a transaction object that owns proposed writes until commit;
- small-state legal-choice equivalence properties across direct validation, cursor pages, page locations, and replay receipts;
- eventual StateCore/Catalog/Journal physical separation.
