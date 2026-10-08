# rev0094 to rev0095 migration map

## Compatibility

rev0095 does not change the TimeState core, profile catalog, transport adapter catalog, or evidence-class catalog. Existing valid rev0094 retained exports remain valid when their embedded assessment, policy, validity-horizon, and evidence-summary timestamps do not occur after `export_context.exported_at`.

## New semantic failures

A retained export that previously passed may now fail if it contains any of the following:

```text
profile_assessments[*].assessment_time > export_context.exported_at
profile_assessments[*].policy_acceptance.checked_at > export_context.exported_at
profile_assessments[*].validity_horizon.evaluated_at > export_context.exported_at
evidence_input_summaries[*].assessment_time > export_context.exported_at
export_context.purpose == current_policy_recheck and current_policy_checked is not true
current_policy_recheck plus actionable/conditional validity_horizon outside the export-time validity window
```

## New files

```text
tools/retained_export_temporal.py
tools/fixture_derivations.py
tests/fixture-derivations.yaml
examples/negative/retained-export-assessment-after-export-invalid.json
examples/negative/retained-export-current-recheck-unchecked-invalid.json
examples/negative/retained-export-current-recheck-expired-actionability-invalid.json
AUDIT-2026.06.12-rev0095.md
archive/REV0095-AUDIT-RETAINED-EXPORT-FIXTURE-REFACTOR.md
```

## Updated files

```text
tools/validate_archive.py
tools/lint_revision_references.py
tests/semantic-test-vectors.yaml
tests/acceptance-tests.md
tests/TRACEABILITY-MATRIX.md
README.md
START_HERE.md
INDEX.md
VALIDATION-REPORT.md
CHANGELOG.md
REVISION-RECEIPT.json
frontier-ticket.json
MANIFEST.json
```
