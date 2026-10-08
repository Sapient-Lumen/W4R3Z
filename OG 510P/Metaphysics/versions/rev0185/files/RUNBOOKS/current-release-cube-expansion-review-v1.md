# Current-release cube-expansion review runbook v1

Scope: `rev0181` local package governance only.

1. Confirm `VERSION` and `CURRENT_RELEASE.yml` agree.
2. Confirm the front door opens with `rev0181` rather than a historical revision.
3. Run `tools/check_current_release.py .`.
4. Run `tools/check_stale_revision_tokens.py .` and review warnings.
5. Run `tools/generate_debt_observations.py .` when open-debt rows change.
6. Run `tools/check_expanded_cube.py .` to confirm cube datasets and observation files exist.
7. Run `tools/check_schema_constraints.py .` to confirm new schemas expose the rev0181 constraint profile.
8. Run `tools/run_query_regression.py .`.
9. Run `tools/check_reference_integrity.py . > REFERENCE_MAP.yml` and copy the same output to the current reference-integrity report when needed.
10. Run `tools/validate_archive.py .`.

Allowed claim: local current-release, cube-expansion, debt/source/access/concept observation surfaces are checked.

Forbidden claims: public deployment, RDF publication, SHACL validation, WCAG conformance, legal compliance, external audit, signed provenance, and philosophical completeness.
