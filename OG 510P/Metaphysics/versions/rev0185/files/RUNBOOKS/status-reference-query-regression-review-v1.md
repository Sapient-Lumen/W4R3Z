# Status, Reference, Query Regression, Claim Language, and Provenance Review Runbook v1

Use this runbook when a release changes current records, status codes, local file references, query behavior, claim-language boundaries, or local provenance records.

1. Update `STATUS_VOCABULARY.yml` before using a new status token in a current record.
2. Update `REFERENCE_MAP.yml` after adding or renaming local artifacts.
3. Run `python3 tools/check_reference_integrity.py .` and resolve any missing local paths or declare a justified wildcard exclusion.
4. Update `QUERY_REGRESSION_SUITE.yml` when a cube query becomes part of the release boundary.
5. Run `python3 tools/run_query_regression.py .`.
6. Update `CLAIM_LANGUAGE_LEDGER.yml` before changing allowed or forbidden public-use wording.
7. Update `PROVENANCE_LEDGER.yml` when the source package, generated artifacts, build activities, or local tool agents change.
8. Run `python3 tools/validate_archive.py .` before packaging and again after fresh extraction.

Stop conditions: undefined current status tokens, missing declared local references, failed query regression, provenance overclaim, compliance overclaim, or a current record missing required fields.
