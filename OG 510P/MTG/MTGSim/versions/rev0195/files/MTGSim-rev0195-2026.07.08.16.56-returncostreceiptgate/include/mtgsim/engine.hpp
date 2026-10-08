#pragma once

#include "mtgsim/types.hpp"

#include <cstddef>
#include <cstdint>
#include <string>
#include <string_view>
#include <vector>

namespace mtgsim {

enum class JournalRetention : std::uint8_t {
    KeepAll,
    ClearAll
};

struct StartOptions {
    std::uint32_t opening_hand_size = 7;
    std::int32_t starting_life_total = 20;
    bool shuffle_libraries = true;
    bool two_player_starting_player_skips_first_draw = true;
};

[[nodiscard]] GameState make_game(std::vector<CardDefinition> definitions,
                                  const std::vector<PlayerDeck>& decks,
                                  std::uint64_t seed);

void start_game(GameState& game, const StartOptions& options = {});
void draw_card(GameState& game, PlayerId player_id);
[[nodiscard]] bool take_mulligan(GameState& game, PlayerId player_id, std::uint32_t opening_hand_size = 7);
[[nodiscard]] bool keep_mulligan_hand(GameState& game, PlayerId player_id, const std::vector<ObjectId>& bottom_cards = {});
[[nodiscard]] bool discard_card(GameState& game, PlayerId player_id, ObjectId object_id);
void lose_life(GameState& game, PlayerId player_id, std::int32_t amount);
void gain_life(GameState& game, PlayerId player_id, std::int32_t amount);
void add_mana(GameState& game, PlayerId player_id, ManaSymbol symbol, std::uint32_t amount = 1);
[[nodiscard]] bool can_pay_mana_cost(const ManaPool& pool, const ManaCost& cost) noexcept;
[[nodiscard]] bool pay_mana_cost(GameState& game, PlayerId player_id, const ManaCost& cost);
void clear_mana_pool(GameState& game, PlayerId player_id);
void clear_all_mana_pools(GameState& game);
void tap_object(GameState& game, PlayerId controller, ObjectId object_id);
[[nodiscard]] std::uint32_t mana_ability_count(const GameState& game, ObjectId object_id) noexcept;
[[nodiscard]] bool can_activate_mana_ability(const GameState& game, PlayerId controller, ObjectId object_id, std::uint32_t mana_ability_index = 1) noexcept;
[[nodiscard]] bool activate_mana_ability(GameState& game, PlayerId controller, ObjectId object_id, std::uint32_t mana_ability_index = 1);
void tap_permanent_for_mana(GameState& game, PlayerId controller, ObjectId object_id);
[[nodiscard]] bool can_pay_mana_cost_with_available_mana(const GameState& game, PlayerId player_id, const ManaCost& cost) noexcept;
[[nodiscard]] bool pay_mana_cost_with_mana_abilities(GameState& game, PlayerId player_id, const ManaCost& cost);
[[nodiscard]] bool can_cast_spell_now(const GameState& game, PlayerId caster, ObjectId object_id) noexcept;
[[nodiscard]] bool can_play_land(const GameState& game, PlayerId player_id, ObjectId object_id) noexcept;
[[nodiscard]] bool play_land_from_hand(GameState& game, PlayerId player_id, ObjectId object_id);
void untap_permanents(GameState& game, PlayerId controller);
void mark_damage(GameState& game, ObjectId object_id, std::uint32_t amount);
[[nodiscard]] ObjectId create_token(GameState& game, PlayerId controller, std::uint32_t definition_index);
[[nodiscard]] std::vector<ObjectId> create_tokens(GameState& game, PlayerId controller, std::uint32_t definition_index, std::uint32_t count);
[[nodiscard]] bool object_ceased_to_exist(const GameState& game, ObjectId object_id) noexcept;
[[nodiscard]] std::size_t zone_change_record_count(const GameState& game) noexcept;
[[nodiscard]] const ZoneChangeRecord* latest_zone_change_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t zone_change_replacement_record_count(const GameState& game) noexcept;
[[nodiscard]] const ZoneChangeReplacementRecord* latest_zone_change_replacement_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t damage_record_count(const GameState& game) noexcept;
[[nodiscard]] const DamageRecord* latest_damage_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t damage_prevention_record_count(const GameState& game) noexcept;
[[nodiscard]] const DamagePreventionRecord* latest_damage_prevention_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t life_change_record_count(const GameState& game) noexcept;
[[nodiscard]] const LifeChangeRecord* latest_life_change_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t mana_change_record_count(const GameState& game) noexcept;
[[nodiscard]] const ManaChangeRecord* latest_mana_change_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t mana_payment_plan_record_count(const GameState& game) noexcept;
[[nodiscard]] const ManaPaymentPlanRecord* latest_mana_payment_plan_record(const GameState& game) noexcept;
[[nodiscard]] std::uint64_t mana_payment_plan_record_identity_hash(const ManaPaymentPlanRecord& record) noexcept;
[[nodiscard]] std::size_t tap_cost_payment_record_count(const GameState& game) noexcept;
[[nodiscard]] const TapCostPaymentRecord* latest_tap_cost_payment_record(const GameState& game) noexcept;
[[nodiscard]] std::uint64_t tap_cost_payment_record_hash(const TapCostPaymentRecord& record) noexcept;
[[nodiscard]] std::size_t sacrifice_cost_payment_record_count(const GameState& game) noexcept;
[[nodiscard]] const SacrificeCostPaymentRecord* latest_sacrifice_cost_payment_record(const GameState& game) noexcept;
[[nodiscard]] std::uint64_t sacrifice_cost_payment_record_hash(const SacrificeCostPaymentRecord& record) noexcept;
[[nodiscard]] std::size_t discard_cost_payment_record_count(const GameState& game) noexcept;
[[nodiscard]] const DiscardCostPaymentRecord* latest_discard_cost_payment_record(const GameState& game) noexcept;
[[nodiscard]] std::uint64_t discard_cost_payment_record_hash(const DiscardCostPaymentRecord& record) noexcept;
[[nodiscard]] std::size_t life_cost_payment_record_count(const GameState& game) noexcept;
[[nodiscard]] const LifeCostPaymentRecord* latest_life_cost_payment_record(const GameState& game) noexcept;
[[nodiscard]] std::uint64_t life_cost_payment_record_hash(const LifeCostPaymentRecord& record) noexcept;
[[nodiscard]] std::size_t return_cost_payment_record_count(const GameState& game) noexcept;
[[nodiscard]] const ReturnCostPaymentRecord* latest_return_cost_payment_record(const GameState& game) noexcept;
[[nodiscard]] std::uint64_t return_cost_payment_record_hash(const ReturnCostPaymentRecord& record) noexcept;
[[nodiscard]] std::size_t loyalty_cost_payment_record_count(const GameState& game) noexcept;
[[nodiscard]] const LoyaltyCostPaymentRecord* latest_loyalty_cost_payment_record(const GameState& game) noexcept;
[[nodiscard]] std::uint64_t loyalty_cost_payment_record_hash(const LoyaltyCostPaymentRecord& record) noexcept;
[[nodiscard]] std::size_t paid_action_declaration_record_count(const GameState& game) noexcept;
[[nodiscard]] const PaidActionDeclarationRecord* latest_paid_action_declaration_record(const GameState& game) noexcept;
[[nodiscard]] std::uint64_t paid_action_declaration_record_hash(const PaidActionDeclarationRecord& record) noexcept;
[[nodiscard]] std::size_t paid_action_transaction_record_count(const GameState& game) noexcept;
[[nodiscard]] const PaidActionTransactionRecord* latest_paid_action_transaction_record(const GameState& game) noexcept;
[[nodiscard]] std::uint64_t paid_action_transaction_record_hash(const PaidActionTransactionRecord& record) noexcept;
[[nodiscard]] std::string serialize_paid_action_transaction_journal(const GameState& game);
[[nodiscard]] std::uint64_t paid_action_transaction_journal_text_hash(std::string_view text) noexcept;
[[nodiscard]] PaidActionTransactionJournalParseResult parse_paid_action_transaction_journal(std::string_view text);
[[nodiscard]] PaidActionTransactionJournalVerifyResult verify_paid_action_transaction_journal(std::string_view text);
[[nodiscard]] PaidActionTransactionJournalVerifyResult verify_paid_action_transaction_journal_for_state(const GameState& game, std::string_view text);
[[nodiscard]] std::size_t counter_change_record_count(const GameState& game) noexcept;
[[nodiscard]] const CounterChangeRecord* latest_counter_change_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t discard_record_count(const GameState& game) noexcept;
[[nodiscard]] const DiscardRecord* latest_discard_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t trigger_record_count(const GameState& game) noexcept;
[[nodiscard]] const TriggerRecord* latest_trigger_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t event_record_count(const GameState& game) noexcept;
[[nodiscard]] const EventRecord* latest_event_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t stack_placement_record_count(const GameState& game) noexcept;
[[nodiscard]] const StackPlacementRecord* latest_stack_placement_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t stack_resolution_record_count(const GameState& game) noexcept;
[[nodiscard]] const StackResolutionRecord* latest_stack_resolution_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t priority_transition_record_count(const GameState& game) noexcept;
[[nodiscard]] const PriorityTransitionRecord* latest_priority_transition_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t state_based_action_record_count(const GameState& game) noexcept;
[[nodiscard]] const StateBasedActionRecord* latest_state_based_action_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t combat_declaration_record_count(const GameState& game) noexcept;
[[nodiscard]] const CombatDeclarationRecord* latest_combat_declaration_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t combat_damage_assignment_record_count(const GameState& game) noexcept;
[[nodiscard]] const CombatDamageAssignmentRecord* latest_combat_damage_assignment_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t draw_record_count(const GameState& game) noexcept;
[[nodiscard]] const DrawRecord* latest_draw_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t mulligan_record_count(const GameState& game) noexcept;
[[nodiscard]] const MulliganRecord* latest_mulligan_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t mulligan_keep_record_count(const GameState& game) noexcept;
[[nodiscard]] const MulliganKeepRecord* latest_mulligan_keep_record(const GameState& game) noexcept;
[[nodiscard]] std::size_t action_receipt_record_count(const GameState& game) noexcept;
[[nodiscard]] const ActionReceiptRecord* latest_action_receipt_record(const GameState& game) noexcept;
[[nodiscard]] std::uint64_t action_receipt_hash(const ActionReceiptRecord& receipt) noexcept;
[[nodiscard]] std::string canonical_action_string(const LegalAction& action);
[[nodiscard]] std::uint64_t legal_action_hash(const LegalAction& action) noexcept;
[[nodiscard]] std::uint64_t legal_action_page_hash(const LegalActionPage& page) noexcept;
[[nodiscard]] std::uint64_t legal_action_page_location_hash(const LegalActionPageLocation& location) noexcept;
[[nodiscard]] std::vector<PlayerId> apnap_ordered_players(const GameState& game);
[[nodiscard]] ChoiceRequest choice_request_for_player(const GameState& game, PlayerId player_id);
[[nodiscard]] ChoiceRequestQueue choice_request_queue(const GameState& game);
[[nodiscard]] ChoiceRequest current_choice_request(const GameState& game);
[[nodiscard]] std::uint64_t choice_request_hash(const ChoiceRequest& request) noexcept;
[[nodiscard]] std::uint64_t choice_request_queue_hash(const ChoiceRequestQueue& queue) noexcept;
[[nodiscard]] std::uint64_t choice_queue_location_hash(const ChoiceQueueLocation& location) noexcept;
[[nodiscard]] StateCheckpointSeal make_state_checkpoint_seal(const GameState& game) noexcept;
[[nodiscard]] bool verify_state_checkpoint_seal(const GameState& game, const StateCheckpointSeal& checkpoint) noexcept;
[[nodiscard]] std::string serialize_state_checkpoint_seal(const StateCheckpointSeal& checkpoint);
[[nodiscard]] StateCheckpointParseResult parse_state_checkpoint_seal(std::string_view text);
[[nodiscard]] std::string serialize_state_core_snapshot(const GameState& game);
[[nodiscard]] StateCoreSnapshotParseResult parse_state_core_snapshot(std::string_view text);
[[nodiscard]] std::uint64_t replay_artifact_text_hash(std::string_view text) noexcept;
[[nodiscard]] ReplayArtifactManifest make_replay_artifact_manifest(std::string_view snapshot_text,
                                                                  std::string_view trace_text,
                                                                  const GameState& final_state,
                                                                  bool applied_only = true);
[[nodiscard]] ReplayArtifactManifest make_replay_artifact_manifest_with_paid_action_journal(std::string_view snapshot_text,
                                                                                           std::string_view trace_text,
                                                                                           const GameState& final_state,
                                                                                           std::string_view paid_action_journal_text,
                                                                                           bool applied_only = true);
[[nodiscard]] std::string serialize_replay_artifact_manifest(const ReplayArtifactManifest& manifest);
[[nodiscard]] ReplayArtifactManifestParseResult parse_replay_artifact_manifest(std::string_view text);
[[nodiscard]] ReplayArtifactVerifyResult verify_replay_artifact_bundle(std::string_view snapshot_text,
                                                                       std::string_view trace_text,
                                                                       const ReplayArtifactManifest& manifest);
[[nodiscard]] ReplayArtifactVerifyResult verify_replay_artifact_bundle_with_paid_action_journal(std::string_view snapshot_text,
                                                                                               std::string_view trace_text,
                                                                                               std::string_view paid_action_journal_text,
                                                                                               const ReplayArtifactManifest& manifest);
[[nodiscard]] ReplayArtifactPrefixResult make_replay_artifact_prefix_bundle(std::string_view snapshot_text,
                                                                                     std::string_view trace_text,
                                                                                     const ReplayArtifactManifest& manifest);
[[nodiscard]] ReplayArtifactResumeResult make_replay_artifact_resume_probe(std::string_view snapshot_text,
                                                                                     std::string_view trace_text,
                                                                                     const ReplayArtifactManifest& manifest);
[[nodiscard]] std::uint64_t canonical_state_hash(const GameState& game) noexcept;
[[nodiscard]] std::uint64_t journal_hash(const GameState& game) noexcept;
[[nodiscard]] std::size_t journal_entry_count(const GameState& game) noexcept;
[[nodiscard]] std::size_t journal_reserved_capacity_bytes(const GameState& game) noexcept;
void clear_journal(GameState& game) noexcept;
[[nodiscard]] GameState make_branch_state(const GameState& source, JournalRetention retention = JournalRetention::ClearAll);
[[nodiscard]] bool exile_permanent(GameState& game, ObjectId object_id);
[[nodiscard]] bool sacrifice_permanent(GameState& game, PlayerId controller, ObjectId object_id);
[[nodiscard]] bool gain_control_of_permanent(GameState& game, PlayerId new_controller, ObjectId object_id);
[[nodiscard]] bool become_copy_of_permanent(GameState& game, ObjectId object_id, ObjectId source_id);
void clear_copy_effect(GameState& game, ObjectId object_id);
[[nodiscard]] bool object_has_copy_effect(const GameState& game, ObjectId object_id) noexcept;
[[nodiscard]] std::uint32_t object_copiable_definition_index(const GameState& game, ObjectId object_id) noexcept;
void add_regeneration_shield(GameState& game, ObjectId object_id, std::uint32_t amount = 1);
[[nodiscard]] std::uint32_t regeneration_shield_count(const GameState& game, ObjectId object_id) noexcept;
[[nodiscard]] bool destroy_permanent(GameState& game, ObjectId object_id, bool allow_regeneration = true);
void add_counter_to_object(GameState& game, ObjectId object_id, CounterKind counter_kind, std::uint32_t amount = 1);
void remove_counter_from_object(GameState& game, ObjectId object_id, CounterKind counter_kind, std::uint32_t amount = 1);
void add_counter_to_player(GameState& game, PlayerId player_id, CounterKind counter_kind, std::uint32_t amount = 1);
[[nodiscard]] std::uint32_t object_counter_count(const GameState& game, ObjectId object_id, CounterKind counter_kind) noexcept;
[[nodiscard]] std::uint32_t player_counter_count(const GameState& game, PlayerId player_id, CounterKind counter_kind) noexcept;
[[nodiscard]] std::uint32_t planeswalker_loyalty(const GameState& game, ObjectId object_id) noexcept;
[[nodiscard]] std::uint32_t battle_defense(const GameState& game, ObjectId object_id) noexcept;
[[nodiscard]] PlayerId battle_protector(const GameState& game, ObjectId object_id) noexcept;
[[nodiscard]] bool set_battle_protector(GameState& game, ObjectId object_id, PlayerId protector);
[[nodiscard]] bool can_activate_activated_ability(const GameState& game, PlayerId controller, ObjectId object_id, std::uint32_t ability_index, TargetRef target = {}) noexcept;
[[nodiscard]] bool can_activate_activated_ability_with_targets(const GameState& game, PlayerId controller, ObjectId object_id, std::uint32_t ability_index, const std::vector<TargetRef>& targets) noexcept;
[[nodiscard]] bool activate_activated_ability(GameState& game, PlayerId controller, ObjectId object_id, std::uint32_t ability_index, TargetRef target = {});
[[nodiscard]] bool activate_activated_ability_with_targets(GameState& game, PlayerId controller, ObjectId object_id, std::uint32_t ability_index, const std::vector<TargetRef>& targets);
[[nodiscard]] bool can_activate_loyalty_ability(const GameState& game, PlayerId controller, ObjectId object_id, TargetRef target = {}) noexcept;
[[nodiscard]] bool can_activate_loyalty_ability_with_targets(const GameState& game, PlayerId controller, ObjectId object_id, const std::vector<TargetRef>& targets) noexcept;
[[nodiscard]] bool activate_loyalty_ability(GameState& game, PlayerId controller, ObjectId object_id, TargetRef target = {});
[[nodiscard]] bool activate_loyalty_ability_with_targets(GameState& game, PlayerId controller, ObjectId object_id, const std::vector<TargetRef>& targets);
[[nodiscard]] bool object_has_ability(const GameState& game, ObjectId object_id, KeywordAbilityMask ability) noexcept;
void create_continuous_effect(GameState& game, ObjectId source_id, PlayerId controller, const StaticEffectDefinition& effect, ContinuousEffectDuration duration, const std::vector<TargetRef>& targets = {});
[[nodiscard]] std::size_t continuous_effect_count(const GameState& game) noexcept;
void expire_continuous_effects(GameState& game, ContinuousEffectDuration duration);
[[nodiscard]] std::int32_t static_power_modifier(const GameState& game, ObjectId object_id) noexcept;
[[nodiscard]] std::int32_t static_toughness_modifier(const GameState& game, ObjectId object_id) noexcept;
[[nodiscard]] bool can_attach_object(const GameState& game, ObjectId attachment_id, TargetRef target) noexcept;
[[nodiscard]] bool attach_object_to(GameState& game, ObjectId attachment_id, TargetRef target);
void detach_object(GameState& game, ObjectId attachment_id);
[[nodiscard]] TargetRef object_attachment_target(const GameState& game, ObjectId attachment_id) noexcept;
[[nodiscard]] std::uint32_t attachment_count_for_target(const GameState& game, TargetRef target) noexcept;
[[nodiscard]] std::uint32_t card_color_mask(const CardDefinition& definition) noexcept;
[[nodiscard]] std::uint32_t object_type_mask(const GameState& game, ObjectId object_id) noexcept;
[[nodiscard]] bool object_has_type(const GameState& game, ObjectId object_id, CardTypeMask type) noexcept;
[[nodiscard]] std::uint32_t object_color_mask(const GameState& game, ObjectId object_id) noexcept;
[[nodiscard]] bool object_has_protection_from_color(const GameState& game, ObjectId object_id, CardColorMask color) noexcept;
[[nodiscard]] bool target_has_protection_from_source(const GameState& game, TargetRef target, ObjectId source_id) noexcept;
[[nodiscard]] bool object_has_summoning_sickness(const GameState& game, ObjectId object_id) noexcept;
[[nodiscard]] std::int32_t effective_power(const GameState& game, ObjectId object_id) noexcept;
[[nodiscard]] std::int32_t effective_toughness(const GameState& game, ObjectId object_id) noexcept;
void add_damage_prevention_shield(GameState& game, TargetRef target, std::uint32_t amount, std::string label = {}, std::uint32_t choice_rank = 0U);
[[nodiscard]] std::uint32_t damage_prevention_shield_total(const GameState& game, TargetRef target) noexcept;
[[nodiscard]] std::size_t damage_prevention_shield_count(const GameState& game) noexcept;
void deal_damage_to_target(GameState& game, ObjectId source_id, TargetRef target, std::uint32_t amount);
void deal_unpreventable_damage_to_target(GameState& game, ObjectId source_id, TargetRef target, std::uint32_t amount);
[[nodiscard]] std::size_t pending_trigger_count(const GameState& game) noexcept;
void put_pending_triggers_on_stack(GameState& game);
bool put_pending_triggers_on_stack(GameState& game, const std::vector<u32>& trigger_order);

[[nodiscard]] bool can_declare_attacker(const GameState& game, PlayerId attacker_controller, ObjectId attacker_id, PlayerId defending_player) noexcept;
[[nodiscard]] bool declare_attacker(GameState& game, PlayerId attacker_controller, ObjectId attacker_id, PlayerId defending_player);
[[nodiscard]] bool can_declare_attacker_to_target(const GameState& game, PlayerId attacker_controller, ObjectId attacker_id, TargetRef defending_target) noexcept;
[[nodiscard]] bool declare_attacker_to_target(GameState& game, PlayerId attacker_controller, ObjectId attacker_id, TargetRef defending_target);
[[nodiscard]] bool can_declare_attackers(const GameState& game, PlayerId attacker_controller, const std::vector<AttackAssignment>& assignments) noexcept;
[[nodiscard]] bool declare_attackers(GameState& game, PlayerId attacker_controller, const std::vector<AttackAssignment>& assignments);
[[nodiscard]] LegalAction make_declare_attackers_action(PlayerId attacker_controller, const std::vector<AttackAssignment>& assignments);
[[nodiscard]] std::vector<AttackAssignment> attack_assignments_from_action(const LegalAction& action);
[[nodiscard]] bool can_declare_blocker(const GameState& game, PlayerId blocker_controller, ObjectId blocker_id, ObjectId attacker_id) noexcept;
[[nodiscard]] bool can_block_attacker_by_evasion(const GameState& game, ObjectId blocker_id, ObjectId attacker_id) noexcept;
[[nodiscard]] bool declare_blocker(GameState& game, PlayerId blocker_controller, ObjectId blocker_id, ObjectId attacker_id);
[[nodiscard]] bool can_declare_blockers(const GameState& game, PlayerId blocker_controller, const std::vector<BlockAssignment>& assignments) noexcept;
[[nodiscard]] bool declare_blockers(GameState& game, PlayerId blocker_controller, const std::vector<BlockAssignment>& assignments);
[[nodiscard]] LegalAction make_declare_blockers_action(PlayerId blocker_controller, const std::vector<BlockAssignment>& assignments);
[[nodiscard]] std::vector<BlockAssignment> block_assignments_from_action(const LegalAction& action);
[[nodiscard]] bool can_order_combat_damage(const GameState& game, PlayerId controller, ObjectId attacker_id, const std::vector<ObjectId>& blocker_order);
[[nodiscard]] bool order_combat_damage(GameState& game, PlayerId controller, ObjectId attacker_id, const std::vector<ObjectId>& blocker_order);
[[nodiscard]] LegalAction make_order_combat_damage_action(PlayerId controller, ObjectId attacker_id, const std::vector<ObjectId>& blocker_order);
[[nodiscard]] std::vector<ObjectId> combat_damage_order_from_action(const LegalAction& action);
void assign_combat_damage(GameState& game);
void clear_combat_assignments(GameState& game);
[[nodiscard]] bool target_ref_is_legal(const GameState& game, TargetRef target, std::uint32_t target_mask) noexcept;
[[nodiscard]] bool target_ref_is_legal_for_source(const GameState& game, TargetRef target, std::uint32_t target_mask, PlayerId source_controller) noexcept;
[[nodiscard]] bool target_ref_is_legal_for_source_object(const GameState& game, TargetRef target, std::uint32_t target_mask, ObjectId source_id) noexcept;
[[nodiscard]] std::vector<TargetRef> enumerate_legal_targets(const GameState& game, std::uint32_t target_mask);
[[nodiscard]] std::vector<TargetRef> enumerate_legal_targets_for_source(const GameState& game, std::uint32_t target_mask, PlayerId source_controller);
[[nodiscard]] std::vector<TargetRef> enumerate_legal_targets_for_source_object(const GameState& game, std::uint32_t target_mask, ObjectId source_id);
[[nodiscard]] std::vector<std::vector<TargetRef>> enumerate_legal_target_sets_for_source_object(const GameState& game, std::uint32_t target_mask, std::uint32_t target_count, ObjectId source_id);
[[nodiscard]] std::uint64_t target_choice_set_hash(const std::vector<TargetRef>& targets) noexcept;
[[nodiscard]] std::uint64_t mode_choice_contract_hash(const SpellModeDefinition& mode) noexcept;
void discard_down_to_max_hand_size(GameState& game, PlayerId player_id);
void apply_state_based_actions(GameState& game);
void move_object(GameState& game, ObjectId object_id, PlayerId target_controller, Zone target_zone);
void cast_from_hand_to_stack(GameState& game, PlayerId caster, ObjectId object_id);
[[nodiscard]] bool cast_from_hand_to_stack_paying_mana(GameState& game, PlayerId caster, ObjectId object_id);
[[nodiscard]] bool cast_from_hand_to_stack_paying_mana_with_target(GameState& game, PlayerId caster, ObjectId object_id, TargetRef target);
[[nodiscard]] bool cast_from_hand_to_stack_paying_mana_with_targets(GameState& game, PlayerId caster, ObjectId object_id, const std::vector<TargetRef>& targets);
[[nodiscard]] bool cast_from_hand_to_stack_paying_mana_with_mode(GameState& game, PlayerId caster, ObjectId object_id, std::uint32_t mode_index, TargetRef target = {});
[[nodiscard]] bool cast_from_hand_to_stack_paying_mana_with_mode_and_targets(GameState& game, PlayerId caster, ObjectId object_id, std::uint32_t mode_index, const std::vector<TargetRef>& targets);
void resolve_top_of_stack(GameState& game);
void pass_priority(GameState& game);
void advance_step(GameState& game);

[[nodiscard]] std::vector<LegalAction> enumerate_legal_actions(const GameState& game, PlayerId player_id);
[[nodiscard]] LegalActionFrontier enumerate_legal_action_frontier(const GameState& game, PlayerId player_id);
[[nodiscard]] LegalActionPage enumerate_legal_action_page(const GameState& game, PlayerId player_id, std::uint64_t cursor, std::uint64_t limit);
[[nodiscard]] LegalActionPageLocation locate_legal_action_page(const GameState& game, const LegalAction& action, std::uint64_t page_limit = 128U);
[[nodiscard]] LegalActionValidation validate_legal_action(const GameState& game, const LegalAction& action);
[[nodiscard]] bool is_legal_action(const GameState& game, const LegalAction& action);
[[nodiscard]] TransitionResult pending_transition_for_player(const GameState& game, PlayerId player_id);
[[nodiscard]] TransitionResult commit_action_transition(GameState& game, const LegalAction& action);
[[nodiscard]] bool transition_result_matches_receipt(const TransitionResult& result, const ActionReceiptRecord& receipt) noexcept;
[[nodiscard]] ActionTraceEntry action_trace_entry_from_transition_result(const TransitionResult& result);
[[nodiscard]] std::uint64_t action_trace_entry_hash(const ActionTraceEntry& entry) noexcept;
[[nodiscard]] bool transition_result_matches_action_trace_entry(const TransitionResult& result, const ActionTraceEntry& entry) noexcept;
[[nodiscard]] std::uint64_t transition_result_trace_entry_hash(const TransitionResult& result) noexcept;
[[nodiscard]] std::uint64_t transition_result_trace_handoff_hash(const TransitionResult& result) noexcept;
[[nodiscard]] std::uint64_t transition_result_preflight_hash(const TransitionResult& result) noexcept;
[[nodiscard]] std::uint64_t transition_result_boundary_hash(const TransitionResult& result) noexcept;
[[nodiscard]] TransitionBoundaryVerifyResult check_transition_result_boundary(const TransitionResult& result, const GameState& before, const GameState& after) noexcept;
[[nodiscard]] bool verify_transition_result_boundary(const TransitionResult& result, const GameState& before, const GameState& after) noexcept;
[[nodiscard]] bool apply_action(GameState& game, const LegalAction& action);
[[nodiscard]] LegalAction action_from_receipt(const ActionReceiptRecord& receipt);
[[nodiscard]] std::vector<ActionTraceEntry> export_action_trace(const GameState& game, bool applied_only = true);
[[nodiscard]] std::string serialize_action_trace(const std::vector<ActionTraceEntry>& trace);
[[nodiscard]] ActionTraceParseResult parse_action_trace(std::string_view text);
[[nodiscard]] ActionReplayResult replay_action_trace(GameState& game, const std::vector<ActionTraceEntry>& trace);
[[nodiscard]] ActionReplayResult replay_action_trace_from_checkpoint(GameState& game, const StateCheckpointSeal& checkpoint, const std::vector<ActionTraceEntry>& trace);

[[nodiscard]] PlayerId next_player_in_turn_order(const GameState& game, PlayerId from);
[[nodiscard]] std::uint32_t alive_player_count(const GameState& game);
[[nodiscard]] std::string debug_summary(const GameState& game);

void record_event(GameState& game, std::string kind, std::string detail);

} // namespace mtgsim
