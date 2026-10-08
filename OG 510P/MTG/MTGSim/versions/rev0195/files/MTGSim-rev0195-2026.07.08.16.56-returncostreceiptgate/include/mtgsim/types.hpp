#pragma once

#include <array>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace mtgsim {

using u8 = std::uint8_t;
using u16 = std::uint16_t;
using u32 = std::uint32_t;
using u64 = std::uint64_t;

struct PlayerId {
    u32 value = 0;
    [[nodiscard]] constexpr bool valid() const noexcept { return value != 0; }
    friend constexpr bool operator==(PlayerId, PlayerId) = default;
};

struct ObjectId {
    u32 value = 0;
    [[nodiscard]] constexpr bool valid() const noexcept { return value != 0; }
    friend constexpr bool operator==(ObjectId, ObjectId) = default;
};

enum class Zone : u8 {
    Library,
    Hand,
    Battlefield,
    Graveyard,
    Stack,
    Exile,
    Command,
    Ante,
    Count
};

[[nodiscard]] constexpr bool zone_is_global(Zone zone_name) noexcept {
    return zone_name == Zone::Stack;
}

[[nodiscard]] constexpr bool zone_uses_controller_container(Zone zone_name) noexcept {
    return zone_name == Zone::Battlefield;
}



enum class ManaSymbol : u8 {
    White,
    Blue,
    Black,
    Red,
    Green,
    Colorless,
    Count
};

struct ManaPool {
    u32 white = 0;
    u32 blue = 0;
    u32 black = 0;
    u32 red = 0;
    u32 green = 0;
    u32 colorless = 0;

    [[nodiscard]] constexpr u32 total() const noexcept {
        return white + blue + black + red + green + colorless;
    }
    [[nodiscard]] constexpr bool empty() const noexcept { return total() == 0U; }
};

struct ManaCost {
    u32 generic = 0;
    u32 white = 0;
    u32 blue = 0;
    u32 black = 0;
    u32 red = 0;
    u32 green = 0;
    u32 colorless = 0;

    [[nodiscard]] constexpr u32 total_symbols() const noexcept {
        return generic + white + blue + black + red + green + colorless;
    }
    [[nodiscard]] constexpr bool free() const noexcept { return total_symbols() == 0U; }
};

enum CardColorMask : u32 {
    ColorNone  = 0,
    ColorWhite = 1u << 0,
    ColorBlue  = 1u << 1,
    ColorBlack = 1u << 2,
    ColorRed   = 1u << 3,
    ColorGreen = 1u << 4,
    ColorAll   = ColorWhite | ColorBlue | ColorBlack | ColorRed | ColorGreen
};

[[nodiscard]] constexpr bool has_color_mask(u32 colors, CardColorMask color) noexcept {
    return (colors & static_cast<u32>(color)) != 0U;
}

[[nodiscard]] constexpr bool color_masks_overlap(u32 a, u32 b) noexcept {
    return (a & b & static_cast<u32>(ColorAll)) != 0U;
}

enum class CounterKind : u8 {
    PlusOnePlusOne,
    MinusOneMinusOne,
    Loyalty,
    Defense,
    Charge,
    Poison,
    Count
};

enum KeywordAbilityMask : u32 {
    AbilityNone         = 0,
    AbilityFlying       = 1u << 0,
    AbilityReach        = 1u << 1,
    AbilityDeathtouch   = 1u << 2,
    AbilityLifelink     = 1u << 3,
    AbilityVigilance    = 1u << 4,
    AbilityFirstStrike  = 1u << 5,
    AbilityDoubleStrike = 1u << 6,
    AbilityTrample      = 1u << 7,
    AbilityIndestructible = 1u << 8,
    AbilityHaste        = 1u << 9,
    AbilityDefender     = 1u << 10,
    AbilityHexproof     = 1u << 11,
    AbilityShroud       = 1u << 12,
    AbilityMenace       = 1u << 13,
    AbilityFlash        = 1u << 14
};

[[nodiscard]] constexpr bool has_ability_mask(u32 abilities, KeywordAbilityMask ability) noexcept {
    return (abilities & static_cast<u32>(ability)) != 0U;
}

struct CounterSet {
    u32 plus_one_plus_one = 0;
    u32 minus_one_minus_one = 0;
    u32 loyalty = 0;
    u32 defense = 0;
    u32 charge = 0;

    [[nodiscard]] constexpr u32 total() const noexcept {
        return plus_one_plus_one + minus_one_minus_one + loyalty + defense + charge;
    }
    [[nodiscard]] constexpr bool empty() const noexcept { return total() == 0U; }
};

enum CardTypeMask : u32 {
    TypeNone         = 0,
    TypeArtifact     = 1u << 0,
    TypeBattle       = 1u << 1,
    TypeCreature     = 1u << 2,
    TypeEnchantment  = 1u << 3,
    TypeInstant      = 1u << 4,
    TypeKindred      = 1u << 5,
    TypeLand         = 1u << 6,
    TypePlaneswalker = 1u << 7,
    TypeSorcery      = 1u << 8
};

[[nodiscard]] constexpr bool has_type_mask(u32 types, CardTypeMask type) noexcept {
    return (types & static_cast<u32>(type)) != 0U;
}

[[nodiscard]] constexpr bool type_masks_overlap(u32 a, u32 b) noexcept {
    return (a & b) != 0U;
}

enum class Phase : u8 {
    Beginning,
    PrecombatMain,
    Combat,
    PostcombatMain,
    Ending
};

enum class Step : u8 {
    Untap,
    Upkeep,
    Draw,
    Main1,
    BeginningOfCombat,
    DeclareAttackers,
    DeclareBlockers,
    CombatDamage,
    EndOfCombat,
    Main2,
    End,
    Cleanup
};

enum class ActionKind : u8 {
    PassPriority,
    CastSpellFromHandPaid,
    PlayLand,
    ActivateTapManaAbility,
    ActivateManaAbility,
    ActivateActivatedAbility,
    ActivateLoyaltyAbility,
    DeclareAttacker,
    DeclareBlocker,
    OrderCombatDamage,
    PutPendingTriggersOnStack,
    Count
};

enum class ChoiceRequestKind : u8 {
    None,
    PriorityAction,
    PendingTriggersToStack,
    DeclareAttackers,
    DeclareBlockers,
    OrderCombatDamage,
    Count
};

enum class LegalActionValidationSource : u8 {
    // The selected action is not legal for the current choice surface.
    None,
    // The selected action matched an action actually listed in the offered frontier.
    OfferedAction,
    // The selected action was omitted from a bounded frontier but accepted by the
    // authoritative domain validator for that choice kind.
    DirectDomainValidation,
    Count
};

inline constexpr u32 kLegalActionSchemaVersion = 2U;
inline constexpr u32 kStateCoreSchemaVersion = 1U;
inline constexpr u32 kStateCheckpointSealSchemaVersion = 2U;
inline constexpr u32 kChoiceRequestSchemaVersion = 2U;
inline constexpr u32 kChoiceRequestQueueSchemaVersion = 1U;
inline constexpr u32 kLegalActionPageSchemaVersion = 3U;
inline constexpr u32 kChoiceQueueLocationSchemaVersion = 1U;
inline constexpr u32 kReplayArtifactManifestSchemaVersion = 3U;
inline constexpr u32 kActionReceiptRecordSchemaVersion = 1U;
inline constexpr u32 kPaidActionDeclarationRecordSchemaVersion = 7U;
inline constexpr u32 kPaidActionTransactionRecordSchemaVersion = 11U;
inline constexpr u32 kPaidActionTransactionJournalSchemaVersion = 9U;
inline constexpr u32 kActionTraceEntrySchemaVersion = 1U;
inline constexpr u32 kTransitionPreflightSealSchemaVersion = 1U;
inline constexpr u32 kTransitionBoundarySealSchemaVersion = 1U;
inline constexpr u32 kTransitionTraceHandoffSealSchemaVersion = 1U;

enum class TargetKind : u8 {
    None,
    Player,
    Object
};

enum TargetMask : u32 {
    TargetNone        = 0,
    TargetPlayer      = 1u << 0,
    TargetObject      = 1u << 1,
    TargetStackObject = 1u << 2,
    TargetAny         = TargetPlayer | TargetObject
};

enum class AttachmentKind : u8 {
    None,
    Aura,
    Equipment,
    Fortification,
    Count
};

enum class EffectKind : u8 {
    None,
    DealDamage,
    DrawCards,
    GainLife,
    AddCounters,
    DestroyPermanent,
    RegeneratePermanent,
    ExilePermanent,
    CreateToken,
    GainControlPermanent,
    CreateContinuousEffect,
    BecomeCopyPermanent,
    CounterSpell,
    Count
};

enum class TriggerEventKind : u8 {
    None,
    CreatureEntersBattlefield,
    CreatureDies,
    Count
};

struct TriggerDefinition {
    TriggerEventKind event = TriggerEventKind::None;
    EffectKind effect_kind = EffectKind::None;
    u32 effect_amount = 0;
    CounterKind effect_counter_kind = CounterKind::PlusOnePlusOne;
    u32 target_mask = TargetNone;
    u32 target_count = 0;
    u32 created_token_definition_index = 0;
    bool exclude_source = true;

    [[nodiscard]] constexpr bool active() const noexcept {
        return event != TriggerEventKind::None && effect_kind != EffectKind::None;
    }
};

struct TargetRef {
    TargetKind kind = TargetKind::None;
    PlayerId player{};
    ObjectId object{};
    // For object targets chosen for spells/abilities, this records the
    // target object's zone-change index at choice time. A zero value is a
    // wildcard for legacy/transient refs such as UI selections, attachment
    // lookups, combat helpers, and direct API probes.
    u64 object_zone_change_index = 0;

    [[nodiscard]] constexpr bool valid() const noexcept { return kind != TargetKind::None; }
    friend constexpr bool operator==(TargetRef a, TargetRef b) noexcept {
        if (a.kind != b.kind) {
            return false;
        }
        switch (a.kind) {
            case TargetKind::Player:
                return a.player == b.player;
            case TargetKind::Object:
                if (a.object != b.object) {
                    return false;
                }
                return a.object_zone_change_index == 0U || b.object_zone_change_index == 0U ||
                       a.object_zone_change_index == b.object_zone_change_index;
            case TargetKind::None:
                return true;
        }
        return false;
    }
};

struct LoyaltyAbilityDefinition {
    std::int32_t cost = 0;
    EffectKind effect_kind = EffectKind::None;
    u32 effect_amount = 0;
    CounterKind effect_counter_kind = CounterKind::PlusOnePlusOne;
    u32 target_mask = TargetNone;
    u32 target_count = 0;
    u32 created_token_definition_index = 0;

    [[nodiscard]] constexpr bool active() const noexcept {
        return effect_kind != EffectKind::None;
    }
};

struct SpellModeDefinition {
    std::string name;
    EffectKind effect_kind = EffectKind::None;
    u32 effect_amount = 0;
    CounterKind effect_counter_kind = CounterKind::PlusOnePlusOne;
    u32 target_mask = TargetNone;
    u32 target_count = 0;
    u32 created_token_definition_index = 0;

    [[nodiscard]] bool active() const noexcept {
        return effect_kind != EffectKind::None;
    }
};

struct ManaAbilityDefinition {
    std::string name;
    bool tap_cost = false;
    ManaPool produces{};

    [[nodiscard]] bool active() const noexcept {
        return !produces.empty();
    }
};

struct SacrificeCostDefinition {
    u32 count = 0;
    u32 required_type_mask = TypeNone;

    [[nodiscard]] constexpr bool active() const noexcept {
        return count != 0U && required_type_mask != TypeNone;
    }
};

struct SacrificeCostPaymentRecord {
    // Typed nonmana cost-payment receipt for CR 601/602 cost payment. The
    // record preserves the exact ordered sacrifice selection, each selected
    // object's zone-change snapshot before payment, the resulting zone-change
    // range, and the summary pay_sacrifice_cost event sequence. This makes
    // sacrifice costs challengeable without scraping prose logs or inferring
    // selected objects only from the broad paid-action zone-change span.
    u64 sequence = 0;
    PlayerId payer{};
    ObjectId source_object{};
    SacrificeCostDefinition cost{};
    std::vector<ObjectId> selected_objects{};
    std::vector<u64> selected_zone_change_indices_before{};
    u32 first_zone_change_record_index = 0;
    u32 zone_change_record_count = 0;
    u64 payment_hash = 0;
};

struct DiscardCostDefinition {
    u32 count = 0;

    [[nodiscard]] constexpr bool active() const noexcept {
        return count != 0U;
    }
};

struct LifeCostDefinition {
    u32 amount = 0;

    [[nodiscard]] constexpr bool active() const noexcept {
        return amount != 0U;
    }
};

struct ReturnCostDefinition {
    u32 count = 0;
    u32 required_type_mask = TypeNone;
    bool require_tapped = false;

    [[nodiscard]] constexpr bool active() const noexcept {
        return count != 0U && required_type_mask != TypeNone;
    }
};

struct DiscardCostPaymentRecord {
    // Typed nonmana cost-payment receipt for discard-as-cost. The selected
    // hand cards, their pre-payment zone-change snapshots, the exact
    // DiscardRecord range, the hand->graveyard ZoneChangeRecord range, and the
    // summary pay_discard_cost event sequence are sealed together so 601/602
    // payment audits do not infer discard costs from generic discard logs.
    u64 sequence = 0;
    PlayerId payer{};
    ObjectId source_object{};
    DiscardCostDefinition cost{};
    std::vector<ObjectId> selected_cards{};
    std::vector<u64> selected_zone_change_indices_before{};
    u32 first_discard_record_index = 0;
    u32 discard_record_count = 0;
    u32 first_zone_change_record_index = 0;
    u32 zone_change_record_count = 0;
    u64 payment_hash = 0;
};

struct LifeCostPaymentRecord {
    // Typed nonmana cost-payment receipt for pay-life costs. Life payment is
    // not damage, so the receipt links the cost declaration to the exact
    // LifeChangeRecord loss row and seals before/after life totals without
    // forcing auditors to infer cost payment from a generic lose_life event.
    u64 sequence = 0;
    PlayerId payer{};
    ObjectId source_object{};
    LifeCostDefinition cost{};
    std::int32_t life_before = 0;
    std::int32_t life_after = 0;
    u32 life_change_record_index = 0;
    u64 payment_hash = 0;
};

struct ReturnCostPaymentRecord {
    // Typed nonmana cost-payment receipt for return-to-hand costs such as the
    // modern web-slinging-style seam. The record seals the exact selected
    // battlefield permanent(s), their pre-payment zone snapshots, the
    // resulting battlefield->hand ZoneChangeRecord range, and the summary
    // payment event so returned objects are not inferred from generic movement.
    u64 sequence = 0;
    PlayerId payer{};
    ObjectId source_object{};
    ReturnCostDefinition cost{};
    std::vector<ObjectId> selected_objects{};
    std::vector<u64> selected_zone_change_indices_before{};
    u32 first_zone_change_record_index = 0;
    u32 zone_change_record_count = 0;
    u64 payment_hash = 0;
};


struct LoyaltyCostPaymentRecord {
    // Typed nonmana cost-payment receipt for loyalty abilities. The generic
    // counter-change row remains the low-level mutation witness, while this
    // receipt seals the activated permanent, signed loyalty symbol cost,
    // before/after loyalty totals, and the exact CounterChangeRecord that paid
    // the cost. This keeps CR 606 payment evidence from being inferred from any
    // loyalty counter change that merely happened during the paid-action span.
    u64 sequence = 0;
    PlayerId payer{};
    ObjectId source_object{};
    u64 source_zone_change_index_before = 0;
    std::int32_t cost_delta = 0;
    u32 loyalty_before = 0;
    u32 loyalty_after = 0;
    u32 counter_change_record_index = 0;
    u64 payment_hash = 0;
};

struct TapCostPaymentRecord {
    // Typed nonmana cost-payment receipt for tap-as-cost in CR 601/602 paid
    // actions. The row seals the source snapshot, the exact tap EventRecord
    // witness, and before/after tapped state so an activated ability's tap
    // cost is not inferred from a plain log row or from final object state.
    u64 sequence = 0;
    PlayerId payer{};
    ObjectId source_object{};
    u64 source_zone_change_index_before = 0;
    bool tapped_before = false;
    bool tapped_after = false;
    u64 tap_event_sequence = 0;
    u64 payment_hash = 0;
};

struct ActivatedAbilityDefinition {
    std::string name;
    ManaCost mana_cost{};
    SacrificeCostDefinition sacrifice_cost{};
    DiscardCostDefinition discard_cost{};
    LifeCostDefinition life_cost{};
    ReturnCostDefinition return_cost{};
    bool tap_cost = false;
    bool sorcery_speed = false;
    EffectKind effect_kind = EffectKind::None;
    u32 effect_amount = 0;
    CounterKind effect_counter_kind = CounterKind::PlusOnePlusOne;
    u32 target_mask = TargetNone;
    u32 target_count = 0;
    u32 created_token_definition_index = 0;

    [[nodiscard]] bool active() const noexcept {
        return effect_kind != EffectKind::None;
    }
};

enum class StaticEffectScope : u8 {
    None,
    Source,
    CreaturesYouControl,
    CreaturesOpponentsControl,
    AllCreatures,
    PermanentsYouControl,
    PermanentsOpponentsControl,
    AllPermanents,
    Count
};

enum class ContinuousEffectDuration : u8 {
    None,
    UntilCleanup,
    UntilEndOfGame,
    Count
};

struct StaticEffectDefinition {
    std::string name;
    std::vector<std::string> depends_on_effect_names{};
    StaticEffectScope scope = StaticEffectScope::None;
    u32 affected_type_mask = TypeCreature;
    u32 added_type_mask = TypeNone;
    u32 removed_type_mask = TypeNone;
    bool sets_color = false;
    u32 set_color_mask = ColorNone;
    u32 added_color_mask = ColorNone;
    u32 removed_color_mask = ColorNone;
    bool sets_power_toughness = false;
    std::int32_t set_power = 0;
    std::int32_t set_toughness = 0;
    std::int32_t power_modifier = 0;
    std::int32_t toughness_modifier = 0;
    u32 granted_ability_mask = AbilityNone;
    u32 removed_ability_mask = AbilityNone;

    [[nodiscard]] bool active() const noexcept {
        return scope != StaticEffectScope::None &&
               (sets_power_toughness || power_modifier != 0 || toughness_modifier != 0 ||
                granted_ability_mask != AbilityNone || removed_ability_mask != AbilityNone ||
                added_type_mask != TypeNone || removed_type_mask != TypeNone || sets_color ||
                added_color_mask != ColorNone || removed_color_mask != ColorNone);
    }
};


enum class ReplacementPriorityTier : u8 {
    SelfReplacement,
    ControlEntering,
    CopyEntering,
    BackFaceEntering,
    General,
    Count
};

struct ZoneChangeReplacementDefinition {
    std::string name;
    StaticEffectScope scope = StaticEffectScope::None;
    Zone from_zone = Zone::Battlefield;
    Zone to_zone = Zone::Graveyard;
    Zone replacement_zone = Zone::Exile;
    u32 affected_type_mask = TypeCreature;
    // Deterministic scaffold for CR 616.1a-e. Lower enum ordinals are earlier
    // required-choice tiers; choice_rank is used only within the eligible tier.
    ReplacementPriorityTier priority_tier = ReplacementPriorityTier::General;
    u32 choice_rank = 0;

    [[nodiscard]] bool active() const noexcept {
        return scope != StaticEffectScope::None && from_zone != replacement_zone && to_zone != replacement_zone;
    }
};

struct CardDefinition {
    std::string name;
    u32 type_mask = TypeNone;
    std::int32_t printed_power = 0;
    std::int32_t printed_toughness = 0;
    std::int32_t printed_loyalty = 0;
    std::int32_t printed_defense = 0;
    ManaCost mana_cost{};
    bool taps_for_mana = false;
    ManaSymbol tap_mana_symbol = ManaSymbol::Colorless;
    std::vector<ManaAbilityDefinition> mana_abilities{};
    EffectKind effect_kind = EffectKind::None;
    u32 effect_amount = 0;
    CounterKind effect_counter_kind = CounterKind::PlusOnePlusOne;
    u32 target_mask = TargetNone;
    u32 target_count = 0;
    u32 created_token_definition_index = 0;
    TriggerDefinition trigger{};
    u32 color_mask = ColorNone;
    u32 protection_color_mask = ColorNone;
    u32 ability_mask = AbilityNone;
    bool attacks_each_combat_if_able = false;
    bool blocks_each_combat_if_able = false;
    // Narrow attacker-side block requirement: the attacking creature must be
    // blocked if a legal declaration can satisfy that requirement. This is a
    // requirement input to the blocker maximizer, not an automatic block.
    bool must_be_blocked_if_able = false;
    // Lure-style blocker assignment requirement: each able blocker controlled
    // by the defending player must block this attacker if doing so can be part
    // of a legal declaration. The blocker maximizer treats each able
    // blocker-attacker pair as one requirement.
    bool all_able_blockers_block_this_if_able = false;
    // Narrow per-creature declaration restrictions used by the combat
    // requirement maximizer. They intentionally model only the "alone" family
    // and not yet arbitrary costs or defender-specific restrictions.
    bool cant_attack_alone = false;
    bool cant_block_alone = false;
    // Narrow blocker-side restriction: this blocker can block only attackers
    // with flying. This lets the requirement maximizer distinguish a must-block
    // creature that is able against a flyer from one unable against a ground
    // attacker.
    bool can_block_only_flying = false;
    // Zero means no restriction. Nonzero battlefield sources impose a global
    // “no more than N creatures attack/block each combat” declaration cap.
    u32 max_attackers_each_combat = 0;
    u32 max_blockers_each_combat = 0;
    // Zero means no per-attacker cap. Nonzero attackers impose “this
    // attacking creature can't be blocked by more than N creatures.”
    u32 max_blockers_to_block_this = 0;
    // Narrow mana-only declaration costs. They model the CR attack/block cost
    // lock-and-pay seam without yet modeling arbitrary tap/sacrifice/discard
    // attack costs or alternate cost-choosing prompts.
    ManaCost attack_cost{};
    ManaCost block_cost{};
    AttachmentKind attachment_kind = AttachmentKind::None;
    std::int32_t attachment_power_bonus = 0;
    std::int32_t attachment_toughness_bonus = 0;
    u32 attachment_granted_ability_mask = AbilityNone;
    LoyaltyAbilityDefinition loyalty_ability{};
    std::vector<SpellModeDefinition> modes{};
    std::vector<ActivatedAbilityDefinition> activated_abilities{};
    std::vector<StaticEffectDefinition> static_effects{};
    std::vector<ZoneChangeReplacementDefinition> zone_change_replacements{};
    SacrificeCostDefinition sacrifice_cost{};
    DiscardCostDefinition discard_cost{};
    LifeCostDefinition life_cost{};
    ReturnCostDefinition return_cost{};
    StaticEffectDefinition continuous_effect{};
    ContinuousEffectDuration continuous_effect_duration = ContinuousEffectDuration::UntilCleanup;

    [[nodiscard]] bool has_ability(KeywordAbilityMask ability) const noexcept {
        return has_ability_mask(ability_mask, ability);
    }

    [[nodiscard]] bool is_modal() const noexcept {
        return !modes.empty();
    }

    [[nodiscard]] bool requires_target() const noexcept {
        if (is_modal()) {
            return false;
        }
        return target_mask != TargetNone &&
               (target_count != 0U || effect_kind != EffectKind::None || attachment_kind == AttachmentKind::Aura);
    }

    [[nodiscard]] bool is_permanent() const noexcept {
        constexpr u32 permanent_types = TypeArtifact | TypeBattle | TypeCreature |
            TypeEnchantment | TypeLand | TypePlaneswalker;
        return (type_mask & permanent_types) != 0;
    }
};

struct GameObject {
    ObjectId id{};
    u32 definition_index = 0;
    bool has_copy_effect = false;
    u32 copied_definition_index = 0;
    PlayerId owner{};
    PlayerId controller{};
    Zone zone = Zone::Library;
    bool tapped = false;
    bool token = false;
    bool ceased_to_exist = false;
    std::int32_t power = 0;
    std::int32_t toughness = 0;
    u32 damage_marked = 0;
    bool deathtouch_damage_marked = false;
    CounterSet counters{};
    std::vector<TargetRef> targets;
    u32 chosen_mode_index = 0;
    bool ability_object = false;
    u32 regeneration_shields = 0;
    TargetRef attached_to{};
    bool attacking = false;
    bool blocked = false;
    PlayerId defending_player{};
    ObjectId attacked_object{};
    ObjectId blocking{};
    // Active-player chosen damage assignment order for blockers of this
    // attacking creature. Empty means no explicit order has been chosen yet;
    // combat damage falls back to current blocker order only for legacy/direct
    // API calls that bypass the public choice gate.
    std::vector<ObjectId> combat_damage_ordered_blockers{};
    PlayerId battle_protector{};
    u32 controlled_since_turn_start_index = 0;
    u32 loyalty_ability_activated_turn = 0;
    u64 zone_change_index = 0;
    u64 layer_timestamp = 0;
};

struct PlayerState {
    PlayerId id{};
    std::string name;
    std::int32_t life = 20;
    u32 poison = 0;
    u32 max_hand_size = 7;
    u32 max_land_plays_per_turn = 1;
    u32 lands_played_this_turn = 0;
    ManaPool mana_pool{};
    bool lost = false;
    u32 empty_library_draw_attempts = 0;
    u32 mulligans_taken = 0;
    u32 turn_start_index = 0;
    std::array<std::vector<ObjectId>, static_cast<std::size_t>(Zone::Count)> zones{};
};

struct Event {
    u64 sequence = 0;
    std::string kind;
    std::string detail;
};

enum class EventRecordKind : u8 {
    Log,
    ZoneChange,
    ZoneReplacement,
    Damage,
    DamagePrevention,
    LifeChange,
    ManaChange,
    CounterChange,
    Discard,
    TriggerQueued,
    TriggerPutOnStack,
    TriggerDropped,
    StackPlacement,
    StackResolution,
    PriorityTransition,
    StateBasedAction,
    CombatDeclaration,
    CombatDamageAssignment,
    PaidActionDeclaration,
    PaidActionTransaction,
    ManaPaymentPlan,
    Draw,
    Mulligan,
    MulliganKeep,
    Count
};

enum class StackPlacementKind : u8 {
    SpellCast,
    ActivatedAbility,
    LoyaltyAbility,
    Count
};

enum class PaidActionTransactionOutcome : u8 {
    Committed,
    RolledBack,
    Count
};

enum class PriorityTransitionOutcome : u8 {
    PriorityAdvanced,
    StackResolved,
    StepAdvanced,
    PendingTriggersPutOnStack,
    NoAlivePlayers,
    Count
};

enum class StackResolutionOutcome : u8 {
    Resolved,
    NoLegalTargets,
    InvalidMode,
    AuraAttachFailed,
    Count
};

enum class TargetLegalityFailureKind : u8 {
    None,
    EmptyTarget,
    TargetKindNotAllowed,
    PlayerMissingOrLost,
    ObjectMissing,
    ObjectZoneNotAllowed,
    ObjectZoneChangeMismatch,
    Shroud,
    Hexproof,
    Protection,
    Count
};

enum class StateBasedActionKind : u8 {
    PlayerLost,
    CounterPairCancel,
    CreatureToughnessGraveyard,
    CreatureDamageDestroy,
    PlaneswalkerLoyaltyGraveyard,
    BattleDefenseGraveyard,
    AttachmentUnattach,
    AuraGraveyard,
    TokenCease,
    Count
};

enum class CombatDeclarationKind : u8 {
    Attacker,
    Blocker,
    Count
};

enum class DrawRecordOutcome : u8 {
    DrewCard,
    EmptyLibrary,
    Count
};

struct EventRecord {
    // Typed event spine that is kept one-to-one with the human-readable
    // Event log. Plain log rows use kind=Log; rule-seam rows link directly
    // to their structured payload records so replay/agent consumers can walk
    // a single ordered stream without parsing Event::detail. Tap log rows
    // additionally preserve object/player/zone-change anchors until a full
    // typed tap/untap record family lands.
    // Audit phrase: tap EventRecord object/player/zone-change anchors.
    u64 sequence = 0;
    EventRecordKind kind = EventRecordKind::Log;
    std::string log_kind;
    ObjectId object{};
    u64 object_zone_change_index = 0;
    PlayerId player{};
    TargetRef target{};
    // rev0153 choice payload anchors; rev0154 seals them into journal_hash.
    // rev0155 extends target choices with an ordered target-set hash so multi-target choices are not merely counted.
    // rev0156 extends mode choices with a selected-mode contract hash so mode anchors prove more than an ordinal.
    u32 choice_mode_index = 0;
    u64 choice_mode_contract_hash = 0;
    u32 choice_target_count = 0;
    u64 choice_target_set_hash = 0;
    u32 zone_change_record_index = 0;
    u32 zone_replacement_record_index = 0;
    u32 damage_record_index = 0;
    u32 damage_prevention_record_index = 0;
    u32 life_change_record_index = 0;
    u32 mana_change_record_index = 0;
    u32 counter_change_record_index = 0;
    u32 discard_record_index = 0;
    u32 trigger_record_index = 0;
    u32 stack_placement_record_index = 0;
    u32 stack_resolution_record_index = 0;
    u32 priority_transition_record_index = 0;
    u32 state_based_action_record_index = 0;
    u32 combat_declaration_record_index = 0;
    u32 combat_damage_assignment_record_index = 0;
    u32 mana_payment_plan_record_index = 0;
    u32 draw_record_index = 0;
    u32 mulligan_record_index = 0;
    u32 mulligan_keep_record_index = 0;
    u32 paid_action_declaration_record_index = 0;
    u32 paid_action_transaction_record_index = 0;
};


struct StackPlacementRecord {
    // Structured twin for putting a spell or activated/loyalty ability onto
    // the stack. It preserves the source/stack identity, chosen mode/targets,
    // paid-cost flags, and priority handoff so action consumers can audit CR
    // 601/602/117 behavior without inferring it from log strings.
    u64 sequence = 0;
    StackPlacementKind kind = StackPlacementKind::Count;
    ObjectId source_object{};
    ObjectId stack_object{};
    PlayerId controller{};
    Zone source_zone_before = Zone::Library;
    u64 source_zone_change_index_before = 0;
    u64 stack_zone_change_index = 0;
    u32 stack_enter_zone_change_record_index = 0;
    u32 ability_index = 0;
    std::int32_t loyalty_cost_delta = 0;
    u32 chosen_mode_index = 0;
    u32 target_mask = TargetNone;
    u32 target_count = 0;
    std::vector<TargetRef> chosen_targets{};
    u32 stack_size_before = 0;
    u32 stack_size_after = 0;
    PlayerId priority_before{};
    PlayerId priority_after{};
    bool physical_card = false;
    bool ability_object = false;
    bool modal_choice = false;
    bool target_choice = false;
    bool mana_cost_required = false;
    bool mana_cost_paid = false;
    bool tap_cost_required = false;
    bool tap_cost_paid = false;
    bool sacrifice_cost_required = false;
    bool sacrifice_cost_paid = false;
    bool discard_cost_required = false;
    bool discard_cost_paid = false;
    bool loyalty_cost_paid = false;
    // rev0149 paid-action phase evidence. These fields turn the CR 601/602
    // ordering seam into typed stack-placement metadata: the chosen
    // mode/targets are locked, then payments mutate the journal, then the
    // final placement row is emitted. Ranges are one-based indexes into the
    // corresponding journal vectors and cover only events/records after the
    // lock point and before this StackPlacementRecord's own EventRecord.
    bool paid_action_phase_recorded = false;
    bool stack_object_on_stack_before_costs = false;
    bool choices_locked_before_costs = false;
    bool paid_action_events_before_stack_placement = false;
    u64 stack_object_entered_sequence = 0;
    u64 choices_locked_sequence = 0;
    u64 first_paid_action_event_sequence = 0;
    u64 last_paid_action_event_sequence = 0;
    u32 first_mana_payment_plan_record_index = 0;
    u32 mana_payment_plan_record_count = 0;
    u32 first_mana_change_record_index = 0;
    u32 mana_change_record_count = 0;
    u32 first_paid_action_counter_change_record_index = 0;
    u32 paid_action_counter_change_record_count = 0;
    u32 first_paid_action_zone_change_record_index = 0;
    u32 paid_action_zone_change_record_count = 0;
    // rev0152 makes the choice-lock seam explicit. Mode/target selections are
    // still stored as chosen_mode_index/chosen_targets, but these event
    // witnesses prove where the choice rows sit between stack entry and cost
    // payment. They are EventRecord sequences, not vector indexes.
    u64 first_choice_event_sequence = 0;
    u64 last_choice_event_sequence = 0;
    u32 choice_event_count = 0;
    // rev0153 splits the generic choice span into named payload anchors.
    // Mode and target choices can now be challenged independently, and the
    // linked EventRecord rows carry the chosen mode index / target count.
    // rev0154 seals both anchor sequences into journal_hash.
    u64 mode_choice_event_sequence = 0;
    u64 target_choice_event_sequence = 0;
    // rev0151 narrows sacrifice costs from a generic paid-action zone span to
    // a named cost witness range plus the summary payment event. These are
    // one-based ZoneChangeRecord indexes and an EventRecord sequence, all
    // inside the paid-action window.
    u32 first_sacrifice_cost_zone_change_record_index = 0;
    u32 sacrifice_cost_zone_change_record_count = 0;
    u64 sacrifice_cost_event_sequence = 0;
    // rev0171 links the exact SacrificeCostPaymentRecord receipt(s) to this
    // paid-action phase. Today there is one payment record per sacrifice cost,
    // but this is a range so future composite nonmana costs do not need another
    // schema break. The hash is the stable hash of the first receipt in the
    // range for the common one-record case and must be nonzero when paid.
    u32 first_sacrifice_cost_payment_record_index = 0;
    u32 sacrifice_cost_payment_record_count = 0;
    u64 sacrifice_cost_payment_hash = 0;
    // rev0191 brings discard-as-cost into the same typed paid-action spine.
    // The discard-record range names the semantic DiscardRecord rows, while
    // the zone-change range anchors the physical hand->graveyard movement and
    // the payment-record range carries the sealed selection/hash receipt.
    u32 first_discard_cost_record_index = 0;
    u32 discard_cost_record_count = 0;
    u32 first_discard_cost_zone_change_record_index = 0;
    u32 discard_cost_zone_change_record_count = 0;
    u64 discard_cost_event_sequence = 0;
    u32 first_discard_cost_payment_record_index = 0;
    u32 discard_cost_payment_record_count = 0;
    u64 discard_cost_payment_hash = 0;
    // rev0192 adds a first-class tap-as-cost receipt range, retaining the
    // existing event witness as the low-level tap row but no longer making
    // auditors infer the cost payment from that row alone.
    u32 first_tap_cost_payment_record_index = 0;
    u32 tap_cost_payment_record_count = 0;
    u64 tap_cost_payment_hash = 0;
    u64 tap_cost_event_sequence = 0;
    // rev0193 adds pay-life cost receipts. The life-change row remains the
    // low-level event, while this range/hash proves it was paid as a locked
    // cost for this action rather than as damage or effect text.
    bool life_cost_required = false;
    bool life_cost_paid = false;
    u32 first_life_cost_payment_record_index = 0;
    u32 life_cost_payment_record_count = 0;
    u64 life_cost_payment_hash = 0;
    u32 first_life_cost_life_change_record_index = 0;
    u32 life_cost_life_change_record_count = 0;
    u64 life_cost_event_sequence = 0;
    // rev0195 adds return-to-hand cost receipts for nonmana costs that move
    // chosen battlefield objects back to hand, keeping them distinct from
    // effect-driven bounce or ordinary zone movement.
    bool return_cost_required = false;
    bool return_cost_paid = false;
    u32 first_return_cost_zone_change_record_index = 0;
    u32 return_cost_zone_change_record_count = 0;
    u64 return_cost_event_sequence = 0;
    u32 first_return_cost_payment_record_index = 0;
    u32 return_cost_payment_record_count = 0;
    u64 return_cost_payment_hash = 0;
    // rev0194 adds a first-class loyalty-cost receipt range. rev0195 adds a first-class return-to-hand cost receipt range. The generic paid
    // counter-change span remains useful for ordering, but this range/hash proves
    // that the loyalty counter mutation specifically paid the locked loyalty cost.
    u32 first_loyalty_cost_payment_record_index = 0;
    u32 loyalty_cost_payment_record_count = 0;
    u64 loyalty_cost_payment_hash = 0;
    u64 loyalty_cost_event_sequence = 0;
    // rev0158 paid spell declaration evidence: a single typed declaration/cost-lock
    // record sits after stack entry and choices, before payment, then links back
    // here after the stack placement row is sealed. The hash excludes the
    // circular stack_placement_record_index backlink.
    u32 paid_action_declaration_record_index = 0;
    u64 paid_action_declaration_hash = 0;
};

struct TargetResolutionCheckRecord {
    // Per-target CR 608.2b resolution receipt. The engine evaluates target
    // legality once as resolution begins, stores the precise ordered result
    // here, and feeds only the legal targets to the effect payload. This keeps
    // partial-resolution behavior challengeable without re-running mutable
    // target predicates after effects begin to apply.
    u32 target_index = 0;
    TargetRef target{};
    PlayerId source_controller{};
    bool legal_on_resolution = false;
    TargetLegalityFailureKind failure_kind = TargetLegalityFailureKind::None;
    Zone object_zone_on_resolution = Zone::Count;
    u64 object_zone_change_index_on_resolution = 0;
};

struct StackResolutionRecord {
    // Structured twin for stack resolution. It captures the late target-
    // legality check, effect payload, and final stack-object movement so CR
    // 608-style resolution behavior is auditable without scraping log text.
    u64 sequence = 0;
    ObjectId stack_object{};
    PlayerId controller{};
    bool ability_object = false;
    bool permanent_spell = false;
    bool aura_spell = false;
    bool modal_spell = false;
    u32 chosen_mode_index = 0;
    EffectKind effect_kind = EffectKind::None;
    u32 effect_amount = 0;
    CounterKind effect_counter_kind = CounterKind::PlusOnePlusOne;
    u32 target_mask = TargetNone;
    u32 target_count = 0;
    std::vector<TargetRef> chosen_targets{};
    std::vector<TargetResolutionCheckRecord> target_resolution_checks{};
    // rev0188 links resolved triggered ability stack objects back to the
    // TriggerRecord that created them. Activated/loyalty ability objects keep
    // this field at zero.
    u32 trigger_record_index = 0;
    u32 required_target_count = 0;
    u32 legal_target_count = 0;
    bool missing_required_targets = false;
    bool all_targets_illegal = false;
    bool required_target_failed = false;
    bool modal_choice_invalid = false;
    bool effect_payload_applied = false;
    StackResolutionOutcome outcome = StackResolutionOutcome::Resolved;
    u64 stack_zone_change_index = 0;
    u32 stack_leave_zone_change_record_index = 0;
    bool stack_object_left_stack = false;
    Zone final_zone = Zone::Stack;
};

struct PriorityTransitionRecord {
    // Structured twin for pass-priority windows. It records the pass count,
    // pending-trigger gate, stack/step outcome, and before/after priority so
    // response-window behavior can be audited without scraping pass_priority logs.
    u64 sequence = 0;
    PriorityTransitionOutcome outcome = PriorityTransitionOutcome::Count;
    PlayerId player{};
    PlayerId active_player{};
    PlayerId priority_before{};
    PlayerId priority_after{};
    Step step_before = Step::Untap;
    Step step_after = Step::Untap;
    u32 stack_size_before = 0;
    u32 stack_size_after = 0;
    ObjectId stack_top_before{};
    ObjectId stack_top_after{};
    u32 consecutive_passes_before = 0;
    u32 consecutive_passes_after_pass = 0;
    u32 consecutive_passes_after = 0;
    u32 alive_players = 0;
    u32 pending_triggers_before = 0;
    u32 pending_triggers_after = 0;
    u32 stack_resolution_record_index = 0;
    u32 trigger_stack_record_count_before = 0;
    u32 trigger_stack_record_count_after = 0;
    bool pass_count_incremented = false;
    bool priority_changed = false;
    bool stack_resolved = false;
    bool step_advanced = false;
    bool pending_triggers_put_on_stack = false;
};


struct StateBasedActionRecord {
    // Structured twin for state-based actions. It snapshots the condition that
    // caused the SBA and links to any resulting zone movement so consumers can
    // audit automatic cleanup/destruction without parsing string logs.
    u64 sequence = 0;
    u32 check_index = 0;
    u32 pass_index = 0;
    u32 pass_candidate_count = 0;
    StateBasedActionKind kind = StateBasedActionKind::Count;
    ObjectId object{};
    PlayerId player{};
    Zone object_zone = Zone::Library;
    u64 object_zone_change_index = 0;
    std::int32_t effective_power = 0;
    std::int32_t effective_toughness = 0;
    u32 damage_marked = 0;
    bool deathtouch_damage_marked = false;
    u32 plus_one_plus_one_counters = 0;
    u32 minus_one_minus_one_counters = 0;
    u32 loyalty_counters = 0;
    u32 defense_counters = 0;
    u32 regeneration_shields_before = 0;
    u32 regeneration_shields_after = 0;
    bool regeneration_applied = false;
    bool indestructible = false;
    bool object_left_battlefield = false;
    bool attachment_detached = false;
    bool token_ceased = false;
    u32 zone_change_record_index = 0;
};

struct ZoneChangeRecord {
    // Structured twin for the string `move_object` event. It records the
    // requested movement and the finalized movement after replacement effects,
    // preserving enough pre-change identity for future LKI/event consumers.
    u64 sequence = 0;
    ObjectId object{};
    PlayerId owner{};
    PlayerId previous_controller{};
    PlayerId new_controller{};
    Zone from_zone = Zone::Library;
    Zone requested_zone = Zone::Library;
    Zone to_zone = Zone::Library;
    u64 from_zone_change_index = 0;
    u64 to_zone_change_index = 0;
    u32 first_replacement_record_index = 0;
    u32 replacement_record_count = 0;
    u32 first_counter_change_record_index = 0;
    u32 counter_change_record_count = 0;
    u32 first_damage_prevention_record_index = 0;
    u32 damage_prevention_record_count = 0;
    bool replacement_applied = false;
    bool was_token = false;
    bool was_ability_object = false;
    bool was_battlefield_creature = false;
    bool creature_died = false;
};

struct ZoneChangeReplacementRecord {
    // Structured twin for each applied zone-change replacement effect. It
    // captures the affected-player fallback choice, the source LKI, the current
    // event being rewritten, and the final ZoneChangeRecord it fed.
    u64 sequence = 0;
    ObjectId object{};
    PlayerId affected_player{};
    PlayerId controller{};
    ObjectId source{};
    std::string name;
    Zone from_zone = Zone::Library;
    Zone event_to_zone = Zone::Library;
    Zone replacement_zone = Zone::Library;
    u32 definition_index = 0;
    ReplacementPriorityTier priority_tier = ReplacementPriorityTier::General;
    ReplacementPriorityTier candidate_min_priority_tier = ReplacementPriorityTier::General;
    u32 choice_rank = 0;
    u32 candidate_count = 0;
    u32 eligible_candidate_count = 0;
    u32 pass_index = 0;
    u32 zone_change_record_index = 0;
    u64 source_zone_change_index = 0;
    bool chosen_among_multiple = false;
};



struct CombatDeclarationRecord {
    // Structured twin for declare attacker/blocker events. It snapshots the
    // combat-role identity, defender/attacker target, vigilance tap behavior,
    // and evasion/menace batch context so combat state is auditable before
    // damage assignment.
    u64 sequence = 0;
    CombatDeclarationKind kind = CombatDeclarationKind::Count;
    PlayerId controller{};
    ObjectId actor{};
    u64 actor_zone_change_index = 0;
    TargetRef target{};
    u64 target_zone_change_index = 0;
    PlayerId defending_player{};
    ObjectId attacker{};
    ObjectId blocker{};
    ObjectId attacked_object{};
    u64 attacker_zone_change_index = 0;
    u64 blocker_zone_change_index = 0;
    bool target_is_player = false;
    bool target_is_planeswalker = false;
    bool target_is_battle = false;
    bool tapped_before = false;
    bool tapped_after = false;
    bool vigilance = false;
    bool attacker_had_flying = false;
    bool blocker_had_flying = false;
    bool blocker_had_reach = false;
    bool attacker_had_menace = false;
    u32 blocker_batch_size = 0;
    u32 final_blocker_count_for_attacker = 0;
    bool menace_satisfied = false;
    bool attacker_marked_blocked_after = false;
};

struct CombatDamageAssignmentRecord {
    // Structured twin for combat damage assignment. It captures the attacker/
    // blocker batch context, trample/excess routing, source and target LKI, and
    // links the assignment to the resulting DamageRecord so combat damage can be
    // replayed without scraping combat_damage_* log strings.
    u64 sequence = 0;
    ObjectId source{};
    PlayerId source_controller{};
    u64 source_zone_change_index = 0;
    TargetRef target{};
    u64 target_zone_change_index = 0;
    u32 assigned = 0;
    u32 damage_record_index = 0;
    bool first_strike_batch = false;
    bool split_combat_damage = false;
    bool source_was_attacker = false;
    bool source_was_blocker = false;
    bool attacker_was_blocked = false;
    u32 blocker_count = 0;
    bool source_had_trample = false;
    bool excess_trample = false;
};

struct DamageRecord {
    // Structured twin for the final string damage event. It preserves the
    // source/target snapshot and the requested/prevented/dealt/not-dealt
    // quantities so future replacement, prevention, trigger, and replay code
    // does not have to parse human-readable event text.
    u64 sequence = 0;
    ObjectId source{};
    PlayerId source_controller{};
    TargetRef target{};
    u32 amount = 0;
    u32 prevented = 0;
    u32 dealt = 0;
    u32 not_dealt = 0;
    bool prevented_by_protection = false;
    bool unpreventable = false;
    bool protection_prevention_ignored = false;
    bool source_had_lifelink = false;
    bool source_had_deathtouch = false;
    u32 source_color_mask = ColorNone;
    u32 source_ability_mask = AbilityNone;
    u64 source_zone_change_index = 0;
    u64 target_zone_change_index = 0;
    bool target_was_creature = false;
    bool target_was_planeswalker = false;
    bool target_was_battle = false;
    bool target_was_damageable = false;
    bool damage_disallowed_by_target_type = false;
    u32 counters_removed = 0;
    u32 first_damage_counter_change_record_index = 0;
    u32 damage_counter_change_record_count = 0;
    // rev0178 binds CR 120 damage-to-life results to the typed life ledger.
    // Player damage and lifelink gains now point at the exact LifeChangeRecord
    // rows they caused, so DamageRecord::dealt cannot drift from life totals.
    u32 first_damage_life_change_record_index = 0;
    u32 damage_life_change_record_count = 0;
    u32 first_damage_prevention_record_index = 0;
    u32 damage_prevention_record_count = 0;
};


enum class DamagePreventionRecordKind : u8 {
    ShieldAdded,
    ShieldConsumed,
    ShieldExpired,
    ShieldAppliedToUnpreventableDamage,
    Count
};

struct DamagePreventionRecord {
    // Structured twin for damage-prevention shield lifecycle. It records shield
    // creation, consumption by a DamageRecord, and expiration when an object
    // target changes zones so prevention replay does not depend on prose logs or
    // mutable shield vectors alone.
    u64 sequence = 0;
    DamagePreventionRecordKind kind = DamagePreventionRecordKind::Count;
    u64 shield_id = 0;
    TargetRef target{};
    u32 amount = 0;
    u32 remaining_before = 0;
    u32 remaining_after = 0;
    u32 damage_record_index = 0;
    u32 zone_change_record_index = 0;
    PlayerId affected_player{};
    u32 choice_rank = 0;
    u32 candidate_count = 0;
    u32 pass_index = 0;
    bool chosen_among_multiple = false;
    std::string label;
};




enum class LifeChangeKind : u8 {
    Loss,
    Gain,
    Count
};

struct LifeChangeRecord {
    // Structured twin for life-total mutations. It records the player,
    // before/after totals, signed delta, and gain/loss direction so damage,
    // lifelink, triggers, and future replacement/prevention hooks can audit
    // life changes without scraping lose_life/gain_life strings. Damage-result
    // rows carry a backlink and source/target snapshot to the DamageRecord that
    // caused them, instead of making replay infer CR 120 life results from
    // event prose or adjacent log ordering.
    u64 sequence = 0;
    PlayerId player{};
    LifeChangeKind kind = LifeChangeKind::Count;
    std::int32_t amount = 0;
    std::int32_t life_before = 0;
    std::int32_t life_after = 0;
    ObjectId damage_source{};
    u64 damage_source_zone_change_index = 0;
    TargetRef damage_target{};
    u32 damage_record_index = 0;
    bool damage_result = false;
    bool lifelink_result = false;
};

enum class ManaChangeKind : u8 {
    Produced,
    Paid,
    Emptied,
    Count
};

struct ManaChangeRecord {
    // Structured twin for mana-pool mutations. It captures production,
    // payment, and pool-emptying deltas with before/after pools so casting and
    // mana-ability replay does not infer cost transactions from prose logs.
    u64 sequence = 0;
    PlayerId player{};
    ManaChangeKind kind = ManaChangeKind::Count;
    ManaPool pool_before{};
    ManaPool pool_after{};
    ManaPool added{};
    ManaPool spent{};
    ManaCost cost{};
    ObjectId source{};
    u64 source_zone_change_index = 0;
    u32 mana_ability_index = 0;
    // Cost-plan evidence for automatic payment. Paid records now say how
    // many mana-ability steps were reserved, how many tap sources were
    // locked out before planning, and the stable hash of the planned locked
    // source identities plus mana-ability steps, so cost locks are typed data
    // instead of only prose in mana_auto_plan events. Produced records created
    // by an automatic plan also point back to their owning plan record and
    // one-based step slot, making the execution witness bidirectional.
    u32 auto_payment_mana_ability_count = 0;
    u32 auto_payment_locked_tap_source_count = 0;
    u64 auto_payment_plan_hash = 0;
    u32 auto_payment_plan_record_index = 0;
    u32 auto_payment_producer_plan_record_index = 0;
    u32 auto_payment_producer_plan_step_index = 0;
    bool auto_payment = false;
};

struct ManaPaymentPlanLockedSourceRecord {
    ObjectId source{};
    u64 source_zone_change_index = 0;
};

struct ManaPaymentPlanStepRecord {
    ObjectId source{};
    u64 source_zone_change_index = 0;
    u32 mana_ability_index = 0;
    ManaPool produces{};
    u32 produced_mana_change_record_index = 0;
    u64 tap_event_sequence = 0;
    bool tap_cost = false;
};

struct PaidActionDeclarationRecord {
    // Typed declaration/cost-lock seam for paid spells and stack-using ability
    // activations. It is emitted only inside the staged paid-action body
    // transaction: if a later payment/body step fails, the cloned state is
    // discarded and this declaration record does not leak into the committed
    // journal.
    u64 sequence = 0;
    u32 schema_version = kPaidActionDeclarationRecordSchemaVersion;
    ActionKind action_kind = ActionKind::CastSpellFromHandPaid;
    PlayerId player{};
    ObjectId source_object{};
    ObjectId stack_object{};
    u32 definition_index = 0;
    Zone source_zone_before = Zone::Library;
    u64 source_zone_change_index_before = 0;
    u64 stack_zone_change_index = 0;
    u32 stack_enter_zone_change_record_index = 0;
    u64 stack_object_entered_sequence = 0;
    u64 choices_locked_sequence = 0;
    u32 ability_index = 0;
    std::int32_t loyalty_cost_delta = 0;
    u32 declared_mode_index = 0;
    u64 declared_mode_contract_hash = 0;
    u32 target_mask = TargetNone;
    u32 target_count = 0;
    std::vector<TargetRef> declared_targets{};
    u64 declared_target_set_hash = 0;
    ManaCost total_mana_cost{};
    SacrificeCostDefinition sacrifice_cost{};
    DiscardCostDefinition discard_cost{};
    LifeCostDefinition life_cost{};
    ReturnCostDefinition return_cost{};
    bool total_cost_locked = false;
    bool mana_cost_required = false;
    bool tap_cost_required = false;
    bool sacrifice_cost_required = false;
    bool discard_cost_required = false;
    bool life_cost_required = false;
    bool return_cost_required = false;
    bool loyalty_cost_required = false;
    bool modal_choice_declared = false;
    bool target_choice_declared = false;
    bool payment_attempted = false;
    u64 first_payment_event_sequence = 0;
    u64 last_payment_event_sequence = 0;
    // rev0191 keeps typed nonmana cost receipts in the declaration seal so
    // cost-lock rows carry exact sacrifice/discard payment evidence that later
    // stack-placement and terminal transaction rows must echo.
    u32 first_sacrifice_cost_payment_record_index = 0;
    u32 sacrifice_cost_payment_record_count = 0;
    u64 sacrifice_cost_payment_hash = 0;
    u32 first_discard_cost_payment_record_index = 0;
    u32 discard_cost_payment_record_count = 0;
    u64 discard_cost_payment_hash = 0;
    u32 first_tap_cost_payment_record_index = 0;
    u32 tap_cost_payment_record_count = 0;
    u64 tap_cost_payment_hash = 0;
    u32 first_life_cost_payment_record_index = 0;
    u32 life_cost_payment_record_count = 0;
    u64 life_cost_payment_hash = 0;
    u32 first_return_cost_payment_record_index = 0;
    u32 return_cost_payment_record_count = 0;
    u64 return_cost_payment_hash = 0;
    u32 first_loyalty_cost_payment_record_index = 0;
    u32 loyalty_cost_payment_record_count = 0;
    u64 loyalty_cost_payment_hash = 0;
    u32 stack_placement_record_index = 0;
    u64 declaration_hash = 0;
};


struct PaidActionTransactionRecord {
    // Final paid-action causal receipt. A committed record is emitted after the
    // stack-placement receipt, so consumers can audit one terminal transaction
    // row instead of inferring success from several phase ranges. Rollback rows
    // are reserved for staged-body failures: they preserve speculative-count
    // evidence while confirming the source physical state was restored.
    u64 sequence = 0;
    u32 schema_version = kPaidActionTransactionRecordSchemaVersion;
    PaidActionTransactionOutcome outcome = PaidActionTransactionOutcome::Count;
    ActionKind action_kind = ActionKind::Count;
    PlayerId player{};
    ObjectId source_object{};
    ObjectId stack_object{};
    u32 stack_placement_record_index = 0;
    u32 paid_action_declaration_record_index = 0;
    u64 paid_action_declaration_hash = 0;
    bool committed_paid_action_declaration_snapshot_present = false;
    PaidActionDeclarationRecord committed_paid_action_declaration_snapshot{};
    u64 stack_object_entered_sequence = 0;
    u64 choices_locked_sequence = 0;
    u64 first_paid_action_event_sequence = 0;
    u64 last_paid_action_event_sequence = 0;
    u32 first_mana_payment_plan_record_index = 0;
    u32 mana_payment_plan_record_count = 0;
    u32 first_mana_change_record_index = 0;
    u32 mana_change_record_count = 0;
    u32 first_paid_action_counter_change_record_index = 0;
    u32 paid_action_counter_change_record_count = 0;
    u32 first_paid_action_zone_change_record_index = 0;
    u32 paid_action_zone_change_record_count = 0;
    // rev0191 carries exact sacrifice/discard cost payment receipt ranges to
    // the terminal transaction so auditors do not have to infer nonmana
    // payments indirectly from placement-only phase spans.
    u32 first_sacrifice_cost_payment_record_index = 0;
    u32 sacrifice_cost_payment_record_count = 0;
    u64 sacrifice_cost_payment_hash = 0;
    u32 first_discard_cost_payment_record_index = 0;
    u32 discard_cost_payment_record_count = 0;
    u64 discard_cost_payment_hash = 0;
    u32 first_tap_cost_payment_record_index = 0;
    u32 tap_cost_payment_record_count = 0;
    u64 tap_cost_payment_hash = 0;
    u32 first_life_cost_payment_record_index = 0;
    u32 life_cost_payment_record_count = 0;
    u64 life_cost_payment_hash = 0;
    u32 first_return_cost_payment_record_index = 0;
    u32 return_cost_payment_record_count = 0;
    u64 return_cost_payment_hash = 0;
    u32 first_loyalty_cost_payment_record_index = 0;
    u32 loyalty_cost_payment_record_count = 0;
    u64 loyalty_cost_payment_hash = 0;
    u32 speculative_event_count = 0;
    u32 speculative_event_record_count = 0;
    u32 speculative_stack_placement_record_count = 0;
    u32 speculative_paid_action_declaration_record_count = 0;
    u64 speculative_paid_action_declaration_sequence = 0;
    u64 speculative_paid_action_declaration_hash = 0;
    bool speculative_paid_action_declaration_snapshot_present = false;
    PaidActionDeclarationRecord speculative_paid_action_declaration_snapshot{};
    u64 speculative_first_payment_event_sequence = 0;
    u64 speculative_last_payment_event_sequence = 0;
    // rev0181: for committed transactions these are the pre-action and
    // post-action StateCore hashes, not two equal post-action samples. For
    // rollback transactions they remain the before/after hashes of the
    // committed branch to prove no staged physical mutation leaked out.
    u64 physical_state_hash_before = 0;
    u64 physical_state_hash_after = 0;
    u64 next_event_sequence_before = 0;
    u64 speculative_next_event_sequence_after = 0;
    bool committed = false;
    bool rolled_back = false;
    bool physical_state_preserved_on_rollback = false;
    bool choices_before_payment = false;
    bool payments_before_placement = false;
    bool placement_before_transaction = false;
    u64 transaction_hash = 0;
};

struct PaidActionTransactionJournalHeader {
    // Parsed header for MTGSim.PaidActionTransactionJournal.v1-v9. The counts
    // and hashes intentionally bind the text export back to a concrete
    // GameState without requiring the verifier to deserialize the full state.
    u32 schema_version = kPaidActionTransactionJournalSchemaVersion;
    u64 record_count = 0;
    u64 declaration_record_count = 0;
    u64 stack_placement_record_count = 0;
    u64 journal_hash = 0;
    u64 state_hash = 0;
    // v2 binds the ordered exported transaction rows so truncation, row mixing,
    // or stray schema fields are rejected before any state-bound comparison.
    u64 record_payload_hash = 0;
    // v3 exposes causal row bounds. A standalone verifier rejects zero or
    // non-monotonic transaction sequences and requires these header bounds to
    // match the parsed rows, so an internally self-consistent text export cannot
    // be causally scrambled without being challenged. v4 keeps the header shape
    // stable while row/declaration schemas carry typed sacrifice-cost receipts.
    u64 first_transaction_sequence = 0;
    u64 last_transaction_sequence = 0;
};

struct PaidActionTransactionJournalRecord {
    u32 index = 0;
    u64 line_number = 0;
    PaidActionTransactionRecord transaction{};
    u64 exported_recomputed_transaction_hash = 0;
    u64 exported_committed_snapshot_recomputed_hash = 0;
    u64 exported_speculative_snapshot_recomputed_hash = 0;
};

struct PaidActionTransactionJournal {
    PaidActionTransactionJournalHeader header{};
    std::vector<PaidActionTransactionJournalRecord> records{};
};

struct PaidActionTransactionJournalParseResult {
    bool ok = false;
    PaidActionTransactionJournal journal{};
    u64 error_line = 0;
    std::string error;
};

enum class PaidActionTransactionJournalVerifyFailureKind : u8 {
    None,
    ParseFailed,
    UnsupportedSchema,
    RecordCountMismatch,
    RecordSequenceMismatch,
    TransactionHashMismatch,
    ExportedTransactionHashMismatch,
    SnapshotPresenceMismatch,
    CommittedSnapshotHashMismatch,
    SpeculativeSnapshotHashMismatch,
    OutcomeFlagMismatch,
    StateBindingMismatch,
    RecordPayloadHashMismatch,
    Count
};

struct PaidActionTransactionJournalVerifyResult {
    bool ok = false;
    PaidActionTransactionJournalVerifyFailureKind failure = PaidActionTransactionJournalVerifyFailureKind::None;
    PaidActionTransactionJournalParseResult parse{};
    u64 error_line = 0;
    u64 record_index = 0;
    std::string error;
    u64 expected = 0;
    u64 actual = 0;
    u64 text_hash = 0;
};

struct ManaPaymentPlanRecord {
    // Structured twin for automatic mana-payment planning. It preserves the
    // locked tap-source set and selected mana-ability steps that a paid
    // ManaChangeRecord seals by hash, so agents can audit the plan without
    // parsing mana_auto_plan prose or reverse-engineering pool deltas. Each
    // step is also linked to the produced ManaChangeRecord that executed it,
    // and tap-cost steps name the ordered tap Event sequence that paid the
    // source tap before production. Pool-span snapshots record the mana pool
    // before planning and the pool handed into final payment, turning the plan
    // into an execution witness rather than only intent. The stable identity
    // hash is payer-scoped, so identical empty plans by different players do
    // not collide in replay or multi-agent audit streams. Validation also
    // rejects any tap-cost step that reuses a source snapshot from
    // locked_tap_sources inside the same payment plan.
    // Audit phrase: tap_event_sequence automatic mana tap-event witness.
    // Audit phrase: turning the plan into an execution witness.
    // Audit phrase: payer-scoped automatic payment plan hash.
    u64 sequence = 0;
    PlayerId player{};
    ManaCost cost{};
    ManaPool pool_before_plan{};
    ManaPool pool_before_payment{};
    std::vector<ManaPaymentPlanLockedSourceRecord> locked_tap_sources{};
    std::vector<ManaPaymentPlanStepRecord> mana_ability_steps{};
    u64 plan_hash = 0;
    u32 paid_mana_change_record_index = 0;
};

enum class CounterChangeKind : u8 {
    ObjectAdded,
    ObjectRemoved,
    PlayerAdded,
    Count
};

struct CounterChangeRecord {
    // Structured twin for counter mutations. It preserves object/player
    // identity, the counter kind, before/after counts, and optional damage
    // source context so loyalty, defense, poison, P/T counters, and future
    // counter replacement hooks can audit changes without parsing log text.
    u64 sequence = 0;
    CounterChangeKind kind = CounterChangeKind::Count;
    CounterKind counter_kind = CounterKind::Count;
    ObjectId object{};
    PlayerId player{};
    u64 object_zone_change_index = 0;
    u32 amount = 0;
    u32 count_before = 0;
    u32 count_after = 0;
    ObjectId source{};
    u64 source_zone_change_index = 0;
    u32 zone_change_record_index = 0;
    bool damage_result = false;
    bool cost_payment = false;
    bool zone_change_cleanup = false;
};

enum class DiscardRecordKind : u8 {
    ExplicitChoice,
    CleanupHandSize,
    CostPayment,
    Count
};

struct DiscardRecord {
    // Structured twin for discard choices. It records the player, chosen card,
    // hand/graveyard sizes, and the hand->graveyard ZoneChangeRecord so cleanup
    // discard and future discard effects can be replayed without parsing strings.
    u64 sequence = 0;
    DiscardRecordKind kind = DiscardRecordKind::Count;
    PlayerId player{};
    ObjectId card{};
    u32 hand_size_before = 0;
    u32 hand_size_after = 0;
    u32 graveyard_size_before = 0;
    u32 graveyard_size_after = 0;
    u32 max_hand_size = 0;
    u64 card_zone_change_index_before = 0;
    u64 card_zone_change_index_after = 0;
    u32 zone_change_record_index = 0;
    bool explicit_choice = false;
    bool cleanup_hand_size = false;
    bool cost_payment = false;
    bool used_zone_change_pipeline = false;
};

struct DrawRecord {
    // Structured twin for card-draw events. It forces draws through the
    // zone-change pipeline, preserving the library->hand movement or the
    // empty-library draw attempt so draw/LKI consumers do not depend on
    // direct container mutation or draw_* string logs.
    u64 sequence = 0;
    DrawRecordOutcome outcome = DrawRecordOutcome::Count;
    PlayerId player{};
    ObjectId card{};
    u32 library_size_before = 0;
    u32 library_size_after = 0;
    u32 hand_size_before = 0;
    u32 hand_size_after = 0;
    u32 empty_library_draw_attempts_before = 0;
    u32 empty_library_draw_attempts_after = 0;
    u64 card_zone_change_index_before = 0;
    u64 card_zone_change_index_after = 0;
    u32 zone_change_record_index = 0;
    bool card_moved = false;
    bool empty_library_attempt = false;
};


struct MulliganRecord {
    // Structured twin for a London-style pre-keep mulligan redraw. It records
    // the hand-to-library return, deterministic shuffle, and redraw record
    // ranges so opening-hand consumers can audit mulligans without scraping
    // string logs or bypassing the zone/draw pipelines.
    u64 sequence = 0;
    PlayerId player{};
    u32 mulligans_before = 0;
    u32 mulligans_after = 0;
    u32 opening_hand_size = 0;
    u32 returned_count = 0;
    u32 draw_attempt_count = 0;
    u32 successful_draw_count = 0;
    u32 library_size_before = 0;
    u32 library_size_after_return = 0;
    u32 library_size_after_shuffle = 0;
    u32 library_size_after = 0;
    u32 hand_size_before = 0;
    u32 hand_size_after_return = 0;
    u32 hand_size_after = 0;
    u32 empty_library_draw_attempts_before = 0;
    u32 empty_library_draw_attempts_after = 0;
    u64 rng_state_before = 0;
    u64 rng_state_after = 0;
    u32 first_return_zone_change_record_index = 0;
    u32 return_zone_change_record_count = 0;
    u32 first_draw_record_index = 0;
    u32 draw_record_count = 0;
    bool shuffled = false;
    bool used_zone_change_pipeline = false;
    bool used_draw_pipeline = false;
};



struct MulliganKeepRecord {
    // Structured twin for keeping a mulligan hand and bottoming cards. It
    // records the required bottom count from mulligans_taken, the explicit or
    // deterministic card choices, the hand-to-library movements, and the
    // final bottom-library order so London mulligan setup is executable rather
    // than a redraw-only scaffold.
    u64 sequence = 0;
    PlayerId player{};
    u32 mulligans_taken = 0;
    u32 bottom_count_required = 0;
    u32 bottom_count = 0;
    u32 hand_size_before = 0;
    u32 hand_size_after = 0;
    u32 library_size_before = 0;
    u32 library_size_after = 0;
    u32 first_bottom_zone_change_record_index = 0;
    u32 bottom_zone_change_record_count = 0;
    std::vector<ObjectId> bottomed_cards{};
    bool explicit_choice = false;
    bool deterministic_fallback = false;
    bool used_zone_change_pipeline = false;
    bool placed_on_bottom = false;
};

struct TriggerRecord {
    // Structured twin for queued triggered abilities. It links the event that
    // caused the trigger, the LKI source snapshot, and the eventual synthetic
    // stack object so replay/agent consumers do not infer trigger lifecycle from strings.
    u64 sequence = 0;
    TriggerEventKind event = TriggerEventKind::None;
    ObjectId subject{};
    u64 subject_zone_change_index = 0;
    PlayerId controller{};
    ObjectId source{};
    std::string source_name;
    u32 source_color_mask = ColorNone;
    u32 source_ability_mask = AbilityNone;
    u64 source_zone_change_index = 0;
    EffectKind effect_kind = EffectKind::None;
    u32 effect_amount = 0;
    CounterKind effect_counter_kind = CounterKind::PlusOnePlusOne;
    u32 target_mask = TargetNone;
    u32 target_count = 0;
    // rev0187 trigger target-choice seal: when a pending trigger crosses
    // the CR 603.3d stack gate, the TriggerRecord records the required
    // target count, the selected target vector, how many legal target sets
    // were available to the deterministic chooser, and an ordered hash of
    // the selected set. This makes no-legal-choice drops and successful
    // targeted placements challengeable without parsing event strings.
    u32 required_target_count = 0;
    std::vector<TargetRef> chosen_targets{};
    u32 legal_target_set_count = 0;
    u64 choice_target_set_hash = 0;
    bool target_choice_recorded = false;
    bool no_legal_choices = false;
    u32 created_token_definition_index = 0;
    u64 caused_by_event_sequence = 0;
    ObjectId stack_object{};
    u64 put_on_stack_sequence = 0;
    u32 stack_order = 0;
    // rev0188 resolution backlink. When a triggered ability actually resolves,
    // this keeps the durable TriggerRecord joined to the StackResolutionRecord
    // that performed late target checks and payload application. Countered or
    // otherwise removed abilities legitimately leave these fields empty.
    u32 stack_resolution_record_index = 0;
    u64 resolved_sequence = 0;
    StackResolutionOutcome resolution_outcome = StackResolutionOutcome::Count;
    bool resolved_effect_payload_applied = false;
    bool dropped = false;
    u64 dropped_sequence = 0;
};

struct PendingTrigger {
    PlayerId controller{};
    ObjectId source{};
    ObjectId subject{};
    u64 subject_zone_change_index = 0;
    std::string source_name;
    TriggerEventKind event = TriggerEventKind::None;
    EffectKind effect_kind = EffectKind::None;
    u32 effect_amount = 0;
    CounterKind effect_counter_kind = CounterKind::PlusOnePlusOne;
    u32 target_mask = TargetNone;
    u32 target_count = 0;
    u32 created_token_definition_index = 0;
    u32 source_color_mask = ColorNone;
    u32 source_ability_mask = AbilityNone;
    u64 source_zone_change_index = 0;
    u64 caused_by_event_sequence = 0;
    u32 trigger_record_index = 0;
};

struct DamagePreventionShield {
    u64 id = 0;
    TargetRef target{};
    u32 remaining = 0;
    u32 choice_rank = 0;
    std::string label;
};



struct ActionReceiptRecord {
    // Transition receipt written by apply_action(...). It is intentionally a
    // coarse action boundary, not another one-to-one EventRecord payload: one
    // chosen action may create many rule events before control returns to the
    // caller. Hashes and journal counts are sampled before the receipt itself is
    // appended so the row can audit the rule work the action caused without a
    // self-referential journal hash.
    u64 receipt_index = 0;
    ActionKind kind = ActionKind::PassPriority;
    PlayerId player{};
    ObjectId object{};
    std::vector<TargetRef> targets{};
    u32 mode_index = 0;
    u32 ability_index = 0;
    u32 mana_ability_index = 0;
    std::vector<u32> trigger_order{};
    ChoiceRequestKind choice_kind = ChoiceRequestKind::None;
    u32 choice_request_schema_version = kChoiceRequestSchemaVersion;
    u64 choice_request_hash = 0;
    u64 choice_action_count = 0;
    bool choice_required = false;
    bool choice_action_frontier_complete = true;
    u64 choice_action_generation_limit = 0;
    LegalActionValidationSource choice_validation_source = LegalActionValidationSource::None;
    bool choice_page_location_found = false;
    bool choice_page_location_checked = false;
    u32 choice_page_schema_version = kLegalActionPageSchemaVersion;
    u64 choice_page_state_hash = 0;
    u64 choice_page_choice_request_hash = 0;
    u64 choice_page_requested_limit = 0;
    u64 choice_page_effective_limit = 0;
    u64 choice_page_cursor = 0;
    u64 choice_action_cursor = 0;
    u64 choice_page_index = 0;
    u64 choice_page_next_cursor = 0;
    u64 choice_page_actions_seen = 0;
    u64 choice_page_scanned_pages = 0;
    bool choice_page_complete = true;
    u64 choice_page_total_actions_lower_bound = 0;
    bool choice_page_total_actions_exact = false;
    u64 choice_page_remaining_actions_lower_bound = 0;
    u64 choice_page_hash = 0;
    u64 choice_page_location_hash = 0;
    u32 choice_queue_schema_version = kChoiceRequestQueueSchemaVersion;
    u64 choice_queue_hash = 0;
    u64 choice_queue_index = 0;
    u64 choice_queue_size = 0;
    u32 choice_queue_location_schema_version = kChoiceQueueLocationSchemaVersion;
    bool choice_queue_location_found = false;
    bool choice_queue_location_checked = false;
    u64 choice_queue_location_hash = 0;
    u32 action_schema_version = kLegalActionSchemaVersion;
    u64 action_hash = 0;
    u32 state_schema_version = kStateCoreSchemaVersion;
    u64 state_hash_before = 0;
    u64 state_hash_after = 0;
    u64 journal_hash_before = 0;
    // Post-action/pre-receipt journal sample. `journal_hash_after` is kept as
    // the legacy receipt field name used by ActionTrace-era callers;
    // `journal_hash_after_action` is the explicit rev0122 alias used by the
    // transition kernel and validator so the receipt cannot silently blur its
    // own append row into the action-body journal boundary.
    u64 journal_hash_after = 0;
    u64 journal_hash_after_action = 0;
    u64 journal_entries_before = 0;
    u64 journal_entries_after_action = 0;
    // Legacy field name for the same post-action/pre-receipt count.
    u64 journal_entries_after = 0;
    u64 next_event_sequence_before = 0;
    u64 next_event_sequence_after = 0;
    bool legal_before = false;
    bool applied = false;

    [[nodiscard]] bool has_post_action_journal_seal() const noexcept {
        return journal_hash_before != 0U &&
               journal_hash_after != 0U &&
               journal_hash_after_action == journal_hash_after &&
               journal_entries_after_action == journal_entries_after &&
               journal_entries_after_action >= journal_entries_before;
    }
};

struct ContinuousEffectTarget {
    TargetRef target{};
    u64 object_zone_change_index = 0;
};

struct ContinuousEffectDefinition {
    std::string name;
    StaticEffectDefinition effect{};
    ContinuousEffectDuration duration = ContinuousEffectDuration::UntilCleanup;
    PlayerId controller{};
    ObjectId source{};
    std::vector<ContinuousEffectTarget> locked_targets{};
    u64 timestamp = 0;

    [[nodiscard]] bool active() const noexcept {
        return duration != ContinuousEffectDuration::None && effect.active();
    }
};

struct GameState {
    std::vector<CardDefinition> definitions;
    std::vector<GameObject> objects;
    std::vector<PlayerState> players;
    std::vector<ObjectId> stack;
    u64 rng_state = 0;
    u64 next_event_sequence = 1;
    u64 next_zone_change_index = 1;
    u64 next_damage_prevention_shield_id = 1;
    u64 next_continuous_effect_timestamp = 1;
    u64 next_layer_timestamp = 1;
    PlayerId starting_player{1};
    PlayerId active_player{1};
    PlayerId priority_player{1};
    u32 turn_number = 1;
    Step step = Step::Untap;
    u32 consecutive_priority_passes = 0;
    bool attackers_declared_this_step = false;
    bool combat_damage_assigned_this_step = false;
    bool journal_trimmed = false;
    std::vector<PlayerId> blocker_declaration_complete_players;
    std::vector<PendingTrigger> pending_triggers;
    std::vector<TriggerRecord> trigger_records;
    std::vector<DamagePreventionShield> damage_prevention_shields;
    std::vector<ContinuousEffectDefinition> continuous_effects;
    std::vector<Event> events;
    std::vector<EventRecord> event_records;
    std::vector<StackPlacementRecord> stack_placement_records;
    std::vector<StackResolutionRecord> stack_resolution_records;
    std::vector<PriorityTransitionRecord> priority_transition_records;
    std::vector<StateBasedActionRecord> state_based_action_records;
    std::vector<ZoneChangeRecord> zone_change_records;
    std::vector<ZoneChangeReplacementRecord> zone_change_replacement_records;
    std::vector<CombatDeclarationRecord> combat_declaration_records;
    std::vector<CombatDamageAssignmentRecord> combat_damage_assignment_records;
    std::vector<DamageRecord> damage_records;
    std::vector<DamagePreventionRecord> damage_prevention_records;
    std::vector<LifeChangeRecord> life_change_records;
    std::vector<ManaChangeRecord> mana_change_records;
    std::vector<ManaPaymentPlanRecord> mana_payment_plan_records;
    std::vector<TapCostPaymentRecord> tap_cost_payment_records;
    std::vector<SacrificeCostPaymentRecord> sacrifice_cost_payment_records;
    std::vector<DiscardCostPaymentRecord> discard_cost_payment_records;
    std::vector<LifeCostPaymentRecord> life_cost_payment_records;
    std::vector<ReturnCostPaymentRecord> return_cost_payment_records;
    std::vector<LoyaltyCostPaymentRecord> loyalty_cost_payment_records;
    std::vector<CounterChangeRecord> counter_change_records;
    std::vector<DiscardRecord> discard_records;
    std::vector<DrawRecord> draw_records;
    std::vector<MulliganRecord> mulligan_records;
    std::vector<MulliganKeepRecord> mulligan_keep_records;
    std::vector<PaidActionDeclarationRecord> paid_action_declaration_records;
    std::vector<PaidActionTransactionRecord> paid_action_transaction_records;
    std::vector<ActionReceiptRecord> action_receipt_records;
};

struct PlayerDeck {
    std::string player_name;
    std::vector<u32> definition_indices;
};

struct AttackAssignment {
    ObjectId attacker{};
    TargetRef target{};
    friend constexpr bool operator==(AttackAssignment, AttackAssignment) = default;
};

struct BlockAssignment {
    ObjectId blocker{};
    ObjectId attacker{};
    friend constexpr bool operator==(BlockAssignment, BlockAssignment) = default;
};

struct LegalAction {
    ActionKind kind = ActionKind::PassPriority;
    PlayerId player{};
    ObjectId object{};
    std::string label;
    TargetRef target{};
    std::vector<TargetRef> targets{};
    u32 mode_index = 0;
    u32 ability_index = 0;
    u32 mana_ability_index = 0;
    // For PutPendingTriggersOnStack, this is the one-based TriggerRecord order
    // chosen for pending triggers as they are put on the stack (bottom-to-top).
    // An empty vector preserves the legacy deterministic fallback.
    std::vector<u32> trigger_order{};
};

struct LegalActionFrontier {
    // Bounded generators must not pretend a prefix is the complete legal set.
    // `complete == false` means generation stopped before every candidate was
    // examined. Callers may still submit a canonical action for direct domain
    // validation through is_legal_action/apply_action.
    std::vector<LegalAction> actions{};
    bool complete = true;
    u64 generation_limit = 0;
};

struct LegalActionPage {
    // Deterministic cursor view over a choice domain. schema_version binds
    // replay/page hashes to the external cursor contract, not just contents.
    // `cursor` is the zero-based legal-action offset requested by the caller;
    // `next_cursor` is the first offset not returned. When `complete == false`,
    // another page beginning at `next_cursor` is known to contain at least one
    // action. `actions_seen` is
    // exact only when complete is true; otherwise it is a lower bound proving
    // that at least one candidate exists after this page.
    std::vector<LegalAction> actions{};
    u32 schema_version = kLegalActionPageSchemaVersion;
    ChoiceRequestKind kind = ChoiceRequestKind::None;
    PlayerId chooser{};
    u64 state_hash = 0;
    u64 choice_request_hash = 0;
    u64 cursor = 0;
    u64 next_cursor = 0;
    u64 requested_limit = 0;
    u64 effective_limit = 0;
    u64 actions_seen = 0;
    bool complete = true;
    u64 total_actions_lower_bound = 0;
    bool total_actions_exact = false;
    u64 remaining_actions_lower_bound = 0;
    u64 page_hash = 0;
};

struct LegalActionPageLocation {
    // Optional locator for callers that need to prove where a selected action
    // appears in a particular version of the deterministic paged choice
    // surface. This is separate from
    // validation: an action can be legal by direct domain validation before the
    // caller pays the cost of walking pages to find its offset.
    bool found = false;
    u32 page_schema_version = kLegalActionPageSchemaVersion;
    ChoiceRequestKind kind = ChoiceRequestKind::None;
    PlayerId chooser{};
    u64 page_state_hash = 0;
    u64 page_choice_request_hash = 0;
    u64 requested_page_limit = 0;
    u64 effective_page_limit = 0;
    u64 page_cursor = 0;
    u64 action_cursor = 0;
    u64 index_in_page = 0;
    u64 next_cursor = 0;
    u64 actions_seen = 0;
    u64 scanned_pages = 0;
    bool page_complete = true;
    u64 total_actions_lower_bound = 0;
    bool total_actions_exact = false;
    u64 remaining_actions_lower_bound = 0;
    u64 page_hash = 0;
    u64 action_hash = 0;
    u64 location_hash = 0;
};

struct LegalActionValidation {
    bool legal = false;
    LegalActionValidationSource source = LegalActionValidationSource::None;
    ChoiceRequestKind choice_kind = ChoiceRequestKind::None;
    bool choice_required = false;
    bool action_frontier_complete = true;
    u64 action_generation_limit = 0;
    u64 action_count = 0;
    u64 choice_request_hash = 0;

    [[nodiscard]] bool listed() const noexcept {
        return source == LegalActionValidationSource::OfferedAction;
    }

    [[nodiscard]] bool directly_validated() const noexcept {
        return source == LegalActionValidationSource::DirectDomainValidation;
    }
};

struct ChoiceRequest {
    // Typed choice surface exposed by the engine before a LegalAction is applied.
    // schema_version makes the hash contract visible to receipts/traces instead
    // of burying it solely in the StableHasher domain string. action_set_hash
    // binds replay to the offered choices, not merely to the selected action,
    // so semantic drift in enumeration/order is diagnosable.
    u32 schema_version = kChoiceRequestSchemaVersion;
    ChoiceRequestKind kind = ChoiceRequestKind::None;
    PlayerId chooser{};
    bool required = false;
    bool action_frontier_complete = true;
    u64 action_generation_limit = 0;
    u64 state_hash = 0;
    u64 action_set_hash = 0;
    std::vector<LegalAction> actions{};
};

struct ChoiceRequestQueue {
    // APNAP-ordered set of currently exposed choice requests. This is separate
    // from a single ChoiceRequest so replay can detect global choice-order
    // drift even when the selected player's local action set is unchanged.
    // schema_version makes the queue-hash protocol visible to receipts/traces
    // instead of burying it solely in the StableHasher domain string.
    u32 schema_version = kChoiceRequestQueueSchemaVersion;
    u64 state_hash = 0;
    u64 queue_hash = 0;
    std::vector<ChoiceRequest> requests{};
};

struct ChoiceQueueLocation {
    // Compact proof that the selected action's local ChoiceRequest is the same
    // APNAP queue entry the transition receipt/replay trace claims. This
    // parallels LegalActionPageLocation: detailed fields remain visible while a
    // single seal catches queue/index/request/action drift before mutation.
    bool found = false;
    u32 schema_version = kChoiceQueueLocationSchemaVersion;
    u64 state_hash = 0;
    u64 queue_hash = 0;
    u64 queue_index = 0;
    u64 queue_size = 0;
    ChoiceRequestKind request_kind = ChoiceRequestKind::None;
    PlayerId chooser{};
    bool request_required = false;
    bool action_frontier_complete = true;
    u64 action_generation_limit = 0;
    u64 choice_request_hash = 0;
    u64 choice_action_count = 0;
    u64 action_hash = 0;
    u64 location_hash = 0;
};

struct StateCheckpointSeal {
    // Durable guard for binding an action trace to the exact checkpoint it was
    // exported from. This is intentionally a seal, not full state
    // deserialization yet: it lets persisted replay fail before mutation when
    // the caller supplies the wrong starting GameState. schema_version makes
    // the checkpoint contract explicit instead of burying it in the text header.
    u32 schema_version = kStateCheckpointSealSchemaVersion;
    u64 state_hash = 0;
    u64 journal_hash = 0;
    u64 journal_entries = 0;
    u64 action_receipts = 0;
    u64 object_count = 0;
    u64 player_count = 0;
    u64 stack_size = 0;
    u64 rng_state = 0;
    u64 next_zone_change_index = 0;
    u64 next_event_sequence = 0;
    u32 turn_number = 0;
    Step step = Step::Untap;
    PlayerId active_player{};
    PlayerId priority_player{};
    bool journal_trimmed = false;
};

struct StateCheckpointParseResult {
    bool ok = false;
    StateCheckpointSeal checkpoint{};
    u64 error_line = 0;
    std::string error;
};


enum class TransitionStatus : u8 {
    // A player/system decision is available but has not been selected yet.
    NeedChoice,
    // The proposed transition was rejected before semantic mutation.
    Rejected,
    // The transition committed and exactly one causal action receipt should name it.
    Committed,
    Count
};

struct TransitionResult {
    // Public seam for the reducer contract: current state plus explicit choice
    // should either expose a typed choice request, reject without mutation, or
    // commit with one causal receipt. The first implementation wraps the
    // existing LegalAction/apply_action boundary while preserving legacy
    // apply_action audit semantics for callers that still want illegal-attempt
    // receipts.
    TransitionStatus status = TransitionStatus::Rejected;
    // Canonical selected action for committed/rejected transition attempts.
    // UI labels are stripped before the reducer hashes or records the action so
    // immediate transition callers can hand the result to replay/audit code
    // without retaining the caller's original LegalAction object.
    LegalAction action{};
    ChoiceRequest choice_request{};
    ChoiceRequestQueue choice_queue{};
    u64 choice_queue_index = 0;
    LegalActionValidation validation{};
    LegalActionPageLocation page_location{};
    ChoiceQueueLocation queue_location{};
    bool choice_page_location_checked = false;
    bool choice_queue_location_checked = false;
    bool choice_queue_location_found = false;
    u32 action_schema_version = kLegalActionSchemaVersion;
    u64 action_hash = 0;
    u32 state_schema_version = kStateCoreSchemaVersion;
    // Durable before/after checkpoint seals for the transition boundary.
    // These bind the scalar StateCore/journal fields below to the existing
    // StateCheckpointSeal protocol so immediate callers can verify the exact
    // pre-state they proposed against and the exact post-state that was adopted.
    StateCheckpointSeal checkpoint_before{};
    StateCheckpointSeal checkpoint_after{};
    u64 state_hash_before = 0;
    u64 state_hash_after = 0;
    u64 journal_hash_before = 0;
    u64 journal_hash_after = 0;
    u64 journal_hash_after_action = 0;
    u64 journal_entries_before = 0;
    u64 journal_entries_after_action = 0;
    u64 journal_entries_after = 0;
    u64 action_receipts_before = 0;
    u64 action_receipts_after = 0;
    u64 next_event_sequence_before = 0;
    u64 next_event_sequence_after = 0;
    u64 causal_receipt_index = 0;
    u32 action_receipt_schema_version = kActionReceiptRecordSchemaVersion;
    u64 causal_receipt_hash = 0;
    // Durable hash of the exact ActionTraceEntry row projected from this
    // TransitionResult. The trace handoff seal commits to this field so replay
    // consumers can compare the carried value before reconstructing/exporting
    // the row from receipt history.
    u32 action_trace_entry_schema_version = kActionTraceEntrySchemaVersion;
    u64 action_trace_entry_hash = 0;
    // Durable before-mutation choice/validation seal. This binds the
    // proposed state, canonical selected action (when present), APNAP queue,
    // validation result, and page/queue proof locations before any staged
    // StateCore mutation can be adopted.
    u32 transition_preflight_schema_version = kTransitionPreflightSealSchemaVersion;
    u64 transition_preflight_hash = 0;
    u32 transition_boundary_schema_version = kTransitionBoundarySealSchemaVersion;
    u64 transition_boundary_hash = 0;
    // Durable handoff seal from the immediate transition result to the replay
    // trace row it should project. This closes the boundary between trusted
    // transition adoption and the persisted ActionTraceEntry replay surface.
    u32 transition_trace_handoff_schema_version = kTransitionTraceHandoffSealSchemaVersion;
    u64 transition_trace_handoff_hash = 0;
    bool legal_before = false;
    bool applied = false;
    bool staged_commit_attempted = false;
    bool staged_commit_applied = false;
    bool staged_receipt_checked = false;
    bool staged_receipt_consistent = false;
    bool staged_adoption_guard_passed = false;
    bool staged_commit_adopted = false;
    std::string reason;

    [[nodiscard]] bool need_choice() const noexcept { return status == TransitionStatus::NeedChoice; }
    [[nodiscard]] bool rejected() const noexcept { return status == TransitionStatus::Rejected; }
    [[nodiscard]] bool committed() const noexcept { return status == TransitionStatus::Committed; }

    [[nodiscard]] bool has_transition_checkpoint_seals() const noexcept {
        return checkpoint_before.schema_version == kStateCheckpointSealSchemaVersion &&
               checkpoint_after.schema_version == kStateCheckpointSealSchemaVersion &&
               checkpoint_before.state_hash == state_hash_before &&
               checkpoint_after.state_hash == state_hash_after &&
               checkpoint_before.journal_hash == journal_hash_before &&
               checkpoint_after.journal_hash == journal_hash_after &&
               checkpoint_before.journal_entries == journal_entries_before &&
               checkpoint_after.journal_entries == journal_entries_after &&
               checkpoint_before.action_receipts == action_receipts_before &&
               checkpoint_after.action_receipts == action_receipts_after &&
               checkpoint_before.next_event_sequence == next_event_sequence_before &&
               checkpoint_after.next_event_sequence == next_event_sequence_after;
    }

    [[nodiscard]] bool state_core_unchanged() const noexcept {
        return state_hash_before == state_hash_after && next_event_sequence_before == next_event_sequence_after;
    }

    [[nodiscard]] bool checkpoint_stable() const noexcept {
        return has_transition_checkpoint_seals() &&
               checkpoint_before.state_hash == checkpoint_after.state_hash &&
               checkpoint_before.journal_hash == checkpoint_after.journal_hash &&
               checkpoint_before.journal_entries == checkpoint_after.journal_entries &&
               checkpoint_before.action_receipts == checkpoint_after.action_receipts &&
               checkpoint_before.next_event_sequence == checkpoint_after.next_event_sequence;
    }

    [[nodiscard]] bool journal_unchanged() const noexcept {
        return journal_hash_before == journal_hash_after &&
               journal_entries_before == journal_entries_after &&
               action_receipts_before == action_receipts_after;
    }

    [[nodiscard]] bool rejected_without_mutation() const noexcept {
        return rejected() && state_core_unchanged() && journal_unchanged();
    }

    [[nodiscard]] bool rejected_with_checkpoint_stability() const noexcept {
        return rejected_without_mutation() && checkpoint_stable();
    }

    [[nodiscard]] bool has_selected_action() const noexcept {
        return action_schema_version == kLegalActionSchemaVersion && action_hash != 0U;
    }

    [[nodiscard]] bool committed_with_single_receipt() const noexcept {
        return committed() && applied && has_selected_action() && causal_receipt_index != 0U &&
               action_receipts_after == action_receipts_before + 1U;
    }

    [[nodiscard]] bool has_causal_receipt_hash() const noexcept {
        return action_receipt_schema_version == kActionReceiptRecordSchemaVersion &&
               causal_receipt_index != 0U &&
               causal_receipt_hash != 0U;
    }

    [[nodiscard]] bool has_transition_preflight_seal() const noexcept {
        return transition_preflight_schema_version == kTransitionPreflightSealSchemaVersion &&
               transition_preflight_hash != 0U;
    }

    [[nodiscard]] bool has_transition_boundary_seal() const noexcept {
        return transition_boundary_schema_version == kTransitionBoundarySealSchemaVersion &&
               transition_boundary_hash != 0U;
    }

    [[nodiscard]] bool has_action_trace_entry_seal() const noexcept {
        return action_trace_entry_schema_version == kActionTraceEntrySchemaVersion &&
               action_trace_entry_hash != 0U;
    }

    [[nodiscard]] bool has_transition_trace_handoff_seal() const noexcept {
        return transition_trace_handoff_schema_version == kTransitionTraceHandoffSealSchemaVersion &&
               transition_trace_handoff_hash != 0U;
    }

    [[nodiscard]] bool committed_with_hashed_causal_receipt() const noexcept {
        return committed_with_single_receipt() && has_causal_receipt_hash();
    }

    [[nodiscard]] bool committed_with_staged_adoption() const noexcept {
        return committed_with_single_receipt() &&
               staged_commit_attempted && staged_commit_applied && staged_commit_adopted;
    }

    [[nodiscard]] bool has_post_action_journal_seal() const noexcept {
        return journal_entries_after_action >= journal_entries_before &&
               journal_entries_after == journal_entries_after_action + 1U;
    }

    [[nodiscard]] bool committed_with_checkpoint_seals() const noexcept {
        return committed_with_single_receipt() && has_transition_checkpoint_seals();
    }

    [[nodiscard]] bool committed_with_atomic_adoption_guard() const noexcept {
        return committed_with_staged_adoption() &&
               committed_with_hashed_causal_receipt() &&
               committed_with_checkpoint_seals() &&
               staged_receipt_checked &&
               staged_receipt_consistent &&
               staged_adoption_guard_passed &&
               has_post_action_journal_seal();
    }

    [[nodiscard]] bool committed_with_action_journal_seal() const noexcept {
        return committed_with_atomic_adoption_guard() &&
               journal_hash_after_action != journal_hash_after;
    }

    [[nodiscard]] bool committed_with_preflight_choice_seal() const noexcept {
        return committed_with_atomic_adoption_guard() && has_transition_preflight_seal();
    }

    [[nodiscard]] bool committed_with_transition_boundary_seal() const noexcept {
        return committed_with_atomic_adoption_guard() &&
               has_transition_preflight_seal() &&
               has_transition_boundary_seal();
    }

    [[nodiscard]] bool committed_with_trace_handoff_seal() const noexcept {
        return committed_with_transition_boundary_seal() &&
               has_action_trace_entry_seal() &&
               has_transition_trace_handoff_seal();
    }

    [[nodiscard]] bool has_checked_page_location() const noexcept {
        return choice_page_location_checked && page_location.found &&
               page_location.location_hash != 0U &&
               page_location.page_schema_version == kLegalActionPageSchemaVersion;
    }

    [[nodiscard]] bool has_checked_queue_location() const noexcept {
        return choice_queue_location_checked && choice_queue_location_found &&
               queue_location.found && queue_location.location_hash != 0U &&
               queue_location.schema_version == kChoiceQueueLocationSchemaVersion;
    }

    [[nodiscard]] bool committed_with_choice_proofs() const noexcept {
        return committed_with_single_receipt() &&
               has_checked_page_location() &&
               has_checked_queue_location();
    }
};

enum class TransitionBoundaryFailureKind : u8 {
    None,
    StatusInvalid,
    BoundarySealMissing,
    BoundarySealMismatch,
    PreflightSealMissing,
    PreflightSealMismatch,
    CheckpointSealMismatch,
    BeforeCheckpointMismatch,
    AfterCheckpointMismatch,
    NeedChoiceMutation,
    NeedChoiceMissingActions,
    NeedChoiceCausalReceipt,
    RejectedMutation,
    RejectedCausalReceipt,
    CommittedAtomicGuardMissing,
    TraceEntrySealMissing,
    TraceEntrySealMismatch,
    TraceHandoffSealMissing,
    TraceHandoffSealMismatch,
    ReceiptCountMismatch,
    ReceiptMissing,
    ReceiptIndexMismatch,
    ReceiptHashMismatch,
    ReceiptResultMismatch,
    Count
};

struct TransitionBoundaryVerifyResult {
    // Diagnostic companion to verify_transition_result_boundary(...). The bool
    // wrapper remains for existing callers, while this surface lets replay,
    // search, and agent code localize the first broken seam without re-running
    // the verifier by hand. Hash fields are populated even on early failures
    // when the corresponding evidence is available.
    bool ok = false;
    TransitionBoundaryFailureKind failure = TransitionBoundaryFailureKind::BoundarySealMissing;
    u64 expected_transition_boundary_hash = 0;
    u64 observed_transition_boundary_hash = 0;
    u64 expected_transition_preflight_hash = 0;
    u64 observed_transition_preflight_hash = 0;
    u64 expected_action_trace_entry_hash = 0;
    u64 observed_action_trace_entry_hash = 0;
    u32 expected_action_trace_entry_schema_version = 0;
    u32 observed_action_trace_entry_schema_version = 0;
    u64 expected_transition_trace_handoff_hash = 0;
    u64 observed_transition_trace_handoff_hash = 0;
    u64 expected_causal_receipt_hash = 0;
    u64 observed_causal_receipt_hash = 0;
    u64 causal_receipt_index = 0;

    [[nodiscard]] bool passed() const noexcept { return ok && failure == TransitionBoundaryFailureKind::None; }
    [[nodiscard]] bool failed() const noexcept { return !passed(); }
};

enum class ActionReplayFailureKind : u8 {
    None,
    CheckpointSchemaMismatch,
    CheckpointHashMismatch,
    ChoiceQueueHashMismatch,
    ChoiceRequestHashMismatch,
    ChoiceValidationSourceMismatch,
    ChoicePageLocationMismatch,
    ActionHashMismatch,
    StateHashSchemaMismatch,
    StateHashBeforeMismatch,
    ApplyResultMismatch,
    StateHashAfterMismatch,
    Count
};


struct ActionTraceEntry {
    // Minimal replayable projection of an ActionReceiptRecord. The action is
    // stored without relying on LegalAction::label, and the expected hashes let
    // replay stop at the first divergent transition instead of comparing only a
    // final state. Zero expected hashes are treated as wildcards for hand-built
    // traces.
    LegalAction action{};
    ChoiceRequestKind expected_choice_kind = ChoiceRequestKind::None;
    u32 expected_choice_request_schema_version = 0;
    u64 expected_choice_request_hash = 0;
    u64 expected_choice_action_count = 0;
    bool expected_choice_required = false;
    bool expected_choice_action_frontier_complete = true;
    u64 expected_choice_action_generation_limit = 0;
    LegalActionValidationSource expected_choice_validation_source = LegalActionValidationSource::None;
    bool expected_choice_validation_source_present = false;
    bool expected_choice_page_location_present = false;
    bool expected_choice_page_location_found = false;
    bool expected_choice_page_location_checked = false;
    u32 expected_choice_page_schema_version = 0;
    bool expected_choice_page_context_present = false;
    u64 expected_choice_page_state_hash = 0;
    u64 expected_choice_page_choice_request_hash = 0;
    u64 expected_choice_page_requested_limit = 0;
    u64 expected_choice_page_effective_limit = 0;
    u64 expected_choice_page_cursor = 0;
    u64 expected_choice_action_cursor = 0;
    u64 expected_choice_page_index = 0;
    u64 expected_choice_page_next_cursor = 0;
    u64 expected_choice_page_actions_seen = 0;
    u64 expected_choice_page_scanned_pages = 0;
    bool expected_choice_page_complete = true;
    bool expected_choice_page_count_present = false;
    u64 expected_choice_page_total_actions_lower_bound = 0;
    bool expected_choice_page_total_actions_exact = false;
    u64 expected_choice_page_remaining_actions_lower_bound = 0;
    u64 expected_choice_page_hash = 0;
    u64 expected_choice_page_location_hash = 0;
    u32 expected_choice_queue_schema_version = 0;
    u64 expected_choice_queue_hash = 0;
    u64 expected_choice_queue_index = 0;
    u64 expected_choice_queue_size = 0;
    u32 expected_choice_queue_location_schema_version = 0;
    bool expected_choice_queue_location_found = false;
    bool expected_choice_queue_location_checked = false;
    u64 expected_choice_queue_location_hash = 0;
    u32 expected_action_schema_version = 0;
    u64 expected_action_hash = 0;
    u32 expected_state_schema_version = 0;
    u64 expected_state_hash_before = 0;
    u64 expected_state_hash_after = 0;
    bool expected_applied = true;
};

struct ActionReplayResult {
    bool ok = true;
    ActionReplayFailureKind failure = ActionReplayFailureKind::None;
    u64 attempted = 0;
    u64 applied = 0;
    u64 mismatch_index = 0;
    u64 expected_action_hash = 0;
    u64 actual_action_hash = 0;
    u32 expected_checkpoint_schema_version = 0;
    u32 actual_checkpoint_schema_version = 0;
    u32 expected_action_schema_version = 0;
    u32 actual_action_schema_version = 0;
    u32 expected_state_schema_version = 0;
    u32 actual_state_schema_version = 0;
    u32 expected_choice_request_schema_version = 0;
    u32 actual_choice_request_schema_version = 0;
    u64 expected_choice_request_hash = 0;
    u64 actual_choice_request_hash = 0;
    u64 expected_choice_action_count = 0;
    u64 actual_choice_action_count = 0;
    ChoiceRequestKind expected_choice_kind = ChoiceRequestKind::None;
    ChoiceRequestKind actual_choice_kind = ChoiceRequestKind::None;
    LegalActionValidationSource expected_choice_validation_source = LegalActionValidationSource::None;
    LegalActionValidationSource actual_choice_validation_source = LegalActionValidationSource::None;
    LegalActionPageLocation expected_choice_page_location{};
    LegalActionPageLocation actual_choice_page_location{};
    u32 expected_choice_queue_schema_version = 0;
    u32 actual_choice_queue_schema_version = 0;
    u64 expected_choice_queue_hash = 0;
    u64 actual_choice_queue_hash = 0;
    u64 expected_choice_queue_index = 0;
    u64 actual_choice_queue_index = 0;
    u64 expected_choice_queue_size = 0;
    u64 actual_choice_queue_size = 0;
    u32 expected_choice_queue_location_schema_version = 0;
    u32 actual_choice_queue_location_schema_version = 0;
    u64 expected_choice_queue_location_hash = 0;
    u64 actual_choice_queue_location_hash = 0;
    u64 expected_state_hash = 0;
    u64 actual_state_hash = 0;
    bool expected_applied = false;
    bool actual_applied = false;
};

struct ActionTraceParseResult {
    // Result for the stable text trace codec. Parse failures are deliberately
    // explicit and line-indexed so a persisted replay artifact can fail before
    // it mutates a checkpoint.
    bool ok = false;
    std::vector<ActionTraceEntry> trace;
    u64 error_line = 0;
    std::string error;
};

struct StateCoreSnapshotParseResult {
    // Result for the StateCore snapshot codec. The reconstructed GameState
    // deliberately carries a trimmed/empty journal; source_checkpoint preserves
    // the journal metadata from the state that produced the snapshot so callers
    // can bind a trace to the same StateCore without pretending evidence rows
    // were serialized.
    bool ok = false;
    GameState game{};
    StateCheckpointSeal source_checkpoint{};
    u64 error_line = 0;
    std::string error;
};


enum class ReplayArtifactFailureKind : u8 {
    None,
    UnsupportedFormat,
    ManifestSchemaMismatch,
    ManifestBundleHashMismatch,
    SnapshotTextHashMismatch,
    TraceTextHashMismatch,
    SnapshotParseFailed,
    CheckpointSealMismatch,
    TraceParseFailed,
    ActionCountMismatch,
    TraceReplayFailed,
    FinalStateHashMismatch,
    PaidActionJournalMissing,
    PaidActionJournalTextHashMismatch,
    PaidActionJournalVerifyFailed,
    PaidActionJournalRecordCountMismatch,
    PaidActionJournalStateHashMismatch,
    PaidActionJournalHashMismatch,
    PaidActionJournalPayloadHashMismatch,
    Count
};

struct ReplayArtifactManifest {
    // Durable manifest for binding a StateCoreSnapshot.v1 text artifact to an
    // ActionTrace.v17 text artifact and to the expected final StateCore hash.
    // schema_version makes the manifest/bundle-hash protocol visible instead
    // of burying it solely in the header and hash domain. Hashes are over the
    // exact artifact text, so newline/path-independent tampering is caught
    // before replay or at final-state comparison.
    // v3 can also attach a PaidActionTransactionJournal.v9 export. That keeps
    // replay bundles from proving only the chosen actions while silently
    // dropping the paid-action transaction receipts that explain cost/payment
    // ordering and rollback evidence.
    u32 schema_version = kReplayArtifactManifestSchemaVersion;
    std::string snapshot_format = "MTGSim.StateCoreSnapshot.v1";
    std::string trace_format = "MTGSim.ActionTrace.v17";
    u64 snapshot_text_hash = 0;
    u64 trace_text_hash = 0;
    u64 checkpoint_state_hash = 0;
    u64 checkpoint_journal_hash = 0;
    u64 checkpoint_journal_entries = 0;
    u64 action_count = 0;
    u64 final_state_hash = 0;
    bool applied_only = true;
    bool paid_action_journal_attached = false;
    std::string paid_action_journal_format = "none";
    u64 paid_action_journal_text_hash = 0;
    u64 paid_action_journal_record_count = 0;
    u64 paid_action_journal_state_hash = 0;
    u64 paid_action_journal_journal_hash = 0;
    u64 paid_action_journal_record_payload_hash = 0;
    u64 bundle_hash = 0;
};

struct ReplayArtifactManifestParseResult {
    bool ok = false;
    ReplayArtifactManifest manifest{};
    u64 error_line = 0;
    std::string error;
};

struct ReplayArtifactVerifyResult {
    bool ok = false;
    ReplayArtifactFailureKind failure = ReplayArtifactFailureKind::None;
    std::string error;
    u64 error_line = 0;
    u32 expected_manifest_schema_version = 0;
    u32 actual_manifest_schema_version = 0;
    u64 expected_snapshot_text_hash = 0;
    u64 actual_snapshot_text_hash = 0;
    u64 expected_trace_text_hash = 0;
    u64 actual_trace_text_hash = 0;
    u64 expected_checkpoint_state_hash = 0;
    u64 actual_checkpoint_state_hash = 0;
    u64 expected_checkpoint_journal_hash = 0;
    u64 actual_checkpoint_journal_hash = 0;
    u64 expected_checkpoint_journal_entries = 0;
    u64 actual_checkpoint_journal_entries = 0;
    u64 expected_action_count = 0;
    u64 actual_action_count = 0;
    u64 expected_final_state_hash = 0;
    u64 actual_final_state_hash = 0;
    u64 expected_paid_action_journal_text_hash = 0;
    u64 actual_paid_action_journal_text_hash = 0;
    u64 expected_paid_action_journal_record_count = 0;
    u64 actual_paid_action_journal_record_count = 0;
    u64 expected_paid_action_journal_state_hash = 0;
    u64 actual_paid_action_journal_state_hash = 0;
    u64 expected_paid_action_journal_journal_hash = 0;
    u64 actual_paid_action_journal_journal_hash = 0;
    u64 expected_paid_action_journal_record_payload_hash = 0;
    u64 actual_paid_action_journal_record_payload_hash = 0;
    u64 action_count = 0;
    ActionReplayResult replay{};
    PaidActionTransactionJournalVerifyResult paid_action_journal_verify{};
};

struct ReplayArtifactPrefixResult {
    // A reduced, manifest-bound replay bundle rooted at the original snapshot.
    // For step-level replay failures this keeps the longest known-good prefix
    // and records the next_bad_step that first diverged. For final-hash
    // mismatches, the whole trace is the known-good prefix and the mismatch is
    // isolated to the manifest expectation.
    bool ok = false;
    std::string error;
    ReplayArtifactVerifyResult source_verify{};
    ReplayArtifactFailureKind source_failure = ReplayArtifactFailureKind::None;
    u64 prefix_action_count = 0;
    u64 next_bad_step = 0;
    u64 prefix_final_state_hash = 0;
    std::vector<ActionTraceEntry> prefix_trace;
    std::string prefix_trace_text;
    ReplayArtifactManifest prefix_manifest{};
    std::string prefix_manifest_text;
};

struct ReplayArtifactResumeResult {
    // A manifest-bound resume probe rooted at the longest known-good prefix
    // state. Unlike ReplayArtifactPrefixResult, this writes a new snapshot at
    // the prefix boundary and keeps the suffix trace so the suspect transition
    // becomes step 1 in a smaller replay artifact.
    bool ok = false;
    std::string error;
    ReplayArtifactVerifyResult source_verify{};
    ReplayArtifactFailureKind source_failure = ReplayArtifactFailureKind::None;
    u64 prefix_action_count = 0;
    u64 suffix_action_count = 0;
    u64 next_bad_step = 0;
    u64 resume_state_hash = 0;
    std::string resume_snapshot_text;
    std::vector<ActionTraceEntry> suffix_trace;
    std::string suffix_trace_text;
    ReplayArtifactManifest suffix_manifest{};
    std::string suffix_manifest_text;
    ReplayArtifactVerifyResult suffix_verify{};
};

[[nodiscard]] constexpr std::size_t zone_index(Zone zone) noexcept {
    return static_cast<std::size_t>(zone);
}

[[nodiscard]] const char* to_string(Zone zone) noexcept;
[[nodiscard]] const char* to_string(ManaSymbol symbol) noexcept;
[[nodiscard]] const char* to_string(CardColorMask color) noexcept;
[[nodiscard]] const char* to_string(CounterKind counter_kind) noexcept;
[[nodiscard]] const char* to_string(KeywordAbilityMask ability) noexcept;
[[nodiscard]] const char* to_string(Phase phase) noexcept;
[[nodiscard]] const char* to_string(Step step) noexcept;
[[nodiscard]] const char* to_string(ActionKind action) noexcept;
[[nodiscard]] const char* to_string(ChoiceRequestKind choice_request_kind) noexcept;
[[nodiscard]] const char* to_string(LegalActionValidationSource source) noexcept;
[[nodiscard]] const char* to_string(TransitionBoundaryFailureKind failure) noexcept;
[[nodiscard]] const char* to_string(TargetKind target_kind) noexcept;
[[nodiscard]] const char* to_string(AttachmentKind attachment_kind) noexcept;
[[nodiscard]] const char* to_string(EffectKind effect_kind) noexcept;
[[nodiscard]] const char* to_string(TriggerEventKind trigger_event) noexcept;
[[nodiscard]] const char* to_string(EventRecordKind event_record_kind) noexcept;
[[nodiscard]] const char* to_string(ReplacementPriorityTier priority_tier) noexcept;
[[nodiscard]] const char* to_string(StackPlacementKind stack_placement_kind) noexcept;
[[nodiscard]] const char* to_string(PaidActionTransactionOutcome outcome) noexcept;
[[nodiscard]] const char* to_string(StackResolutionOutcome outcome) noexcept;
[[nodiscard]] const char* to_string(TargetLegalityFailureKind failure_kind) noexcept;
[[nodiscard]] const char* to_string(PriorityTransitionOutcome outcome) noexcept;
[[nodiscard]] const char* to_string(StateBasedActionKind state_based_action_kind) noexcept;
[[nodiscard]] const char* to_string(CombatDeclarationKind combat_declaration_kind) noexcept;
[[nodiscard]] const char* to_string(DrawRecordOutcome draw_record_outcome) noexcept;
[[nodiscard]] const char* to_string(DamagePreventionRecordKind damage_prevention_record_kind) noexcept;
[[nodiscard]] const char* to_string(LifeChangeKind life_change_kind) noexcept;
[[nodiscard]] const char* to_string(ManaChangeKind mana_change_kind) noexcept;
[[nodiscard]] const char* to_string(CounterChangeKind counter_change_kind) noexcept;
[[nodiscard]] const char* to_string(DiscardRecordKind discard_record_kind) noexcept;
[[nodiscard]] const char* to_string(StaticEffectScope scope) noexcept;
[[nodiscard]] const char* to_string(ContinuousEffectDuration duration) noexcept;
[[nodiscard]] Phase phase_for_step(Step step) noexcept;
[[nodiscard]] PlayerId expected_zone_container_player(const GameObject& obj, Zone zone_name) noexcept;

[[nodiscard]] PlayerState& player(GameState& game, PlayerId id);
[[nodiscard]] const PlayerState& player(const GameState& game, PlayerId id);
[[nodiscard]] GameObject& object(GameState& game, ObjectId id);
[[nodiscard]] const GameObject& object(const GameState& game, ObjectId id);
[[nodiscard]] std::vector<ObjectId>& zone(GameState& game, PlayerId id, Zone zone_name);
[[nodiscard]] const std::vector<ObjectId>& zone(const GameState& game, PlayerId id, Zone zone_name);

} // namespace mtgsim
