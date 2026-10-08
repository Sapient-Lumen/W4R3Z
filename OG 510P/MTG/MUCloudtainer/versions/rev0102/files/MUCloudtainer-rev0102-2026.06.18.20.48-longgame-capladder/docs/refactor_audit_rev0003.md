# rev0003 refactor / audit log

## Refactors

- Added `features.py` so observation encoding is no longer ad hoc inside agents or scripts.
- Added `env.py` so learning/search code can attach to one wrapper instead of directly mutating `GameState`.
- Added `agents.py` so random and heuristic pilots share a common interface.
- Updated `__init__.py` to export the new public wrapper and agent classes.

## Rule audits added as tests

- `test_main_pass_moves_to_attack_then_postcombat_then_next_turn`
- `test_cleanup_after_end_step_does_not_tick_impending_twice`
- `test_force_pitch_at_one_life_is_legal_but_loses_after_casting`
- `test_new_jace_from_legend_rule_can_be_used_even_if_old_jace_was_used`
- `test_slot_env_smoke_and_feature_vector`
- `test_heuristic_agent_game_smoke`

## Known simplifications retained

- No mulligans yet.
- No full PettingZoo/Gym API yet.
- Slot actions are fixed-width but semantically dynamic.
- Heuristic agent is a baseline, not strategy truth.
- Tiny arena data is only plumbing evidence.
