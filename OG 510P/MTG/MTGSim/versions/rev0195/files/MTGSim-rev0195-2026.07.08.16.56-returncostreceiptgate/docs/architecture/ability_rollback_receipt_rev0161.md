# MTGSim rev0161 — Ability Rollback Receipt

## Mission-critical seam

rev0161 addresses the riskiest gap left by rev0160: failed direct ability activations were mostly dying at preflight, so the cube could prove that illegal actions stayed out of legal-action enumeration but could not yet prove the rule-733 rollback shape for a direct attempt that was structurally begin-able and failed only at payment.

The change is intentionally narrow and executable. `can_activate_*` still answers the legal-action frontier question and remains payability-filtered. The direct `activate_*` paths now use a separate begin-before-payment gate: structural timing, controller, target, and source checks happen before staging; mana/loyalty payment failures happen inside `commit_paid_action_body_transaction(...)`.

That means an unpayable direct activated or loyalty ability attempt now leaves exactly one durable external receipt: a `PaidActionTransactionRecord` with `RolledBack`, no committed `StackPlacementRecord`, no committed `PaidActionDeclarationRecord`, equal pre/post physical StateCore hashes, and speculative-count evidence proving that the discarded branch reached declaration/cost-lock.

## Online rules check

Online research for this pass rechecked Wizards' public rules page and current TXT download. The observed current Comprehensive Rules TXT is effective 2026-06-19: <https://media.wizards.com/2026/downloads/MagicCompRules%2020260619.txt>. The local bundled ledger remains metadata-only and pinned to the packaged 2026-04-17 source until a deliberate rules-refresh/diff revision.

The rule spine used for this code change is:

- 602.2a-b: activated abilities are created on the stack and then follow the spell-casting payment process.
- 601.2h: the player pays total costs after lock-in, and unpayable costs cannot be paid.
- 733.1: an illegal or incomplete action is reversed, payments are canceled, and the player keeps priority.

## Code/refactor shape

- `src/engine.cpp` now has begin-before-payment gates for activated and loyalty ability paths.
- `can_activate_activated_ability_with_targets(...)` and `can_activate_loyalty_ability_with_targets(...)` remain full legal-frontier filters that include payability.
- `activate_activated_ability_with_targets(...)` and `activate_loyalty_ability_with_targets(...)` stage structurally valid direct attempts before payment, allowing rollback receipts to be emitted on payment failure.
- `src/validation.cpp` now rejects paid rollback transaction rows that claim a paid action but expose no speculative declaration/cost-lock evidence.

## Executable proof

New focused regressions:

- `test_failed_activated_ability_payment_rolls_back_transaction_receipt`
- `test_failed_loyalty_ability_payment_rolls_back_transaction_receipt`

Release smoke: `337/337` C++ all-in-one release cases passed in `reports/harness/cpp_allinone_release_rev0161_smoke.json`.

## What remains risky

The next high-risk seam is not another prose registry. It is expanding the same direct-attempt rollback receipt model to richer declaration payloads: mode/X decisions, optional costs, alternative costs, and multi-stage nonmana cost plans. The target shape should stay vertical: one risky action family, one staged rollback path, one validator hardening, and one focused executable proof.
