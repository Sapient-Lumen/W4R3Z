# Schema-fixture coverage audit and refactor

rev0176 includes an explicit audit/refactor pass because the archive is no longer only doctrinal. By rev0175 it contained 77 schemas, 76 examples, and 50 negative fixtures. The linter could prove that individual JSON files parsed and selected example/schema pairs validated, but a human reader still could not quickly answer: Which rights domain does this object family govern? Which negative fixtures test it? Which surfaces own it? Which family is missing from the map?

## Findings

1. **Schema validity was necessary but too local.** A file could validate while the family had no visible owner, lifecycle axis, or negative fixture.
2. **Fixture growth was cumulative but under-indexed.** The fixture suite and report knew what ran, but not which domain each object family belonged to.
3. **Linter hard-coding is now a maintenance risk.** A growing list of example pairs inside `tools/lint_archive.py` is useful for release hygiene but not sufficient as a governance map.
4. **The research tail remains packet-dense.** The archive has many research micro-doctrines. This pass does not move them, but it creates the mapping discipline needed before any future compaction.
5. **Domain vocabulary needed a registry.** Without a registry, new schemas become a pile of files rather than a cube layer.

## Refactor performed

rev0176 adds:

- `schemas/schema-fixture-domain-registry.schema.json`;
- `examples/schema-fixture-domain-registry-rev0176.json`;
- `tools/audit_schema_fixture_coverage.py`;
- linter integration so the registry audit runs during `make lint`;
- a new doctrine surface, `docs/30-transition/schema-fixture-domain-registry-and-refactor-controls.md`.

The registry currently maps the rev0176 object families and records audit findings for the full schema/fixture layer. Future revisions should expand the registry backward across high-reliance families before adding another large wave of schemas.

## Audit levels

| Level | Meaning | Reliance effect |
|---|---|---|
| `COV0` | JSON parses only | no reliance |
| `COV1` | schema/example pair validates | local reliance only |
| `COV2` | family has owner surface and domain map | ordinary filing reliance |
| `COV3` | family has mapped negative fixtures and failure effects | verifier reliance |
| `COV4` | family is crosswalked to release gates, remedies, appeals, and field operations | live-effect reliance |
| `COV5` | family is statistically monitored for drift, gaming, and stale coverage | scaled operational reliance |

rev0176 brings the new labor object families to `COV3` and creates the path for legacy families to move beyond pairwise validation.

## Refactor rule

No new schema family should be admitted unless it has at least one worked example, one owner surface, one domain tag, one lifecycle tag, one privacy/default-seal statement, one reliance effect, and either a negative fixture or a written reason why a fixture is deferred.

This rule is deliberately boring. It prevents a rights archive from becoming a box of persuasive but unmapped artifacts.

