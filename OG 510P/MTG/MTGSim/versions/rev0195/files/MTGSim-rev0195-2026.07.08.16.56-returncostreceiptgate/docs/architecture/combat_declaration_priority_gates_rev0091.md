# rev0091 combat declaration priority gates

rev0091 fixes a high-risk action-surface bug: ordinary priority choices were still visible while combat declaration windows were open. That let an active player receive `PassPriority` before attackers were explicitly declared, and it let the active player appear ahead of a defending player's blocker declaration in the choice queue.

The engine now treats attacker and blocker declarations as mandatory turn-based choice gates. The gate still exposes explicit empty declarations (`DeclareAttacker:none` / `DeclareBlocker:none`) when they are legal, but it does not expose ordinary priority actions until the relevant declaration window has completed.

## Executable behavior

- During `DeclareAttackers`, before `attackers_declared_this_step` is true, only the active player receives attacker declaration actions.
- Other players receive no priority scaffold actions while that attacker declaration gate is open.
- During `DeclareBlockers`, while any defending player with attackers to block has not completed a blocker declaration, only those defending players receive blocker declaration actions.
- The active player's `PassPriority` action is not legal while a defender's block/no-block declaration is still pending.
- `ChoiceRequest::required` is now true for `DeclareAttackers` and `DeclareBlockers`, matching the existing pending-trigger gate behavior.
- After a legal declaration, including an empty declaration, priority resumes through the ordinary choice surface; priority actions resume only after the explicit declaration gate is closed.

## Refactor note

The declaration enumeration code is now centralized in `append_attack_declaration_actions(...)` and `append_block_declaration_actions(...)`, and the gate checks live in `attack_declaration_choice_pending(...)`, `blocker_declaration_choice_pending_for_player(...)`, and `any_blocker_declaration_choice_pending(...)`. This keeps the public action surface from reintroducing priority-before-declaration drift while preserving the batch declaration encodings added in rev0083-rev0090.

## Still open

This is not a complete CR 508/509 implementation. Damage assignment order choices, arbitrary declaration costs, richer defender-specific restrictions, banding/multi-attacker blockers, and fully staged rollback remain future work. The important improvement is that the engine can no longer skip the current explicit declaration transaction by presenting ordinary priority too early.
