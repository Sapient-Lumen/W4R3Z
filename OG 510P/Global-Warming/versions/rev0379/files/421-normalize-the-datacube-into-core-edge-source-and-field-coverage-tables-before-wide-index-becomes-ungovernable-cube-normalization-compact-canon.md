---
id: '421'
revision_added: rev0284
status: canon
object_type: ledger
domain_tags:
- cube_governance
- data_model
- metadata
- provenance
- interoperability
- nuclear_preference_audit
- nuclear_energy
- nuclear_regulatory_legitimacy
- nuclear_integrated_energy_systems
- nuclear_cogeneration
- nuclear_desalination
- nuclear_hydrogen
- nuclear_data_centers
- nuclear_system_benefit
- counterfactual_dispatch
- avoided_harm_accounting
- nuclear_cyber_digital_assurance
service_floor:
- cube_normalization_state
- queryable_multidimensional_archive
- field_coverage_visibility
hazard_tags:
- compound_hazard
clock_tags:
- learning_clock
- standards_clock
actor_tags:
- archive_maintainer
- data_steward
- auditor
- service_owner
- research_user
instrument_tags:
- normalized_edge_table
- data_dictionary
- controlled_vocabulary
- source_edge_table
- field_coverage_dashboard
routes_to:
- '364'
- '371'
- '421'
- '422'
- '428'
- '438'
- '439'
- '443'
- '454'
- '455'
- '456'
- '457'
- '458'
- '464'
- '465'
- '466'
- '467'
- '468'
- '498'
source_ids:
- S756
- S757
- S758
- S759
- S760
upstream_dependencies:
- schema_json
- cube_data_dictionary
- source_register
- numbered_files
- route_graph
downstream_consequences:
- better_validation
- easier_query_views
- source_auditability
- less_schema_drift
equity_lenses:
- low_capacity_users
- public_reviewers
- future_maintainers
degraded_modes:
- wide_index_retained_as_backward_compatibility
- normalized_tables_generated_from_index
- manual_source_check
evidence_grade: synthesis
speculation_level: low
bottlenecks:
- wide_table_sprawl
- implicit_semantics
- duplicate_fields
- unowned_metadata
- hard_to_test_routes
failure_modes:
- cube_becomes_prose_index
- queries_break_after_new_columns
- source_use_not_traceable
- sparse_fields_hide_false_maturity
proof_ledgers:
- file_core_table
- tag_edge_table
- route_edge_table
- source_edge_table
- field_coverage_dashboard
- validation_rules
cube_normalization_state: wide index retained, normalized core/tag/route/source/field-coverage
  tables generated, source provenance exposed, and validation rules updated
---

# 421 — Normalize the datacube into core, edge, source, and field-coverage tables before the wide index becomes ungovernable

## Core claim

A datacube is not mature merely because a very wide CSV exists. It is mature when observations, dimensions, attributes, provenance, catalog metadata, field definitions, and validation rules can be separated, queried, regenerated, and audited.

Rev0283 created a data dictionary and route graph. Rev0284 adds the next refactor: a stable wide index remains for human scanning, but the cube now also emits normalized core, tag, route, source, and field-coverage tables. The W3C Data Cube vocabulary treats multidimensional data as observed values organized along dimensions with associated metadata [S756]. DCAT shows why dataset and data-service metadata should be cataloged for discovery and reuse [S757]. PROV-O shows why provenance needs explicit representation across systems and contexts [S758]. FAIR makes the operating rule plain: data should be findable, accessible, interoperable, and reusable, including for machine use [S759]. DCAT-US provides the parallel public-sector metadata discipline for data inventories [S760].

## Refactor packet

A cube revision should now preserve these layers:

- `cube/index.csv` for backward-compatible scanning;
- `cube/file-core.csv` for one row per numbered file;
- `cube/tag-edge-table.csv` for many-to-many tags;
- `cube/route-edge-table.csv` for file-to-file routes;
- `cube/source-edge-table.csv` for file-to-source provenance;
- `cube/field-coverage-dashboard.csv` for sparse-field and schema-growth audit;
- `cube/source-use-ledger.csv` for register-to-use reconciliation;
- `cube/validation-rules.json` for machine-testable expectations.

## Anti-sprawl rule

Do not add a column merely because a new note has a new phrase. Add a column only when a future query or validation rule needs it. Otherwise, encode the relation as a tag edge, route edge, source edge, or register row.

## Cube rule

The field `cube_normalization_state` asks whether a note belongs to the cube's own data-governance layer. Blank is fine for most climate-service notes; blank is not fine for metadata, query, source, or validation packets.

---
Citations point to `sources/register.md`.
