# SQLite card catalog hook — through rev0024

rev0008 adds the first concrete card-data database hook. The goal is not to implement real card import yet; the goal is to create a small, audited, reproducible shape that later importers can target.

## Files

- `data/cards/sample_cards.json`: tiny sample/fake input deck of card definitions.
- `data/cards/schema/card_catalog_schema.sql`: SQLite schema for normalized card definitions and metadata.
- `tools/card_db.py`: stdlib-only builder that loads JSON, validates coarse fields, computes type/target masks, writes SQLite, and emits a JSON report.
- `reports/cards/card_catalog.sqlite`: generated local catalog.
- `reports/cards/card_catalog_report_latest.json`: generated metrics/report summary.

## Why SQLite here

SQLite is a practical local spine for generated card metadata because it is portable, queryable, cacheable, and easy for Python and C++ tooling to inspect. The engine core should not parse large external card dumps during hot simulation loops. Instead, importers can normalize card metadata into compact DB artifacts and later compile/load the subset needed for a benchmark, scenario, or ML rollout.

## Current schema

`card_definitions` currently stores:

- dense `card_id`;
- card `name`;
- bit-packed coarse type mask;
- power/toughness;
- normalized mana-cost JSON;
- simple tap-for-mana metadata;
- simple effect kind/amount;
- target mask;
- source path.

`metadata` stores schema, input path, notice, and generation timestamp.

## Boundary with official data

The checked-in sample data is fictional. Future importers can read MTGJSON or Scryfall-style bulk data, but this cube should not bundle official Oracle text or images unless a later license/legal review explicitly approves it.

## Harness integration

`tools/harness.py cards` runs the builder directly. The `test`, `all`, and `matrix` plans now include the card catalog step so drift in the DB importer is caught together with rules/scenario/fuzz regressions.

## rev0012 keyword columns

The local SQLite card catalog schema now stores `keywords_json` plus a compact `ability_mask` for fictional/sample cards. This is not a rules implementation and it is not Oracle text. It is a normalization seam: future importers can ingest Scryfall/MTGJSON-style bulk data into a local catalog, while the C++ engine continues to prove behavior through rule-ledger-linked tests.

## rev0013 keyword-mask expansion

The sample card catalog importer now recognizes `first_strike`, `double_strike`, `trample`, and `indestructible` in addition to the rev0012 keyword subset. The sample catalog remains fictional and should not be interpreted as Oracle import. It is a low-risk SQLite target for metadata-shape experiments while C++ tests and the rule ledger remain the source of rule-conformance claims.


## rev0014 keyword-mask expansion

The sample importer now recognizes `haste`, `defender`, `hexproof`, and `shroud` in addition to earlier keyword bits. The checked-in sample catalog remains tiny and fictional, but it now exercises the same ability-mask vocabulary used by attack legality and source-aware targeting tests.


## rev0015 color/protection metadata

The sample SQLite card catalog schema is now `v3` and stores `colors_json`, `color_mask`, `protection_colors_json`, and `protection_color_mask`. The default fictional sample data includes a menace creature and a protection-from-red creature. This database path is metadata plumbing, not rules proof: executable conformance still comes from the C++ tests, scenarios, fuzzing, and rule ledger.

## rev0016 effect samples

The fictional sample catalog now includes two noncreature effect cards: a destroy-object spell and a regeneration-object spell. The SQLite schema already had `effect_kind`, `effect_amount`, and `target_mask`; rev0016 uses those columns as a tiny smoke path for future generated-card metadata without importing official Oracle text.

## rev0017 attachment metadata

The sample SQLite card-catalog schema advanced from `v4` to `v5`. It still stores `attachment_kind`, attachment P/T bonuses, attachment-granted keyword JSON, and `attachment_granted_ability_mask`. The fictional sample catalog now includes a simple Aura and Equipment. This is still metadata plumbing only: the rules proof lives in C++ tests, data-driven scenarios, fuzz/invariants, and the rule ledger.

## rev0018 schema v5: token/effect payload metadata

The local fictional card catalog advanced to `mtgsim.card_catalog.v5`. It now records `is_token` and `created_token_definition_index`, plus report counts for token sample cards, create-token effect cards, and exile effect cards. This is still only metadata for local/generated fixtures; it does not imply Oracle-text ingestion or rules correctness.


## rev0019 catalog v6

The sample SQLite card catalog advanced to `mtgsim.card_catalog.v6`. It now stores fictional planeswalker metadata: printed loyalty, a compact loyalty-ability JSON payload, loyalty cost, effect kind/amount, and target mask. The catalog remains metadata glue only; rules correctness still comes from focused C++ and scenario tests.


## rev0020 card-catalog v7

The sample SQLite catalog now records `printed_defense` for fictional battle definitions and reports `battles` plus `battle_defense_cards` in the generated summary. The catalog remains metadata-only and does not prove rules correctness.


## rev0021 modal metadata

The fictional sample catalog schema is now `mtgsim.card_catalog.v8`. It stores `modes_json`, `mode_count`, and `modal_target_mask_union` so downstream tools can plan mode-aware tests without parsing C++ definitions. This remains sample metadata only; it is not an Oracle-text parser.

## rev0022 timing and flash metadata

The fictional sample catalog schema is now `mtgsim.card_catalog.v9`. The schema shape is unchanged from v8, but the keyword mask and sample data now include `flash`, and the generated report counts `flash_cards`. The new fictional samples are `Sample Flash Ambusher`, `Sample Timing Ritual`, and `Sample Training Ground`.

## Rev0023 activated ability metadata

The sample SQLite card catalog advanced to `mtgsim.card_catalog.v10`. It records `activated_abilities_json`, `activated_ability_count`, `activated_target_mask_union`, `activated_tap_cost_count`, and `activated_sorcery_speed_count`. These fields are for local/generated metadata and do not bundle official Oracle text.


## Rev0024 mana-ability metadata

The fictional sample catalog advanced to `mtgsim.card_catalog.v11`. It records `mana_abilities_json`, `mana_ability_count`, `explicit_mana_ability_count`, `mana_ability_tap_cost_count`, and `mana_ability_produced_total`. The sample data now includes fictional explicit mana sources such as `Sample Mana Prism` and `Sample Chromatic Filter`. This remains local metadata plumbing; rules conformance is proven by C++ tests, scenario fixtures, fuzz/invariants, and the rule ledger.

## Schema v12: static effects

The fictional card catalog now records `static_effects_json`, `static_effect_count`, `static_granted_ability_mask_union`, `static_power_modifier_total`, and `static_toughness_modifier_total`. These fields are metadata for tests and tooling only; they are not a replacement for rules conformance.



## rev0027 card catalog v13

The fictional SQLite catalog now records static type/color payload summaries: added/removed type unions, color-set counts, and added/removed color unions. These fields are import smoke tests for card metadata plumbing; they are not proof that real Oracle text has been parsed or implemented.


## rev0028 catalog delta

The local fictional card catalog advances to `mtgsim.card_catalog.v14`. Static-effect metadata now includes ability-removal summaries (`static_removed_ability_mask_union`) and base-P/T-set summaries (`static_set_pt_count`, `static_set_power_total`, `static_set_toughness_total`). These columns are for local generated/test cards only; they are not a substitute for Oracle-text parsing or Comprehensive Rules coverage.
## Schema v15: temporary continuous-effect metadata

rev0029 advances the fictional card catalog to `mtgsim.card_catalog.v15`. It adds `continuous_effects_json`, `continuous_effect_count`, duration metadata, and summary masks/totals for temporary ability, type, color, base-P/T, and P/T-modifier payloads. These are local synthetic rows only; they do not contain Wizards Oracle text.

## Schema v16: copy-effect samples

rev0030 advances the fictional card catalog to `mtgsim.card_catalog.v17`. The schema shape remains compatible with v15, but the importer now reports `copy_effect_cards` by using the existing `effect_kind` column, and the sample data includes fictional copy-effect rows. This remains local metadata plumbing only; copy-rule conformance is measured by focused C++ tests, scenario fixtures, validation, and the rule ledger.

## rev0032 dependency metadata

rev0032 advances the fictional catalog metadata to `mtgsim.card_catalog.v17`. The schema adds `static_dependency_count` and `continuous_dependency_count`, and `normalize_static_effects(...)` preserves `depends_on_effect_names` inside the JSON payload. This keeps dependency-ordering fixtures queryable without implying that the sample catalog can infer real Oracle-text dependencies.
