# Claim-route controlling-ledger order audit

The controlling-ledger list in a claim-route binding is an authority propagation object. It should not contain duplicate ledger names, unknown files, or unstable order drift that hides which ledgers govern a claim.

The generated audit `docs/30-program/claim-route-controlling-ledger-order-audit.generated.md` checks duplicate and unknown entries for every binding row and records whether list order is stable after de-duplication.
