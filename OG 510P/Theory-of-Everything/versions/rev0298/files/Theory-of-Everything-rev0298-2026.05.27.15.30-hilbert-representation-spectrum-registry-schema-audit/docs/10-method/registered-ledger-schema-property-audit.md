# Registered-ledger schema property audit

This audit checks registered executable ledger schemas against the route-layer registry. A ledger row schema should not list required row fields without declaring property envelopes for those fields.

The audit is generated at `docs/30-program/registered-ledger-schema-property-audit.generated.md` and is lint-enforced. It is not a scientific evidence source; it prevents row-shape drift as the cube grows.
