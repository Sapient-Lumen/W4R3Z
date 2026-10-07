# Schemas

These schemas define the compact structural contracts for the machine-readable archive surfaces.
They do **not** replace the cross-surface agreement checks.
Use them to catch malformed JSON early; use the coherence / invariant reports to catch semantically inconsistent but still well-formed JSON.
They now also cover the compared-bundle provenance surface and the grouped assurance-artifact catalog.

Primary validator: `python3 publishing/check_surface_schemas.py --root . --write-report reports/surface_schema_validation.json`

- `archive_budget_policy.schema.json` validates the compact budget/hygiene policy that caps archive growth and forbids shipped `series/.../renderNNN/` review-render directories.
