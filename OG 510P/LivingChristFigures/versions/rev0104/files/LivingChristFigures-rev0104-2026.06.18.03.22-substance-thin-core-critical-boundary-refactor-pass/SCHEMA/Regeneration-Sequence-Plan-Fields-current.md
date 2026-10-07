# Regeneration-Sequence-Plan Fields — current

Rows: 9

| field | required | allowed_values_or_pattern | meaning |
| --- | --- | --- | --- |
| step_id | true | regen_[0-9]{3} | Stable deterministic regeneration-plan step identifier. |
| phase | true | ordered phase label | Coarse phase for deterministic ordering. |
| tool_path | true | tools/*.py | Generator tool path. |
| command | true | shell command string | Reviewable command for regenerating the declared outputs. |
| declared_outputs | true | pipe-separated package paths | Tracked output artifacts declared for the tool. |
| declared_inputs | false | pipe-separated package paths | Named input paths declared in generated-artifact provenance. |
| dependency_status | true | pass/missing_dependency | Pass when all declared tool/output/input paths exist. |
| execution_mode | true | plan_only_deterministic_order | Indicates this report is a plan, not an asynchronous runner. |
| note | false | free text | Human-readable path dependency note. |
