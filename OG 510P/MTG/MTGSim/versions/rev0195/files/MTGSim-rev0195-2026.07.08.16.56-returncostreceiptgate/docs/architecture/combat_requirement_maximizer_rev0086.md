# rev0086 combat requirement maximizer

rev0086 advances the rev0085 requirement solver from “all requirements must be satisfied” to “the declaration must satisfy the maximum number of requirements that can legally be satisfied under active restrictions.”

The phrase maximum satisfiable is used deliberately: this revision asks how many requirements can be met, then rejects declarations that satisfy fewer.

The concrete restriction slice is deliberately narrow and executable:

- `CardDefinition::max_attackers_each_combat = N` models a battlefield source that imposes a global “no more than N creatures can attack each combat” cap.
- `CardDefinition::max_blockers_each_combat = N` models a battlefield source that imposes a global “no more than N creatures can block each combat” cap.
- zero means no cap; multiple active caps combine by taking the lowest nonzero value.
- the cap is included in StateCore hashing and StateCoreSnapshot.v1 serialization so replay/checkpoint identity sees the legal-surface change.

## Attack declarations

Attack declarations still use the public `AttackAssignment` batch path introduced in rev0084. A candidate declaration is legal only if:

1. every chosen attacker has an individually legal defending target;
2. the final number of attacking creatures does not exceed `max_attackers_each_combat` when such a source is active;
3. the chosen attackers include as many `attacks_each_combat_if_able` creatures as can be legally included under the active cap.

Example: if two creatures must attack and a battlefield source limits the combat to one attacker, either required creature alone is legal, an optional-only attacker is illegal, and both required attackers are illegal because the restriction forbids the pair.

## Block declarations

Block declarations now reuse a shared basic-constraints helper before requirement counting. A candidate declaration is legal only if:

1. every chosen blocker can individually block its chosen attacker;
2. no blocker is assigned twice;
3. menace is satisfied for every affected menace attacker;
4. the final number of blocking creatures does not exceed `max_blockers_each_combat` when such a source is active;
5. the chosen blockers include as many `blocks_each_combat_if_able` creatures as can be legally included under those constraints.

The block-side maximizer performs a small declaration search over available blocker choices because optional blockers can be necessary to make a required blocker legal against menace. This matters when a required blocker has a legal partner in the abstract, but an active one-blocker restriction prevents the complete two-blocker menace declaration. In that case zero block requirements are satisfiable, so an explicit no-block declaration is legal.

## Validation and audit

The validator now catches committed combat metadata that exceeds active attack/block caps with:

- `combat.attack_limit_exceeded`
- `combat.block_limit_exceeded`

The datacube audit probes now look for the max-satisfaction helpers, cap fields, validation errors, and regression tests. This is an audit/refactor of the combat seam itself rather than another registry-only update.

## Still open

This is not full CR 508/509 declaration solving. Open pieces include per-creature restrictions, “must be blocked” effects, attack/block costs, player-selected damage assignment order, true rollback from a staged declaration transaction, and complete simultaneous-choice/APNAP integration. The important change is that restrictions and requirements now interact through the replayable public declaration boundary instead of being handled as independent local filters.
