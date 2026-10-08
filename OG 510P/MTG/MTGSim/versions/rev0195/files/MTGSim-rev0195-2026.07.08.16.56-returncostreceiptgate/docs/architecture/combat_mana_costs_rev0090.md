# rev0090 combat mana-cost declaration seam

rev0090 adds a deliberately narrow combat-cost transaction: mana-only required costs to attack or block.

## Implemented

- `CardDefinition::attack_cost`
- `CardDefinition::block_cost`
- StateCore hash and snapshot serialization for both fields
- batch-level `attack_declaration_cost(...)`
- batch-level `block_declaration_cost(...)`
- public `LegalAction` filtering when the locked mana-only declaration cost is not payable
- mana-ability autopayment during the turn-based declaration action
- priority snapshot restoration after payment
- `pay_attack_cost` and `pay_block_cost` event evidence
- trace replay tests for paid attack and paid block declarations

## Important semantic guard

Combat declaration costs are not requirement-forcing fuel. A creature that must attack or block if able does not force its controller to pay a cost merely to satisfy that requirement. The same principle applies to attacker-side blocking requirements: a cost-bearing blocker may block if its controller chooses and can pay, but it does not make no-block illegal by itself.

The requirement maximizers therefore use cost-free candidates when computing compulsory maximum satisfaction. Actual declarations still include cost-bearing attackers/blockers when the player chooses them and the locked mana cost is payable.

## Not implemented yet

- optional attack costs
- non-mana costs such as tap, sacrifice, or discard
- cost-modification effects
- multiple cost-choice prompts
- full staged rollback for every declaration failure mode
- blocker damage-order choices
- banding

This revision is a transaction seam, not a complete CR 508/509 implementation.


Semantic guard: combat declaration cost payment is not forced by requirement maximization; costs gate chosen declarations but do not create compulsory payments.
