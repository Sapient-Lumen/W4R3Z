
# Schema registry audit

Rev0021 adds a non-destructive schema registry audit. It parses JSON surfaces, records their top-level shape, identifies primary row arrays when possible, and assigns a heuristic schema candidate where one is visible.

This is not full schema enforcement. It is the map needed before full schema enforcement.

Counts recorded in the release:

- JSON surfaces audited before final hash manifest: 479
- Schema files observed before adding rev0021 schemas: 150
- JSON parse errors: 0
- Root surfaces mapped for alias readiness: 174
