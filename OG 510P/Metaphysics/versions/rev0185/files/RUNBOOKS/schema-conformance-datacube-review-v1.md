# Schema Conformance and Datacube Review Runbook v1

## Purpose

This runbook governs local review of schema-conformance reports, `CONTROL_STACK.yml`, `CUBE_INDEX.yml`, and current release records. It is a local archive runbook only. It does not create public linked data, SHACL validation, RDF publication, FAIR certification, independent audit, public query service, source-watch automation, domain review, or operational deployment authority.

## Entry criteria

Use this runbook when a release claims any of the following:

1. a current register record satisfies a declared schema;
2. the control sequence is canonical rather than only repeated prose;
3. the archive has a datacube, cube index, queryable row layer, or observation map;
4. a source, claim, risk, capacity packet, incident lesson, or deployment boundary can be found by structured query;
5. the validator checks more than package presence and manifest hashes.

## Required artifacts

- `CONTROL_STACK.yml`
- `CUBE_INDEX.yml`
- `EXTERNAL_CROSSWALK.yml`
- `REGISTERS/schemas/schema-conformance-report-v1.yml`
- `REGISTERS/schemas/control-stack-record-v1.yml`
- `REGISTERS/schemas/datacube-index-record-v1.yml`
- `REGISTERS/rev0165-schema-conformance.yml`
- `REGISTERS/rev0165-control-stack.yml`
- `REGISTERS/rev0165-datacube-index.yml`
- current full-profile records for validation, workflow, automation, semantic fidelity, deployment boundary, incident response, post-incident learning, effectiveness monitoring, risk portfolio, and capacity allocation
- a validation transcript showing whether the local validator passed after manifest regeneration

## Procedure

1. **Classify profile.** Mark current release records as `full_current_release`; retain older compact records as historical unless they are separately migrated.
2. **Check required fields.** For every current release record mapped to a schema, confirm that every listed `required_fields` entry is present and non-empty.
3. **Check control stack.** Confirm that `CONTROL_STACK.yml` covers steps `144` through the current final numbered document and includes the final step.
4. **Check cube index.** Confirm that `CUBE_INDEX.yml` names observation families, dimension families, measure families, attribute families, query examples, and current release observations.
5. **Check forbidden claims.** Confirm that records and release notes forbid public RDF publication, SHACL validation, FAIR compliance, external certification, public monitoring, domain authority, and operational deployment unless separate evidence exists.
6. **Run local validation.** Regenerate `MANIFEST.sha256`, run `python tools/validate_archive.py .`, and record the result.
7. **Name open debt.** Record missing status-vocabulary checks, cross-reference checks, executable query harnesses, independent reproduction, historical normalization, and external/domain review as open debt where appropriate.

## Exit criteria

The release may claim local schema-conformance/datacube-control governance only if:

- the final document is listed in `README.md`, `ARCHIVE_INDEX.md`, and `docs/00-start-here.md`;
- current release records satisfy their required-field schemas;
- `CONTROL_STACK.yml` and `CUBE_INDEX.yml` are present and structurally checked;
- the validation transcript lists what passed, what was not run, and what remains open debt;
- forbidden claim language is present.

## Stop conditions

Stop or release-with-declared-debt if any of the following appears:

- a current full-profile record misses a required field;
- a schema is named but not mapped to the record using it;
- `CONTROL_STACK.yml` omits the current final numbered file;
- `CUBE_INDEX.yml` claims executable queries without a query harness;
- external-source analogies are written as compliance claims;
- public query, public monitoring, source-watch, domain authority, or operational deployment is implied without evidence.
