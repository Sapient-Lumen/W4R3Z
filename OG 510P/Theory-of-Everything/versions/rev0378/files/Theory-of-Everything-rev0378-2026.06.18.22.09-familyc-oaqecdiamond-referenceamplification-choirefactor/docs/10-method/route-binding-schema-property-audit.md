# Route / binding schema property audit

This audit checks a schema-maintenance seam: required route-support fields must be declared as schema properties, not only listed in `required`.

Generated surface:

`docs/30-program/route-binding-schema-property-audit.generated.md`

The audit is not a scientific authority source. It prevents future route-support fields from being required by name while lacking a property envelope in the candidate-route or claim-route binding schemas.
