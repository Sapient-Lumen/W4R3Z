# Report Contract Registry Fields — current

Field schema for rev0066 report-contract registry/audit surfaces.

Rows: 16

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| contract_id | yes | report_contract_[0-9]{4} | stable registry row id |
| surface_path | yes | package-relative *-current.csv path | current CSV surface being described |
| package_zone | yes | root/meta/schema/governance/public | package zone |
| surface_family | yes | string | report family basename |
| csv_path | yes | package-relative csv path | primary CSV path |
| json_path | no | package-relative json path | sibling JSON mirror when present |
| markdown_path | no | package-relative md path | sibling Markdown companion when present |
| schema_path | no | SCHEMA path or Ledger-Contract/README path | field schema, ledger contract, or schema policy surface |
| schema_contract_type | yes | dedicated_field_schema/ledger_contract/field_schema_self_describing/schema_layer_controlled_vocabulary/missing_or_manual_contract | contract mechanism |
| generator_or_owner | yes | tool path or manual owner code | generator or deliberate owner |
| row_count | yes | integer | CSV data row count |
| json_row_count | yes | integer | JSON list row count when applicable |
| companion_policy | yes | csv_json_required/csv_json_md_required/csv_json_md_present_root_optional | companion expectations |
| public_boundary | yes | controlled-ish boundary string | public/use boundary for the surface |
| status | yes | pass/fail | registry row status |
| note | yes | free text | explanation |
