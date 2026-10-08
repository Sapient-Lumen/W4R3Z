# Ledger-family order audit

The ledger-family registry is now large enough that ordering drift can create restart confusion. `docs/30-program/ledger-family-order-audit.generated.md` checks that registered families remain ordered by introduced revision and by their owning open-question gates.

The audit is archive-control only. It does not add scientific authority, but it prevents a late family from hiding earlier in the registry, where generated summaries and restart readers can misread the support-stack chronology.
