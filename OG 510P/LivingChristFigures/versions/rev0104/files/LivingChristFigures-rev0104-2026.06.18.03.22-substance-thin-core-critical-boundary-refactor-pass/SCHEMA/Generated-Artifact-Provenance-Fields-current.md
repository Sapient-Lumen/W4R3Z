# Generated Artifact Provenance Fields current — current

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| artifact_path | true | package-relative path | Generated artifact being tracked. |
| generator | true | tools/*.py path | Generator script responsible for the artifact. |
| input_paths | true | pipe-separated paths | Inputs whose combined fingerprint is recorded. |
| artifact_sha256 | true | sha256 hex | Artifact hash at build time. |
| input_fingerprint | true | sha256 hex | Combined hash of generator and input files. |
| row_count | true | integer-like | CSV data-row count if artifact is CSV. |
| status | true | pass/missing_dependency_or_artifact | Provenance status. |
| note | true | non-empty string | Notes or missing dependencies. |
