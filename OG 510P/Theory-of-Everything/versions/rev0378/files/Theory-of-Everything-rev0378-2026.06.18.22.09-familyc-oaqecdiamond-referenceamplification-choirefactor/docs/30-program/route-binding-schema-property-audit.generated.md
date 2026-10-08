# Route / binding schema property audit (generated)

Generated from `schemas/candidate-route-state-ledger.schema.json` and `schemas/claim-route-binding-ledger.schema.json`. Do not edit directly; run `make index` after changing route or binding schemas.

- Candidate-route required fields: `184`
- Candidate-route required fields missing property declarations: `0`
- Claim-route binding required fields: `169`
- Claim-route binding required fields missing property declarations: `0`

## Rule

Required row fields should also have schema property declarations. Missing property declarations indicate that row shape is enforced only by name, leaving type and property-envelope drift harder to audit.
