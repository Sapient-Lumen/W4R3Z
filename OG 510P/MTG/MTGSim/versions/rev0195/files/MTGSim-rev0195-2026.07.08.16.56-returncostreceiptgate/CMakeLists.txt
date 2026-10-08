cmake_minimum_required(VERSION 3.20)
project(MTGSim VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(mtgsim
    src/engine.cpp
    src/rng.cpp
    src/types.cpp
    src/validation.cpp
    src/rules.cpp
)

target_include_directories(mtgsim PUBLIC include)

target_compile_options(mtgsim PRIVATE
    $<$<CXX_COMPILER_ID:GNU>:-Wall -Wextra -Wpedantic -Wconversion -Wshadow>
    $<$<CXX_COMPILER_ID:Clang>:-Wall -Wextra -Wpedantic -Wconversion -Wshadow>
)

# The engine and validation translation units are compile-time hotspots in
# small linked-revision containers. Keep default Release clean builds practical
# and reproducible; use tools/build.py --release-core-hotspot-opt-level 3 or a
# local CMake override for performance-oriented full-O3 builds.
set_source_files_properties(src/engine.cpp PROPERTIES COMPILE_OPTIONS
    "$<$<AND:$<CONFIG:Release>,$<CXX_COMPILER_ID:GNU>>:-O0>;$<$<AND:$<CONFIG:Release>,$<CXX_COMPILER_ID:Clang>>:-O0>"
)
set_source_files_properties(src/validation.cpp PROPERTIES COMPILE_OPTIONS
    "$<$<AND:$<CONFIG:Release>,$<CXX_COMPILER_ID:GNU>>:-O0>;$<$<AND:$<CONFIG:Release>,$<CXX_COMPILER_ID:Clang>>:-O0>"
)

add_executable(mtgsim_cli apps/mtgsim_cli.cpp)
target_link_libraries(mtgsim_cli PRIVATE mtgsim)

add_executable(mtgsim_tests tests/cpp/test_engine.cpp)
target_link_libraries(mtgsim_tests PRIVATE mtgsim)

add_executable(mtgsim_scenario apps/mtgsim_scenario.cpp)
target_link_libraries(mtgsim_scenario PRIVATE mtgsim)

add_executable(mtgsim_fuzz apps/mtgsim_fuzz.cpp)
target_link_libraries(mtgsim_fuzz PRIVATE mtgsim)

add_executable(bench_turns benchmarks/bench_turns.cpp)
target_link_libraries(bench_turns PRIVATE mtgsim)

add_executable(bench_branch_clearall benchmarks/bench_branch_clearall.cpp)
target_link_libraries(bench_branch_clearall PRIVATE mtgsim)

add_executable(bench_legal_action_frontier benchmarks/bench_legal_action_frontier.cpp)
target_link_libraries(bench_legal_action_frontier PRIVATE mtgsim)

# The executable driver translation units are intentionally glue-heavy. Keep
# release builds from spending cloud/container budget optimizing harness glue
# instead of validating the reusable engine library.
set(MTGSIM_RELEASE_DRIVER_TARGETS mtgsim_tests mtgsim_scenario mtgsim_fuzz mtgsim_cli bench_turns bench_branch_clearall bench_legal_action_frontier)
foreach(driver_target IN LISTS MTGSIM_RELEASE_DRIVER_TARGETS)
    target_compile_options(${driver_target} PRIVATE
        $<$<AND:$<CONFIG:Release>,$<CXX_COMPILER_ID:GNU>>:-O0>
        $<$<AND:$<CONFIG:Release>,$<CXX_COMPILER_ID:Clang>>:-O0>
    )
endforeach()

# The monolithic C++ regression translation unit is a linked-revision
# validation target, not a performance artifact. Keep it at -O0 in Release so
# substantive seam tests compile inside the cloudtainer budget instead of
# starving validation on optimizer work.
target_compile_options(mtgsim_tests PRIVATE
    $<$<AND:$<CONFIG:Release>,$<CXX_COMPILER_ID:GNU>>:-O0>
    $<$<AND:$<CONFIG:Release>,$<CXX_COMPILER_ID:Clang>>:-O0>
)

enable_testing()
add_test(NAME mtgsim_cpp_smoke COMMAND mtgsim_tests)
add_test(NAME mtgsim_cli_replay_artifact_roundtrip COMMAND mtgsim_cli --artifact-roundtrip ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_smoke.snapshot ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_smoke.trace)
add_test(NAME mtgsim_cli_paid_action_journal_demo COMMAND mtgsim_cli --write-paid-action-journal-demo ${CMAKE_BINARY_DIR}/mtgsim_cli_paid_action_transaction_journal.txt)
add_test(NAME mtgsim_cli_paid_action_journal_roundtrip COMMAND mtgsim_cli --paid-action-journal-roundtrip ${CMAKE_BINARY_DIR}/mtgsim_cli_paid_action_transaction_journal_roundtrip.txt)
add_test(NAME mtgsim_cli_replay_bundle_roundtrip COMMAND mtgsim_cli --artifact-bundle-roundtrip ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle.snapshot ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle.trace ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle.manifest)
add_test(NAME mtgsim_cli_paid_replay_bundle_roundtrip COMMAND mtgsim_cli --paid-replay-bundle-roundtrip ${CMAKE_BINARY_DIR}/mtgsim_cli_paid_replay_bundle.snapshot ${CMAKE_BINARY_DIR}/mtgsim_cli_paid_replay_bundle.trace ${CMAKE_BINARY_DIR}/mtgsim_cli_paid_replay_bundle.journal ${CMAKE_BINARY_DIR}/mtgsim_cli_paid_replay_bundle.manifest)
add_test(NAME mtgsim_cli_replay_bundle_inspect_roundtrip COMMAND mtgsim_cli --artifact-bundle-inspect-roundtrip ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle_inspect.snapshot ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle_inspect.trace ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle_inspect.manifest)
add_test(NAME mtgsim_cli_replay_bundle_prefix_roundtrip COMMAND mtgsim_cli --artifact-bundle-prefix-roundtrip ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle_prefix.snapshot ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle_prefix.trace ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle_prefix.manifest ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle_prefix.prefix.trace ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle_prefix.prefix.manifest)
add_test(NAME mtgsim_cli_replay_bundle_resume_roundtrip COMMAND mtgsim_cli --artifact-bundle-resume-roundtrip ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle_resume.snapshot ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle_resume.trace ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle_resume.manifest ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle_resume.resume.snapshot ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle_resume.suffix.trace ${CMAKE_BINARY_DIR}/mtgsim_cli_replay_bundle_resume.suffix.manifest)
add_test(NAME mtgsim_scenario_mana COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/mana_paid_cast.mtgscn)
add_test(NAME mtgsim_scenario_mana_auto COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/mana_auto_cast_sources.mtgscn)
add_test(NAME mtgsim_scenario_mana_auto_search COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/mana_auto_non_greedy_tap_mode.mtgscn)
add_test(NAME mtgsim_scenario_sacrifice_cost COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/sacrifice_cost_trigger_stack_order.mtgscn)
add_test(NAME mtgsim_scenario_sacrifice_cost_target_lock COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/sacrifice_cost_target_locked_before_payment.mtgscn)
add_test(NAME mtgsim_scenario_activated_sacrifice_cost COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/activated_sacrifice_cost_source_lki_stack_order.mtgscn)
add_test(NAME mtgsim_scenario_activated_cost_target_lock COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/activated_cost_target_locked_before_payment.mtgscn)
add_test(NAME mtgsim_scenario_life_cost_spell COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/life_cost_spell_payment.mtgscn)
add_test(NAME mtgsim_scenario_life_cost_activated COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/life_cost_activated_payment.mtgscn)
add_test(NAME mtgsim_scenario_target COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/targeted_bolt_player.mtgscn)
add_test(NAME mtgsim_scenario_target_lki COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/target_blink_identity_stale_before_resolution.mtgscn)
add_test(NAME mtgsim_scenario_multitarget_partial COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/multitarget_partial_resolution.mtgscn)
add_test(NAME mtgsim_scenario_stack_counterspell COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/stack_counterspell_targets_stack_object.mtgscn)
add_test(NAME mtgsim_scenario_combat COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/combat_unblocked_attack.mtgscn)
add_test(NAME mtgsim_scenario_trigger COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/trigger_etb_gain_life.mtgscn)
add_test(NAME mtgsim_scenario_trigger_self_dies_lki COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/trigger_self_dies_lki.mtgscn)
add_test(NAME mtgsim_scenario_trigger_targeted_damage COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/trigger_targeted_damage_player.mtgscn)
add_test(NAME mtgsim_scenario_trigger_self_dies_color_snapshot_protection COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/trigger_self_dies_color_snapshot_protection.mtgscn)
add_test(NAME mtgsim_scenario_prevention COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/prevention_targeted_damage.mtgscn)
add_test(NAME mtgsim_scenario_zone_replacement COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/zone_replacement_dies_exile_no_trigger.mtgscn)
add_test(NAME mtgsim_scenario_zone_replacement_scope COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/zone_replacement_source_scope.mtgscn)
add_test(NAME mtgsim_scenario_zone_replacement_recheck_choice COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/zone_replacement_recheck_choice.mtgscn)
add_test(NAME mtgsim_scenario_counter COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/counter_spell_growth.mtgscn)
add_test(NAME mtgsim_scenario_keywords COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/keyword_flying_reach.mtgscn)
add_test(NAME mtgsim_scenario_keyword_trample COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/keyword_trample_excess.mtgscn)
add_test(NAME mtgsim_scenario_keyword_indestructible COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/keyword_indestructible_damage.mtgscn)
add_test(NAME mtgsim_scenario_keyword_summoning COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/keyword_haste_summoning_sickness.mtgscn)
add_test(NAME mtgsim_scenario_keyword_targeting COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/keyword_hexproof_shroud_targeting.mtgscn)
add_test(NAME mtgsim_scenario_keyword_protection COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/keyword_protection_from_red.mtgscn)
add_test(NAME mtgsim_scenario_keyword_menace COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/keyword_menace_batch_block.mtgscn)
add_test(NAME mtgsim_scenario_destroy_regen COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/regeneration_replaces_destroy.mtgscn)
add_test(NAME mtgsim_scenario_attachments COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/attachment_aura_grants_flying.mtgscn)
add_test(NAME mtgsim_scenario_tokens COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/token_create_spell.mtgscn)
add_test(NAME mtgsim_scenario_planeswalkers COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/planeswalker_combat_attack.mtgscn)
add_test(NAME mtgsim_scenario_battles COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/battle_combat_attack.mtgscn)
add_test(NAME mtgsim_scenario_modal COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/modal_charm_damage.mtgscn)
add_test(NAME mtgsim_scenario_timing COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/timing_flash_in_combat.mtgscn)
add_test(NAME mtgsim_scenario_land_play COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/land_play_special_action.mtgscn)
add_test(NAME mtgsim_scenario_activated COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/activated_ping_stack.mtgscn)
add_test(NAME mtgsim_scenario_static_effects COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/static_anthem_layer.mtgscn)
add_test(NAME mtgsim_scenario_static_type_color COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/static_type_land_animation_layer.mtgscn)
add_test(NAME mtgsim_scenario_static_base_pt COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/static_base_pt_set_layer.mtgscn)
add_test(NAME mtgsim_scenario_static_ability_removal COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/static_ability_removal_layer.mtgscn)
add_test(NAME mtgsim_scenario_control_change COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/control_spell_steals_creature.mtgscn)
add_test(NAME mtgsim_scenario_temporary_continuous COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/temporary_pump_cleanup.mtgscn)
add_test(NAME mtgsim_scenario_copy_effects COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/copy_effect_dragon_projection.mtgscn)
add_test(NAME mtgsim_scenario_timestamp_order COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/timestamp_static_newer_type_order.mtgscn)
add_test(NAME mtgsim_scenario_layer_dependencies COMMAND mtgsim_scenario --scenario ${CMAKE_SOURCE_DIR}/tests/scenarios/dependency_ability_order.mtgscn)
add_test(NAME mtgsim_fuzz_smoke COMMAND mtgsim_fuzz --seed 7001 --steps 40)
add_test(NAME mtgsim_fuzz_risk_seams COMMAND mtgsim_fuzz --seed 7101 --steps 80 --profile risk-seams --require-risk-seams)

set_tests_properties(mtgsim_cpp_smoke PROPERTIES LABELS "cpp;core")
set_tests_properties(mtgsim_cli_replay_artifact_roundtrip mtgsim_cli_replay_bundle_roundtrip mtgsim_cli_paid_replay_bundle_roundtrip mtgsim_cli_replay_bundle_inspect_roundtrip mtgsim_cli_replay_bundle_prefix_roundtrip mtgsim_cli_paid_action_journal_demo mtgsim_cli_paid_action_journal_roundtrip PROPERTIES LABELS "cli;replay;artifacts;manifest;diagnostics;prefix;paid-action-journal")
set_tests_properties(mtgsim_scenario_mana mtgsim_scenario_mana_auto mtgsim_scenario_mana_auto_search mtgsim_scenario_sacrifice_cost mtgsim_scenario_sacrifice_cost_target_lock mtgsim_scenario_activated_sacrifice_cost mtgsim_scenario_activated_cost_target_lock mtgsim_scenario_life_cost_spell mtgsim_scenario_life_cost_activated mtgsim_scenario_target mtgsim_scenario_target_lki mtgsim_scenario_multitarget_partial mtgsim_scenario_stack_counterspell mtgsim_scenario_combat mtgsim_scenario_trigger mtgsim_scenario_trigger_self_dies_lki mtgsim_scenario_trigger_targeted_damage mtgsim_scenario_trigger_self_dies_color_snapshot_protection mtgsim_scenario_prevention mtgsim_scenario_zone_replacement mtgsim_scenario_zone_replacement_scope mtgsim_scenario_zone_replacement_recheck_choice mtgsim_scenario_counter mtgsim_scenario_keywords mtgsim_scenario_keyword_trample mtgsim_scenario_keyword_indestructible mtgsim_scenario_keyword_summoning mtgsim_scenario_keyword_targeting mtgsim_scenario_keyword_protection mtgsim_scenario_keyword_menace mtgsim_scenario_destroy_regen mtgsim_scenario_attachments mtgsim_scenario_tokens mtgsim_scenario_planeswalkers mtgsim_scenario_battles mtgsim_scenario_modal mtgsim_scenario_timing mtgsim_scenario_land_play mtgsim_scenario_activated mtgsim_scenario_static_effects mtgsim_scenario_static_type_color mtgsim_scenario_static_base_pt mtgsim_scenario_static_ability_removal mtgsim_scenario_control_change mtgsim_scenario_temporary_continuous mtgsim_scenario_copy_effects mtgsim_scenario_timestamp_order mtgsim_scenario_layer_dependencies PROPERTIES LABELS "scenario;rules")
set_tests_properties(mtgsim_fuzz_smoke mtgsim_fuzz_risk_seams PROPERTIES LABELS "fuzz;invariants;risk-seams")
