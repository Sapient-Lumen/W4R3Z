# rev0084 — Combat declaration finality action surface

rev0084 takes a second concrete step toward atomic combat. rev0083 proved that a legal menace blocker batch can cross the public action, receipt, and replay boundary. rev0084 broadens that bridge to attacker declarations and to explicit empty declarations.

## Why this matters

A legal Magic combat declaration is a turn-based declaration, not an unbounded series of priority-like micro-actions. The previous surface had two risky behaviors:

1. Attackers were exposed as one attacker at a time, so multi-attacker declarations could not be represented as one selected action.
2. “No attackers” and “no blockers” were represented as absence, which is ambiguous for agents, traces, fuzzing, and replay diagnostics.

rev0084 makes these choices explicit. The selected action can now say “these attackers,” “no attackers,” “these blockers,” or “no blockers,” and the action receipt/trace records that exact selection.

## Implementation slice

- `AttackAssignment` represents an attacker plus defending player/object target.
- `make_declare_attackers_action(...)` and `attack_assignments_from_action(...)` use the same replay-friendly pair-vector pattern introduced for blocker batches.
- `declare_attackers(...)` validates the whole candidate vector before mutation and sets `attackers_declared_this_step` after commit, including the empty declaration.
- `declare_blockers(...)` records the defending player in `blocker_declaration_complete_players` after either a nonempty or empty declaration.
- StateCore snapshots, canonical StateCore hashes, and branch copies now include declaration-completion state.
- `block_assignment_basic_legal(...)` factors shared blocker prechecks so single and batch paths cannot silently diverge before final batch-level checks such as menace.

## Validation intent

The new tests assert end-to-end behavior rather than symbol presence:

- multi-attacker batch: enumerate -> apply -> `ActionReceiptRecord` -> `ActionTrace.v1` -> replay from checkpoint;
- explicit no-block declaration: enumerate -> apply -> `ActionReceiptRecord` -> `ActionTrace.v1` -> replay from checkpoint;
- defender-only attack surfaces still omit nonempty attack choices but expose explicit no-attack;
- illegal flying blocks still omit nonempty block choices but expose explicit no-block.

## Still not done

This is not a complete CR 508/509 solver. The engine still needs one transaction that starts with a pre-declaration checkpoint, proposes the entire declaration, solves restrictions/requirements/costs, rejects illegal declarations without mutation, and only then commits and advances to priority. rev0084 only makes the current public action surface honest enough for that solver to replace internals incrementally.
