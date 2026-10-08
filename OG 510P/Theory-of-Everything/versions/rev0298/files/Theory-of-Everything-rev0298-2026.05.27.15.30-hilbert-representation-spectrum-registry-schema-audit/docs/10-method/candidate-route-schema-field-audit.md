# Candidate-route schema field audit

The route ledger has grown many registered route-support fields. This audit makes sure `schemas/candidate-route-state-ledger.schema.json` does not silently lag behind `LEDGER-FAMILY-REGISTRY.json`.

The generated audit reports whether every registered `route_fields` entry appears in the route-row `required` list of the candidate-route schema. A missing field is a restart and validation risk: the route row may carry an authority handle that the schema does not require.
