# Package File Inventory Fields current

| field | required | allowed/pattern | meaning |
|---|---:|---|---|
| file_path | true | package-relative path | Inventoried package file path. |
| size_bytes | true | integer | File size in bytes. |
| sha256 | true | 64 lowercase hex characters | SHA-256 digest recorded by the file inventory. |
| package_zone | true | root_handoff_layer|candidate_layer|office_card_layer|longform_layer|public_layer|governance_layer|meta_audit_layer|schema_contract_layer|tooling_layer | Primary package zone for the file. |
| file_role | true | controlled role label | Coarse file role used to identify accidental or unclassified package surfaces. |
| currentness | true | current_surface|recent_revision_record|historical_revision_record|current_or_static | Whether the file is current, recent revision history, historical revision history, or static. |
| generated_by | false | tool path or empty | Generator path when known from generated-artifact provenance. |
| public_release_scope | true | public_layer_file_allowlist_required|not_public_layer | Whether the file is inside the public-release layer. |
| notes | false | free text | Inventory note, including self-recursion exclusions. |
