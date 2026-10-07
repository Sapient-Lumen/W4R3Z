# Package Dependency Graph Fields current

| field | required | allowed/pattern | meaning |
|---|---:|---|---|
| edge_id | true | ^dep_[0-9]{5}$ | Dependency edge id. |
| edge_type | true | controlled edge type | Dependency type, such as input_feeds_generated_artifact or ledger_mirrors_json. |
| source_path | true | package-relative path | Source side of the dependency edge. |
| target_path | true | package-relative path | Target side of the dependency edge. |
| generator | false | tools/*.py path | Generator script when applicable. |
| status | true | pass|missing_dependency|info | Whether edge paths exist under configured checks. |
| note | true | non-empty string | Interpretive note for the edge. |
