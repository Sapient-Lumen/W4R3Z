-- MTGSim local card-catalog schema v17.
-- This schema is for local/test card metadata and generated/synthetic card definitions.
-- It intentionally stores no Wizards Oracle text in the datacube.
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS metadata (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS card_definitions (
  card_id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  type_mask INTEGER NOT NULL,
  is_token INTEGER NOT NULL DEFAULT 0,
  power INTEGER NOT NULL DEFAULT 0,
  toughness INTEGER NOT NULL DEFAULT 0,
  loyalty INTEGER NOT NULL DEFAULT 0,
  printed_defense INTEGER NOT NULL DEFAULT 0,
  loyalty_ability_json TEXT NOT NULL DEFAULT '{}',
  loyalty_ability_cost INTEGER NOT NULL DEFAULT 0,
  loyalty_ability_effect_kind TEXT NOT NULL DEFAULT 'none',
  loyalty_ability_effect_amount INTEGER NOT NULL DEFAULT 0,
  loyalty_ability_target_mask INTEGER NOT NULL DEFAULT 0,
  modes_json TEXT NOT NULL DEFAULT '[]',
  mode_count INTEGER NOT NULL DEFAULT 0,
  modal_target_mask_union INTEGER NOT NULL DEFAULT 0,
  activated_abilities_json TEXT NOT NULL DEFAULT '[]',
  activated_ability_count INTEGER NOT NULL DEFAULT 0,
  activated_target_mask_union INTEGER NOT NULL DEFAULT 0,
  activated_tap_cost_count INTEGER NOT NULL DEFAULT 0,
  activated_sorcery_speed_count INTEGER NOT NULL DEFAULT 0,
  mana_abilities_json TEXT NOT NULL DEFAULT '[]',
  mana_ability_count INTEGER NOT NULL DEFAULT 0,
  explicit_mana_ability_count INTEGER NOT NULL DEFAULT 0,
  mana_ability_tap_cost_count INTEGER NOT NULL DEFAULT 0,
  mana_ability_produced_total INTEGER NOT NULL DEFAULT 0,
  static_effects_json TEXT NOT NULL DEFAULT '[]',
  static_effect_count INTEGER NOT NULL DEFAULT 0,
  static_dependency_count INTEGER NOT NULL DEFAULT 0,
  static_granted_ability_mask_union INTEGER NOT NULL DEFAULT 0,
  static_removed_ability_mask_union INTEGER NOT NULL DEFAULT 0,
  static_added_type_mask_union INTEGER NOT NULL DEFAULT 0,
  static_removed_type_mask_union INTEGER NOT NULL DEFAULT 0,
  static_set_color_count INTEGER NOT NULL DEFAULT 0,
  static_added_color_mask_union INTEGER NOT NULL DEFAULT 0,
  static_removed_color_mask_union INTEGER NOT NULL DEFAULT 0,
  static_set_pt_count INTEGER NOT NULL DEFAULT 0,
  static_set_power_total INTEGER NOT NULL DEFAULT 0,
  static_set_toughness_total INTEGER NOT NULL DEFAULT 0,
  static_power_modifier_total INTEGER NOT NULL DEFAULT 0,
  static_toughness_modifier_total INTEGER NOT NULL DEFAULT 0,
  continuous_effects_json TEXT NOT NULL DEFAULT '[]',
  continuous_effect_count INTEGER NOT NULL DEFAULT 0,
  continuous_dependency_count INTEGER NOT NULL DEFAULT 0,
  continuous_duration TEXT NOT NULL DEFAULT 'until_cleanup',
  continuous_granted_ability_mask_union INTEGER NOT NULL DEFAULT 0,
  continuous_removed_ability_mask_union INTEGER NOT NULL DEFAULT 0,
  continuous_added_type_mask_union INTEGER NOT NULL DEFAULT 0,
  continuous_removed_type_mask_union INTEGER NOT NULL DEFAULT 0,
  continuous_set_color_count INTEGER NOT NULL DEFAULT 0,
  continuous_added_color_mask_union INTEGER NOT NULL DEFAULT 0,
  continuous_removed_color_mask_union INTEGER NOT NULL DEFAULT 0,
  continuous_set_pt_count INTEGER NOT NULL DEFAULT 0,
  continuous_power_modifier_total INTEGER NOT NULL DEFAULT 0,
  continuous_toughness_modifier_total INTEGER NOT NULL DEFAULT 0,
  mana_cost_json TEXT NOT NULL DEFAULT '{}',
  colors_json TEXT NOT NULL DEFAULT '[]',
  color_mask INTEGER NOT NULL DEFAULT 0,
  keywords_json TEXT NOT NULL DEFAULT '[]',
  ability_mask INTEGER NOT NULL DEFAULT 0,
  protection_colors_json TEXT NOT NULL DEFAULT '[]',
  protection_color_mask INTEGER NOT NULL DEFAULT 0,
  attachment_kind TEXT NOT NULL DEFAULT 'none',
  attachment_power_bonus INTEGER NOT NULL DEFAULT 0,
  attachment_toughness_bonus INTEGER NOT NULL DEFAULT 0,
  attachment_granted_keywords_json TEXT NOT NULL DEFAULT '[]',
  attachment_granted_ability_mask INTEGER NOT NULL DEFAULT 0,
  taps_for_mana INTEGER NOT NULL DEFAULT 0,
  tap_mana_symbol TEXT NOT NULL DEFAULT 'colorless',
  effect_kind TEXT NOT NULL DEFAULT 'none',
  effect_amount INTEGER NOT NULL DEFAULT 0,
  target_mask INTEGER NOT NULL DEFAULT 0,
  created_token_definition_index INTEGER NOT NULL DEFAULT 0,
  source TEXT NOT NULL DEFAULT 'sample',
  CHECK (is_token IN (0, 1)),
  CHECK (attachment_kind IN ('none', 'aura', 'equipment', 'fortification'))
);
CREATE INDEX IF NOT EXISTS idx_card_definitions_loyalty ON card_definitions(loyalty);
CREATE INDEX IF NOT EXISTS idx_card_definitions_printed_defense ON card_definitions(printed_defense);
CREATE INDEX IF NOT EXISTS idx_card_definitions_loyalty_ability_effect_kind ON card_definitions(loyalty_ability_effect_kind);
CREATE INDEX IF NOT EXISTS idx_card_definitions_mode_count ON card_definitions(mode_count);
CREATE INDEX IF NOT EXISTS idx_card_definitions_modal_target_mask_union ON card_definitions(modal_target_mask_union);
CREATE INDEX IF NOT EXISTS idx_card_definitions_activated_ability_count ON card_definitions(activated_ability_count);
CREATE INDEX IF NOT EXISTS idx_card_definitions_activated_target_mask_union ON card_definitions(activated_target_mask_union);
CREATE INDEX IF NOT EXISTS idx_card_definitions_activated_tap_cost_count ON card_definitions(activated_tap_cost_count);
CREATE INDEX IF NOT EXISTS idx_card_definitions_mana_ability_count ON card_definitions(mana_ability_count);
CREATE INDEX IF NOT EXISTS idx_card_definitions_explicit_mana_ability_count ON card_definitions(explicit_mana_ability_count);
CREATE INDEX IF NOT EXISTS idx_card_definitions_mana_ability_tap_cost_count ON card_definitions(mana_ability_tap_cost_count);
CREATE INDEX IF NOT EXISTS idx_card_definitions_static_effect_count ON card_definitions(static_effect_count);
CREATE INDEX IF NOT EXISTS idx_card_definitions_static_dependency_count ON card_definitions(static_dependency_count);
CREATE INDEX IF NOT EXISTS idx_card_definitions_static_granted_ability_mask_union ON card_definitions(static_granted_ability_mask_union);
CREATE INDEX IF NOT EXISTS idx_card_definitions_static_removed_ability_mask_union ON card_definitions(static_removed_ability_mask_union);
CREATE INDEX IF NOT EXISTS idx_card_definitions_static_added_type_mask_union ON card_definitions(static_added_type_mask_union);
CREATE INDEX IF NOT EXISTS idx_card_definitions_static_removed_type_mask_union ON card_definitions(static_removed_type_mask_union);
CREATE INDEX IF NOT EXISTS idx_card_definitions_static_set_color_count ON card_definitions(static_set_color_count);
CREATE INDEX IF NOT EXISTS idx_card_definitions_static_added_color_mask_union ON card_definitions(static_added_color_mask_union);
CREATE INDEX IF NOT EXISTS idx_card_definitions_static_removed_color_mask_union ON card_definitions(static_removed_color_mask_union);
CREATE INDEX IF NOT EXISTS idx_card_definitions_static_set_pt_count ON card_definitions(static_set_pt_count);
CREATE INDEX IF NOT EXISTS idx_card_definitions_continuous_effect_count ON card_definitions(continuous_effect_count);
CREATE INDEX IF NOT EXISTS idx_card_definitions_continuous_dependency_count ON card_definitions(continuous_dependency_count);
CREATE INDEX IF NOT EXISTS idx_card_definitions_continuous_granted_ability_mask_union ON card_definitions(continuous_granted_ability_mask_union);
CREATE INDEX IF NOT EXISTS idx_card_definitions_continuous_removed_ability_mask_union ON card_definitions(continuous_removed_ability_mask_union);
CREATE INDEX IF NOT EXISTS idx_card_definitions_continuous_added_type_mask_union ON card_definitions(continuous_added_type_mask_union);
CREATE INDEX IF NOT EXISTS idx_card_definitions_continuous_set_pt_count ON card_definitions(continuous_set_pt_count);
CREATE INDEX IF NOT EXISTS idx_card_definitions_type_mask ON card_definitions(type_mask);
CREATE INDEX IF NOT EXISTS idx_card_definitions_is_token ON card_definitions(is_token);
CREATE INDEX IF NOT EXISTS idx_card_definitions_ability_mask ON card_definitions(ability_mask);
CREATE INDEX IF NOT EXISTS idx_card_definitions_color_mask ON card_definitions(color_mask);
CREATE INDEX IF NOT EXISTS idx_card_definitions_protection_color_mask ON card_definitions(protection_color_mask);
CREATE INDEX IF NOT EXISTS idx_card_definitions_attachment_kind ON card_definitions(attachment_kind);
CREATE INDEX IF NOT EXISTS idx_card_definitions_attachment_granted_ability_mask ON card_definitions(attachment_granted_ability_mask);
CREATE INDEX IF NOT EXISTS idx_card_definitions_effect_kind ON card_definitions(effect_kind);
CREATE INDEX IF NOT EXISTS idx_card_definitions_created_token_definition_index ON card_definitions(created_token_definition_index);
CREATE INDEX IF NOT EXISTS idx_card_definitions_name ON card_definitions(name);
