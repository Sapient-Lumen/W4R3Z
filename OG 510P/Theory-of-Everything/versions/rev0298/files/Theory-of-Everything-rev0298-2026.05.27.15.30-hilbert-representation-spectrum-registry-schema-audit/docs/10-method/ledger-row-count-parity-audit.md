# Ledger row-count parity audit

The route-support stack is now large enough that missing route rows can hide inside otherwise-valid JSON ledgers. The generated audit `docs/30-program/ledger-row-count-parity-audit.generated.md` checks route-local-plus-wrapper families for row-count parity.

For each registered family with `cardinality_policy = route-local-plus-wrapper`, the expected count per ledger is:

```text
number of route rows + 1 metadata/provenance wrapper row
```

The audit is not evidence. It is a restart-integrity surface: it makes missing wrapper rows, missing route rows, and uneven ledger counts visible before they become hidden authority gaps.
