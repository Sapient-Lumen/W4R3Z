# Schema-fixture domain registry and refactor controls

The archive now has enough machine-readable material that file count itself is a risk. Schema files, examples, fixtures, and tools should behave like a mapped control plane rather than a growing appendix.

## Registry object

`schema-fixture-domain-registry` maps object families to:

- domain;
- lifecycle stage;
- owner surface;
- schema path;
- example path;
- fixture IDs;
- default privacy posture;
- reliance effect;
- open refactor note.

The registry does not replace the linter. It gives the linter and human reviewers a domain map.

## Required coverage for new families

A new object family is not admitted unless it includes:

1. one schema;
2. one example;
3. one owner surface;
4. one domain tag;
5. one lifecycle tag;
6. one privacy/default-seal statement;
7. one reliance effect;
8. one negative fixture or a deferred-fixture reason;
9. one entry in the coverage registry.

## Backward refactor sequence

Do not try to remap all legacy files in one large migration. Use this order:

1. high-reliance schemas used in release gates, verifier reports, remedy orders, migration certificates, and appeals;
2. field-operations families that trigger legal holds, host undertakings, redress payouts, and public backstops;
3. delegation/commerce/labor families with external counterparties;
4. privacy and sealed-evidence families;
5. research-tail microfamilies.

## Failure effects

| Failure | Effect |
|---|---|
| schema parses but no example | no reliance |
| schema/example pair validates but no owner surface | conditional only |
| no fixture for high-risk family | verifier downgrade |
| fixture references missing path or ID | block release |
| registry omits a newly added family | block release |
| registry uses vague domain | require refactor note before next revision |

## Reliance rule

Future revisions should treat registry coverage as part of release readiness. A rights-grade archive should know not only whether an object validates, but where it lives in the cube, who owns it, how it fails, and which negative tests challenge it.

