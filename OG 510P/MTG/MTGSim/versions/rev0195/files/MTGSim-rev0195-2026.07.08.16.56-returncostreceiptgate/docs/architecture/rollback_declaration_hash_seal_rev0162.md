# rev0162 rollback declaration hash seal

## Mission seam

rev0161 made failed paid spell, activated ability, and loyalty ability attempts leave one terminal rollback receipt, but the receipt still only counted the discarded `PaidActionDeclarationRecord`. That was not enough for a verifier or future agent to challenge exactly what had been declared before the branch was reversed.

rev0162 changes the rollback receipt from count-only evidence into a hash-sealed witness. The committed caller state still does not retain speculative stack objects or speculative declaration records, but `PaidActionTransactionRecord` now carries:

- `speculative_paid_action_declaration_sequence`
- `speculative_paid_action_declaration_hash`
- `speculative_first_payment_event_sequence`
- `speculative_last_payment_event_sequence`

The hash is computed from a local copy of the discarded declaration/cost-lock payload after the failed payment span is known. This keeps rollback compact while preserving a challengeable fingerprint of the exact prepayment declaration that was reversed.

## Rules spine checked online

Online research during this pass rechecked Wizards' public rules page and the current TXT rules download observed there, effective 2026-06-19:

- <https://magic.wizards.com/en/rules>
- <https://media.wizards.com/2026/downloads/MagicCompRules%2020260619.txt>

The relevant rules remain the same narrow seam: rule 601.2f locks total cost, 601.2g gives the player a chance to activate mana abilities before payment, 601.2h pays the total cost and disallows partial/unpayable costs, 602.2 and 602.2b reuse the spell-casting process for activated abilities, and 733.1 reverses an illegal/incomplete action and cancels payments.

## Code-bearing changes

- Bumped `kPaidActionTransactionRecordSchemaVersion` to 2.
- Extended `PaidActionTransactionRecord` with rollback-only speculative declaration hash/span fields.
- Changed rollback recording to inspect the staged branch, copy the discarded declaration, add the failed payment span, hash that payload, and seal it on the caller-visible transaction receipt.
- Added an explicit `loyalty_cost_payment_failed` event before insufficient-loyalty rollback so the failed payment span is visible instead of relying on branch length alone.
- Hardened validation with `paid_action_transaction_record.rollback_missing_speculative_declaration_hash`, `rollback_declaration_sequence_outside_branch`, and rollback payment-span diagnostics.
- Strengthened paid-cast, activated-ability, and loyalty-ability rollback regressions to require the declaration hash and payment span, and to reject count-only rollback receipts.

## Audit/refactor note

This is deliberately not a new registry layer. It is a small executable audit refactor inside the transaction seam: rollback receipts now carry enough identity data to be meaningful without storing speculative state. The remaining high-risk gap is that cost calculation itself is still mostly fixture-level; alternative/additional cost choice and cost modification are not yet represented as a first-class total-cost derivation record.
