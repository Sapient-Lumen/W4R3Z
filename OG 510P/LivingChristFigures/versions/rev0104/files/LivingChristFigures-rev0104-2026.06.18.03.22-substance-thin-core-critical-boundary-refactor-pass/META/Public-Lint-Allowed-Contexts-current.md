# Public Lint Allowed Contexts — current

Generated/curated for `rev0065`.

Allowed-context table for reducing false positives where risky words appear only as prohibitions. This table does not permit exposing the underlying risky information.

Rows: 5

| context_id | context_code | allowed_when | example_shape | lint_effect | status |
| --- | --- | --- | --- | --- | --- |
| public_lint_context_001 | policy_negation | term appears inside a prohibition, refusal, or no-public-expansion statement | This public edition must not include contact routes, coordinates, live capacity, or case-list detail. | downgrade_false_positive_only_after_boundary_phrase_detected | active |
| public_lint_context_002 | boundary_statement | term appears while defining what the public layer withholds | Boundary index only; no referral path, no operational instructions, no vigil map. | downgrade_false_positive_only_after_boundary_phrase_detected | active |
| public_lint_context_003 | prohibited_use_list | term appears in an explicit prohibited-use list | Do not use this cube as a referral directory, case list, safety dashboard, or public contact index. | downgrade_false_positive_only_after_boundary_phrase_detected | active |
| public_lint_context_004 | manifest_description | term appears in package metadata describing withheld classes of material | Public export excludes URLs, locations, operational capacity, and case-adjacent detail. | downgrade_false_positive_only_after_boundary_phrase_detected | active |
| public_lint_context_005 | template_instruction | term appears in a renderer/template instruction telling operators not to emit risky detail | Template may say no contact or route fields are allowed; it may not provide them. | downgrade_false_positive_only_after_boundary_phrase_detected | active |
