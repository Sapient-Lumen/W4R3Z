# rev0134 — Paid Action Transaction Spine

## Mission fit

MTGSim's center is trusted transition semantics: an authoritative `StateCore` plus one rules-valid choice must produce one deterministic next `StateCore` and typed evidence. rev0117–rev0132 hardened the outer `TransitionResult` proof shell. rev0134 moves that discipline inward to the highest-risk semantic body named by rev0133: paid casting and activated-ability payment.

## Audit finding

The earlier paid action helpers did strong preflight checks, but the mutating bodies still contained several provisional phases: move a spell to the stack, create a synthetic activated-ability stack object, stamp mode/target choices, auto-activate mana abilities, spend mana, pay tap/sacrifice costs, pass priority, and record stack placement. A failure inside that sequence should not leave any residue in the caller's `GameState`.

A specific activation seam made the problem concrete: an object with both a tap-cost activated ability and a tap-for-mana ability could be considered a mana-payment candidate for its own activation cost before the tap cost was paid. The same source should not be both the activation tap-cost object and the tap-mana source for that activation. That illegal double-tap path also created a useful rollback regression target.

## Refactor

rev0134 adds `commit_paid_action_body_transaction(...)`, a local transaction helper for paid action bodies. The helper clones the caller state into a staged `GameState`, runs the mutator against the staged copy, and adopts the staged copy only when every phase succeeds. Any staged false result or exception leaves the original state untouched.

The following bodies now run inside that staged transaction:

- `cast_from_hand_to_stack_paying_mana(...)`
- `cast_from_hand_to_stack_paying_mana_with_targets(...)`
- `cast_from_hand_to_stack_paying_mana_with_mode_and_targets(...)`
- `activate_activated_ability_with_targets(...)`

The mana planner was also split around an explicit lock set:

- `activation_locked_tap_sources(...)` returns the source object for activated abilities with tap costs.
- `select_mana_ability_pay_plan_excluding_tap_sources(...)` preserves the existing bounded deterministic search while skipping tap-mana candidates whose object is locked for another cost component.
- `pay_mana_cost_with_mana_abilities_excluding_tap_sources(...)` executes the locked-source plan for activated abilities.

This is still a narrow semantic transaction, not a full Magic casting engine. It stages the current modeled phases and prevents the current activation tap-cost double-tap leak. It does not yet implement alternate costs, additional-cost choices, cost reducers/increasers, spending restrictions, replacement effects around payment, explicit mana-choice UI, or effects modifying produced mana.

## Acceptance tests

`test_activated_ability_tap_cost_locks_source_before_auto_mana_payment` proves both sides of the seam:

1. With only the source object available, activation is not payable; direct activation returns false; no synthetic stack object, stack placement, tapped source, produced mana, or stack entry leaks into the caller state.
2. With an external mana source available, the external source pays the mana cost, the ability source pays only the activation tap-cost, the pool is emptied, and exactly one synthetic ability object reaches the stack.

The new datacube audit probe `audit_paid_action_transaction_wiring(...)` keeps the refactor wired through engine code, regression tests, documentation, audit notes, and the rules ledger.

## Next seam

The next useful slice should generalize this from a local helper to named paid-action phases that can be independently inspected by transition evidence: choice lock, cost lock, mana plan, mana production, payment, nonmana costs, stack placement, and one causal receipt. A failed paid cast should eventually prove that card zones, tapped permanents, mana pool, journal entries, stack placement records, and action receipts all remain exactly unchanged.
