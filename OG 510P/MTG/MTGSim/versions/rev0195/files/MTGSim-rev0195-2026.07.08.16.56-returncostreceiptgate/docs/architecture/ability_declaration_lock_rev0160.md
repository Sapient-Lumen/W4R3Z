# MTGSim rev0160 — Ability Declaration Lock

## Risk addressed

rev0159 made modeled paid stack actions terminate with `PaidActionTransactionRecord`, but only paid spell casts had a first-class declaration/cost-lock receipt. Activated and loyalty ability transactions therefore sealed a weaker chain: the terminal receipt could point to stack-placement and phase evidence, but not to one typed pre-payment declaration payload.

rev0160 closes that asymmetry for stack-using abilities. The semantic heart is still trusted transitions: before payment mutates mana pools, taps permanents, sacrifices objects, or changes loyalty counters, the engine should have a typed claim for *what was declared* and *what total cost shape was locked*.

## Online rules check

The official Wizards Comprehensive Rules PDF observed online for this revision is effective 2026-06-19. It states that activating an ability puts it onto the stack and pays costs in order, that the ability is created on the stack as a non-card object, that the remainder of activation follows the casting process, and that illegal activations return to the moment before activation under rule 733. The datacube continues to avoid bundling official rules text; this note records only identifiers and implementation consequences.

Relevant source anchors checked online: rules 118.2, 601.2f-h, 602.2, 602.2a, 602.2b, 606.4, and 733.

## Code-bearing change

- Generalized `PaidActionDeclarationRecord` from paid spell casts to three paid stack-action kinds: `CastSpellFromHandPaid`, `ActivateActivatedAbility`, and `ActivateLoyaltyAbility`.
- Added declaration payload for ability-specific cost shape: `ability_index`, `loyalty_cost_delta`, `tap_cost_required`, and `loyalty_cost_required`.
- Recorded activated-ability declarations after synthetic stack-object creation and target locking, before mana, tap, and sacrifice payment witnesses.
- Recorded loyalty-ability declarations after synthetic stack-object creation and target locking, before loyalty-counter payment witnesses.
- Extended stable declaration hashing so ability index, loyalty delta, tap-cost requirement, and loyalty-cost requirement are sealed into the declaration identity.
- Extended committed `PaidActionTransactionRecord` validation so all committed paid stack actions must link to a declaration receipt, not just paid spell casts.

## Audit/refactor performed

The validator’s paid-declaration path is no longer a spell-only special case. It now validates spell, activated-ability, and loyalty-ability declarations through a shared spine and branch-specific shape checks:

- spell declarations must keep source and stack object identical, start from hand, and link the stack-enter zone-change row;
- activated and loyalty declarations must separate battlefield source from synthetic stack object and must not claim a physical card stack-enter zone-change row;
- activated declarations may lock mana, tap, and sacrifice cost flags but not loyalty cost state;
- loyalty declarations must lock loyalty cost state and must not claim mana, tap, or sacrifice cost flags;
- stack-placement and transaction receipts must carry the same declaration hash and identity.

The focused executable regression is `test_activated_ability_declaration_record_locks_costs_before_payment`. It proves the activation declaration locks the synthetic stack object, target vector, ability index, mana cost, tap cost, payment span, stack-placement backlink, terminal transaction backlink, hash tamper detection, and cost-flag/placement mismatch rejection. Existing loyalty paid-phase coverage now also asserts loyalty declaration linkage.

## Remaining risk

The next risky seam is failed ability activations that are rejected by preflight rather than staged far enough to emit rollback transaction receipts. rev0160 deliberately did not broaden that surface yet. The next code-bearing pass should distinguish invalid-to-attempt cases from legal-to-attempt-but-unpayable cases, then route the latter through the same rollback receipt model introduced for failed paid casts.
