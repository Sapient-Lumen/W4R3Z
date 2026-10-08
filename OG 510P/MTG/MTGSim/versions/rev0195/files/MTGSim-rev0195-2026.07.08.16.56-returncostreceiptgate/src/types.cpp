#include "mtgsim/types.hpp"

#include <sstream>

namespace mtgsim {

const char* to_string(Zone zone_name) noexcept {
    switch (zone_name) {
        case Zone::Library: return "library";
        case Zone::Hand: return "hand";
        case Zone::Battlefield: return "battlefield";
        case Zone::Graveyard: return "graveyard";
        case Zone::Stack: return "stack";
        case Zone::Exile: return "exile";
        case Zone::Command: return "command";
        case Zone::Ante: return "ante";
        case Zone::Count: return "count";
    }
    return "unknown";
}


const char* to_string(ManaSymbol symbol) noexcept {
    switch (symbol) {
        case ManaSymbol::White: return "white";
        case ManaSymbol::Blue: return "blue";
        case ManaSymbol::Black: return "black";
        case ManaSymbol::Red: return "red";
        case ManaSymbol::Green: return "green";
        case ManaSymbol::Colorless: return "colorless";
        case ManaSymbol::Count: return "count";
    }
    return "unknown";
}

const char* to_string(CardColorMask color) noexcept {
    switch (color) {
        case ColorNone: return "none";
        case ColorWhite: return "white";
        case ColorBlue: return "blue";
        case ColorBlack: return "black";
        case ColorRed: return "red";
        case ColorGreen: return "green";
        case ColorAll: return "all";
    }
    return "unknown";
}

const char* to_string(CounterKind counter_kind) noexcept {
    switch (counter_kind) {
        case CounterKind::PlusOnePlusOne: return "+1/+1";
        case CounterKind::MinusOneMinusOne: return "-1/-1";
        case CounterKind::Loyalty: return "loyalty";
        case CounterKind::Defense: return "defense";
        case CounterKind::Charge: return "charge";
        case CounterKind::Poison: return "poison";
        case CounterKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(KeywordAbilityMask ability) noexcept {
    switch (ability) {
        case AbilityNone: return "none";
        case AbilityFlying: return "flying";
        case AbilityReach: return "reach";
        case AbilityDeathtouch: return "deathtouch";
        case AbilityLifelink: return "lifelink";
        case AbilityVigilance: return "vigilance";
        case AbilityFirstStrike: return "first_strike";
        case AbilityDoubleStrike: return "double_strike";
        case AbilityTrample: return "trample";
        case AbilityIndestructible: return "indestructible";
        case AbilityHaste: return "haste";
        case AbilityDefender: return "defender";
        case AbilityHexproof: return "hexproof";
        case AbilityShroud: return "shroud";
        case AbilityMenace: return "menace";
        case AbilityFlash: return "flash";
    }
    return "unknown";
}

const char* to_string(Phase phase) noexcept {
    switch (phase) {
        case Phase::Beginning: return "beginning";
        case Phase::PrecombatMain: return "precombat_main";
        case Phase::Combat: return "combat";
        case Phase::PostcombatMain: return "postcombat_main";
        case Phase::Ending: return "ending";
    }
    return "unknown";
}

const char* to_string(Step step) noexcept {
    switch (step) {
        case Step::Untap: return "untap";
        case Step::Upkeep: return "upkeep";
        case Step::Draw: return "draw";
        case Step::Main1: return "main1";
        case Step::BeginningOfCombat: return "beginning_of_combat";
        case Step::DeclareAttackers: return "declare_attackers";
        case Step::DeclareBlockers: return "declare_blockers";
        case Step::CombatDamage: return "combat_damage";
        case Step::EndOfCombat: return "end_of_combat";
        case Step::Main2: return "main2";
        case Step::End: return "end";
        case Step::Cleanup: return "cleanup";
    }
    return "unknown";
}

const char* to_string(ActionKind action) noexcept {
    switch (action) {
        case ActionKind::PassPriority: return "pass_priority";
        case ActionKind::CastSpellFromHandPaid: return "cast_spell_from_hand_paid";
        case ActionKind::PlayLand: return "play_land";
        case ActionKind::ActivateTapManaAbility: return "activate_tap_mana_ability";
        case ActionKind::ActivateManaAbility: return "activate_mana_ability";
        case ActionKind::ActivateActivatedAbility: return "activate_activated_ability";
        case ActionKind::ActivateLoyaltyAbility: return "activate_loyalty_ability";
        case ActionKind::DeclareAttacker: return "declare_attacker";
        case ActionKind::DeclareBlocker: return "declare_blocker";
        case ActionKind::OrderCombatDamage: return "order_combat_damage";
        case ActionKind::PutPendingTriggersOnStack: return "put_pending_triggers_on_stack";
        case ActionKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(ChoiceRequestKind choice_request_kind) noexcept {
    switch (choice_request_kind) {
        case ChoiceRequestKind::None: return "none";
        case ChoiceRequestKind::PriorityAction: return "priority_action";
        case ChoiceRequestKind::PendingTriggersToStack: return "pending_triggers_to_stack";
        case ChoiceRequestKind::DeclareAttackers: return "declare_attackers";
        case ChoiceRequestKind::DeclareBlockers: return "declare_blockers";
        case ChoiceRequestKind::OrderCombatDamage: return "order_combat_damage";
        case ChoiceRequestKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(LegalActionValidationSource source) noexcept {
    switch (source) {
        case LegalActionValidationSource::None: return "none";
        case LegalActionValidationSource::OfferedAction: return "offered_action";
        case LegalActionValidationSource::DirectDomainValidation: return "direct_domain_validation";
        case LegalActionValidationSource::Count: return "count";
    }
    return "unknown";
}

const char* to_string(TransitionBoundaryFailureKind failure) noexcept {
    switch (failure) {
        case TransitionBoundaryFailureKind::None: return "none";
        case TransitionBoundaryFailureKind::StatusInvalid: return "status_invalid";
        case TransitionBoundaryFailureKind::BoundarySealMissing: return "boundary_seal_missing";
        case TransitionBoundaryFailureKind::BoundarySealMismatch: return "boundary_seal_mismatch";
        case TransitionBoundaryFailureKind::PreflightSealMissing: return "preflight_seal_missing";
        case TransitionBoundaryFailureKind::PreflightSealMismatch: return "preflight_seal_mismatch";
        case TransitionBoundaryFailureKind::CheckpointSealMismatch: return "checkpoint_seal_mismatch";
        case TransitionBoundaryFailureKind::BeforeCheckpointMismatch: return "before_checkpoint_mismatch";
        case TransitionBoundaryFailureKind::AfterCheckpointMismatch: return "after_checkpoint_mismatch";
        case TransitionBoundaryFailureKind::NeedChoiceMutation: return "need_choice_mutation";
        case TransitionBoundaryFailureKind::NeedChoiceMissingActions: return "need_choice_missing_actions";
        case TransitionBoundaryFailureKind::NeedChoiceCausalReceipt: return "need_choice_causal_receipt";
        case TransitionBoundaryFailureKind::RejectedMutation: return "rejected_mutation";
        case TransitionBoundaryFailureKind::RejectedCausalReceipt: return "rejected_causal_receipt";
        case TransitionBoundaryFailureKind::CommittedAtomicGuardMissing: return "committed_atomic_guard_missing";
        case TransitionBoundaryFailureKind::TraceEntrySealMissing: return "trace_entry_seal_missing";
        case TransitionBoundaryFailureKind::TraceEntrySealMismatch: return "trace_entry_seal_mismatch";
        case TransitionBoundaryFailureKind::TraceHandoffSealMissing: return "trace_handoff_seal_missing";
        case TransitionBoundaryFailureKind::TraceHandoffSealMismatch: return "trace_handoff_seal_mismatch";
        case TransitionBoundaryFailureKind::ReceiptCountMismatch: return "receipt_count_mismatch";
        case TransitionBoundaryFailureKind::ReceiptMissing: return "receipt_missing";
        case TransitionBoundaryFailureKind::ReceiptIndexMismatch: return "receipt_index_mismatch";
        case TransitionBoundaryFailureKind::ReceiptHashMismatch: return "receipt_hash_mismatch";
        case TransitionBoundaryFailureKind::ReceiptResultMismatch: return "receipt_result_mismatch";
        case TransitionBoundaryFailureKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(TargetKind target_kind) noexcept {
    switch (target_kind) {
        case TargetKind::None: return "none";
        case TargetKind::Player: return "player";
        case TargetKind::Object: return "object";
    }
    return "unknown";
}

const char* to_string(AttachmentKind attachment_kind) noexcept {
    switch (attachment_kind) {
        case AttachmentKind::None: return "none";
        case AttachmentKind::Aura: return "aura";
        case AttachmentKind::Equipment: return "equipment";
        case AttachmentKind::Fortification: return "fortification";
        case AttachmentKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(EffectKind effect_kind) noexcept {
    switch (effect_kind) {
        case EffectKind::None: return "none";
        case EffectKind::DealDamage: return "deal_damage";
        case EffectKind::DrawCards: return "draw_cards";
        case EffectKind::GainLife: return "gain_life";
        case EffectKind::AddCounters: return "add_counters";
        case EffectKind::DestroyPermanent: return "destroy_permanent";
        case EffectKind::RegeneratePermanent: return "regenerate_permanent";
        case EffectKind::ExilePermanent: return "exile_permanent";
        case EffectKind::CreateToken: return "create_token";
        case EffectKind::GainControlPermanent: return "gain_control_permanent";
        case EffectKind::CreateContinuousEffect: return "create_continuous_effect";
        case EffectKind::BecomeCopyPermanent: return "become_copy_permanent";
        case EffectKind::CounterSpell: return "counter_spell";
        case EffectKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(TriggerEventKind trigger_event) noexcept {
    switch (trigger_event) {
        case TriggerEventKind::None: return "none";
        case TriggerEventKind::CreatureEntersBattlefield: return "creature_enters_battlefield";
        case TriggerEventKind::CreatureDies: return "creature_dies";
        case TriggerEventKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(EventRecordKind event_record_kind) noexcept {
    switch (event_record_kind) {
        case EventRecordKind::Log: return "log";
        case EventRecordKind::ZoneChange: return "zone_change";
        case EventRecordKind::ZoneReplacement: return "zone_replacement";
        case EventRecordKind::Damage: return "damage";
        case EventRecordKind::DamagePrevention: return "damage_prevention";
        case EventRecordKind::LifeChange: return "life_change";
        case EventRecordKind::ManaChange: return "mana_change";
        case EventRecordKind::CounterChange: return "counter_change";
        case EventRecordKind::Discard: return "discard";
        case EventRecordKind::TriggerQueued: return "trigger_queued";
        case EventRecordKind::TriggerPutOnStack: return "trigger_put_on_stack";
        case EventRecordKind::TriggerDropped: return "trigger_dropped";
        case EventRecordKind::StackPlacement: return "stack_placement";
        case EventRecordKind::StackResolution: return "stack_resolution";
        case EventRecordKind::PriorityTransition: return "priority_transition";
        case EventRecordKind::StateBasedAction: return "state_based_action";
        case EventRecordKind::CombatDeclaration: return "combat_declaration";
        case EventRecordKind::CombatDamageAssignment: return "combat_damage_assignment";
        case EventRecordKind::PaidActionDeclaration: return "paid_action_declaration";
        case EventRecordKind::PaidActionTransaction: return "paid_action_transaction";
        case EventRecordKind::ManaPaymentPlan: return "mana_payment_plan";
        case EventRecordKind::Draw: return "draw";
        case EventRecordKind::Mulligan: return "mulligan";
        case EventRecordKind::MulliganKeep: return "mulligan_keep";
        case EventRecordKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(ReplacementPriorityTier priority_tier) noexcept {
    switch (priority_tier) {
        case ReplacementPriorityTier::SelfReplacement: return "self_replacement";
        case ReplacementPriorityTier::ControlEntering: return "control_entering";
        case ReplacementPriorityTier::CopyEntering: return "copy_entering";
        case ReplacementPriorityTier::BackFaceEntering: return "back_face_entering";
        case ReplacementPriorityTier::General: return "general";
        case ReplacementPriorityTier::Count: return "count";
    }
    return "unknown";
}

const char* to_string(StackPlacementKind stack_placement_kind) noexcept {
    switch (stack_placement_kind) {
        case StackPlacementKind::SpellCast: return "spell_cast";
        case StackPlacementKind::ActivatedAbility: return "activated_ability";
        case StackPlacementKind::LoyaltyAbility: return "loyalty_ability";
        case StackPlacementKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(PaidActionTransactionOutcome outcome) noexcept {
    switch (outcome) {
        case PaidActionTransactionOutcome::Committed: return "committed";
        case PaidActionTransactionOutcome::RolledBack: return "rolled_back";
        case PaidActionTransactionOutcome::Count: return "count";
    }
    return "unknown";
}

const char* to_string(StackResolutionOutcome outcome) noexcept {
    switch (outcome) {
        case StackResolutionOutcome::Resolved: return "resolved";
        case StackResolutionOutcome::NoLegalTargets: return "no_legal_targets";
        case StackResolutionOutcome::InvalidMode: return "invalid_mode";
        case StackResolutionOutcome::AuraAttachFailed: return "aura_attach_failed";
        case StackResolutionOutcome::Count: return "count";
    }
    return "unknown";
}

const char* to_string(TargetLegalityFailureKind failure_kind) noexcept {
    switch (failure_kind) {
        case TargetLegalityFailureKind::None: return "none";
        case TargetLegalityFailureKind::EmptyTarget: return "empty_target";
        case TargetLegalityFailureKind::TargetKindNotAllowed: return "target_kind_not_allowed";
        case TargetLegalityFailureKind::PlayerMissingOrLost: return "player_missing_or_lost";
        case TargetLegalityFailureKind::ObjectMissing: return "object_missing";
        case TargetLegalityFailureKind::ObjectZoneNotAllowed: return "object_zone_not_allowed";
        case TargetLegalityFailureKind::ObjectZoneChangeMismatch: return "object_zone_change_mismatch";
        case TargetLegalityFailureKind::Shroud: return "shroud";
        case TargetLegalityFailureKind::Hexproof: return "hexproof";
        case TargetLegalityFailureKind::Protection: return "protection";
        case TargetLegalityFailureKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(PriorityTransitionOutcome outcome) noexcept {
    switch (outcome) {
        case PriorityTransitionOutcome::PriorityAdvanced: return "priority_advanced";
        case PriorityTransitionOutcome::StackResolved: return "stack_resolved";
        case PriorityTransitionOutcome::StepAdvanced: return "step_advanced";
        case PriorityTransitionOutcome::PendingTriggersPutOnStack: return "pending_triggers_put_on_stack";
        case PriorityTransitionOutcome::NoAlivePlayers: return "no_alive_players";
        case PriorityTransitionOutcome::Count: return "count";
    }
    return "unknown";
}

const char* to_string(StateBasedActionKind state_based_action_kind) noexcept {
    switch (state_based_action_kind) {
        case StateBasedActionKind::PlayerLost: return "player_lost";
        case StateBasedActionKind::CounterPairCancel: return "counter_pair_cancel";
        case StateBasedActionKind::CreatureToughnessGraveyard: return "creature_toughness_graveyard";
        case StateBasedActionKind::CreatureDamageDestroy: return "creature_damage_destroy";
        case StateBasedActionKind::PlaneswalkerLoyaltyGraveyard: return "planeswalker_loyalty_graveyard";
        case StateBasedActionKind::BattleDefenseGraveyard: return "battle_defense_graveyard";
        case StateBasedActionKind::AttachmentUnattach: return "attachment_unattach";
        case StateBasedActionKind::AuraGraveyard: return "aura_graveyard";
        case StateBasedActionKind::TokenCease: return "token_cease";
        case StateBasedActionKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(CombatDeclarationKind combat_declaration_kind) noexcept {
    switch (combat_declaration_kind) {
        case CombatDeclarationKind::Attacker: return "attacker";
        case CombatDeclarationKind::Blocker: return "blocker";
        case CombatDeclarationKind::Count: return "count";
    }
    return "unknown";
}


const char* to_string(DrawRecordOutcome draw_record_outcome) noexcept {
    switch (draw_record_outcome) {
        case DrawRecordOutcome::DrewCard: return "drew_card";
        case DrawRecordOutcome::EmptyLibrary: return "empty_library";
        case DrawRecordOutcome::Count: return "count";
    }
    return "unknown";
}

const char* to_string(DamagePreventionRecordKind damage_prevention_record_kind) noexcept {
    switch (damage_prevention_record_kind) {
        case DamagePreventionRecordKind::ShieldAdded: return "shield_added";
        case DamagePreventionRecordKind::ShieldConsumed: return "shield_consumed";
        case DamagePreventionRecordKind::ShieldExpired: return "shield_expired";
        case DamagePreventionRecordKind::ShieldAppliedToUnpreventableDamage: return "shield_applied_to_unpreventable_damage";
        case DamagePreventionRecordKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(LifeChangeKind life_change_kind) noexcept {
    switch (life_change_kind) {
        case LifeChangeKind::Loss: return "loss";
        case LifeChangeKind::Gain: return "gain";
        case LifeChangeKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(ManaChangeKind mana_change_kind) noexcept {
    switch (mana_change_kind) {
        case ManaChangeKind::Produced: return "produced";
        case ManaChangeKind::Paid: return "paid";
        case ManaChangeKind::Emptied: return "emptied";
        case ManaChangeKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(CounterChangeKind counter_change_kind) noexcept {
    switch (counter_change_kind) {
        case CounterChangeKind::ObjectAdded: return "object_added";
        case CounterChangeKind::ObjectRemoved: return "object_removed";
        case CounterChangeKind::PlayerAdded: return "player_added";
        case CounterChangeKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(DiscardRecordKind discard_record_kind) noexcept {
    switch (discard_record_kind) {
        case DiscardRecordKind::ExplicitChoice: return "explicit_choice";
        case DiscardRecordKind::CleanupHandSize: return "cleanup_hand_size";
        case DiscardRecordKind::CostPayment: return "cost_payment";
        case DiscardRecordKind::Count: return "count";
    }
    return "unknown";
}

const char* to_string(StaticEffectScope scope) noexcept {
    switch (scope) {
        case StaticEffectScope::None: return "none";
        case StaticEffectScope::Source: return "source";
        case StaticEffectScope::CreaturesYouControl: return "creatures_you_control";
        case StaticEffectScope::CreaturesOpponentsControl: return "creatures_opponents_control";
        case StaticEffectScope::AllCreatures: return "all_creatures";
        case StaticEffectScope::PermanentsYouControl: return "permanents_you_control";
        case StaticEffectScope::PermanentsOpponentsControl: return "permanents_opponents_control";
        case StaticEffectScope::AllPermanents: return "all_permanents";
        case StaticEffectScope::Count: return "count";
    }
    return "unknown";
}


const char* to_string(ContinuousEffectDuration duration) noexcept {
    switch (duration) {
        case ContinuousEffectDuration::None: return "none";
        case ContinuousEffectDuration::UntilCleanup: return "until_cleanup";
        case ContinuousEffectDuration::UntilEndOfGame: return "until_end_of_game";
        case ContinuousEffectDuration::Count: return "count";
    }
    return "unknown";
}

Phase phase_for_step(Step step) noexcept {
    switch (step) {
        case Step::Untap:
        case Step::Upkeep:
        case Step::Draw:
            return Phase::Beginning;
        case Step::Main1:
            return Phase::PrecombatMain;
        case Step::BeginningOfCombat:
        case Step::DeclareAttackers:
        case Step::DeclareBlockers:
        case Step::CombatDamage:
        case Step::EndOfCombat:
            return Phase::Combat;
        case Step::Main2:
            return Phase::PostcombatMain;
        case Step::End:
        case Step::Cleanup:
            return Phase::Ending;
    }
    return Phase::Beginning;
}

PlayerId expected_zone_container_player(const GameObject& obj, Zone zone_name) noexcept {
    if (zone_is_global(zone_name)) {
        return PlayerId{};
    }
    return zone_uses_controller_container(zone_name) ? obj.controller : obj.owner;
}

PlayerState& player(GameState& game, PlayerId id) {
    if (!id.valid() || id.value > game.players.size()) {
        throw std::out_of_range("invalid player id");
    }
    return game.players[id.value - 1];
}

const PlayerState& player(const GameState& game, PlayerId id) {
    if (!id.valid() || id.value > game.players.size()) {
        throw std::out_of_range("invalid player id");
    }
    return game.players[id.value - 1];
}

GameObject& object(GameState& game, ObjectId id) {
    if (!id.valid() || id.value > game.objects.size()) {
        throw std::out_of_range("invalid object id");
    }
    return game.objects[id.value - 1];
}

const GameObject& object(const GameState& game, ObjectId id) {
    if (!id.valid() || id.value > game.objects.size()) {
        throw std::out_of_range("invalid object id");
    }
    return game.objects[id.value - 1];
}

std::vector<ObjectId>& zone(GameState& game, PlayerId id, Zone zone_name) {
    return player(game, id).zones.at(zone_index(zone_name));
}

const std::vector<ObjectId>& zone(const GameState& game, PlayerId id, Zone zone_name) {
    return player(game, id).zones.at(zone_index(zone_name));
}

} // namespace mtgsim
