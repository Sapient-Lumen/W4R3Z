# Sensitive Surface Inventory Fields — current

Field contract for `META/Sensitive-Surface-Inventory-current.*`.

Rows: 10

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| surface_id | true | unique ssi_ id | Inventory row id. |
| file | true | package-relative path | File containing the surface. |
| file_scope | true | public/candidate/refresh_note/office_card/governance/meta/schema/longform/tool/root_or_ledger | Coarse file scope. |
| risk_type | true | tool-controlled risk category | Sensitive surface category. |
| severity | true | medium/high | Inventory severity; high in public is a handoff blocker through public lint. |
| occurrence_count | true | integer-like | Count of configured matches in that file/risk class. |
| first_line | true | integer-like | First line where category appears. |
| sample | false | short string | Sample configured match, truncated. |
| public_release_effect | true | non-empty string | Effect before public release. |
| review_note | true | non-empty string | Why this surface needs attention. |
