# rev0158 — Paid Action Declaration / Cost Lock

## Mission fit

The heart of MTGSim is still **trusted transitions**: one authoritative state plus one explicit legal choice should produce one deterministic next state and enough typed evidence to validate, replay, branch, fuzz, search, and explain the transition.

rev0158 turns the riskiest part of the rev0157 roadmap into code: the paid spell-cast path now emits a typed `PaidActionDeclarationRecord` after stack entry and mode/target choice locking, but before mana-payment and nonmana-cost witnesses. This is a narrow vertical slice of the larger future declaration/cost-plan kernel.

## Online rules context

Online research for this slice checked Wizards' public rules page and current Comprehensive Rules TXT. The online TXT observed during the revision is effective 2026-06-19 and identifies the Comprehensive Rules as the ultimate authority for Magic gameplay. This artifact still does not redistribute official rules text; it records only rule identifiers, local implementation status, and source URLs.

Relevant source URLs consulted:

- https://magic.wizards.com/en/rules
- https://media.wizards.com/2026/downloads/MagicCompRules%2020260619.txt

## Code-bearing change

`PaidActionDeclarationRecord` records the declaration surface for the modeled paid spell-cast path:

- action kind, player, source object, stack object, source zone, and stack-entry anchors;
- locked mode and target payload summary, including target-set hash and mode-contract hash where present;
- locked total mana cost and deterministic sacrifice-cost definition;
- schema version and stable declaration identity hash;
- payment-attempt span after the record is sealed; and
- bidirectional link to the final `StackPlacementRecord`.

The final `StackPlacementRecord` now carries `paid_action_declaration_record_index` and `paid_action_declaration_hash`, so the post-payment stack receipt points back to the exact declaration/cost-lock payload it completed.

## Audit/refactor substance

Before rev0158, the cast declaration had to be inferred from nearby `choose_mode`, `choose_target`, mana-plan, sacrifice, and stack-placement rows. That was useful evidence, but it was not one typed assertion that the chosen declaration and total cost were locked before payment began.

This revision makes the pre-payment declaration challengeable directly. Validation now rejects missing declaration backlinks, wrong-kind declaration events, mismatched player/object/source-zone anchors, declaration hashes that no longer match locked cost/choice payload, payment spans that do not align with stack placement, and placement records that fail to point back to the declaration.

The focused regression is `test_paid_spell_declaration_record_locks_costs_before_payment`. It verifies that a successful paid cast creates exactly one declaration record before payment, that failed colored-mana payment rolls the speculative declaration back out of caller state, and that tampering with either the backlink or locked cost is detected.

## What remains risky

This is deliberately not the full `ChoiceDeclarationRecord` / cost-plan engine yet. The next risky seams are:

1. extend the same declaration/cost-lock record to activated abilities and loyalty abilities;
2. split the generic `PaidActionDeclarationRecord` into a reusable declaration surface plus a typed cost-plan/payment-plan record;
3. represent X, alternate costs, additional costs, cost reducers/increasers, divisions, optional choices, and spending restrictions before payment; and
4. make illegal-action rollback evidence reusable across all provisional transitions, not only the currently staged paid-action helpers.

The useful next code slice is therefore activation parity, not another report-only registry pass.
