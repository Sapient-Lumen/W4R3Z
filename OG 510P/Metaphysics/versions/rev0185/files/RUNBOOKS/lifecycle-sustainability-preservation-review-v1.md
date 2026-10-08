# Lifecycle sustainability and preservation review runbook v1

Use this runbook before making maintainership, dependency, preservation, portability, succession, or end-of-life claims.

1. Confirm `MAINTAINERSHIP_STEWARDSHIP_LEDGER.yml` records local stewardship without public support or maintenance SLA language.
2. Confirm `DEPENDENCY_UPDATE_POLICY.yml` records dependency review triggers without automated scanning, vulnerability monitoring, or update-service claims.
3. Confirm `PRESERVATION_ARCHIVAL_PLAN.yml` records package-local preservation targets without archival guarantee, repository, or hosting claims.
4. Confirm `PORTABILITY_INTEROPERABILITY_MATRIX.yml` records practical export surfaces without certification, conformance, or migration guarantees.
5. Confirm `SUCCESSION_CONTINUITY_PLAN.yml` records local handoff boundaries without legal successor designation or authority transfer.
6. Confirm `SUNSET_END_OF_LIFE_LEDGER.yml` records local sunset/deprecation triggers without public notice service, downstream recall, or migration support.
7. Run `python3 tools/check_lifecycle_sustainability.py .` and preserve the six generated report files.
8. Re-run release gates, query regression, reference integrity, fixtures, invariant checks, and manifest generation.

Allowed claim: local lifecycle sustainability surfaces are present and checked.

Forbidden claim: public support, guaranteed maintenance, archival preservation, certified interoperability, legal succession, downstream migration, or public end-of-life service.
