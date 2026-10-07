# Thin-Core Operating Mode — rev0104

The cube should now prefer completion over mirror production.

## Canonical current core

- `Candidate-Ledger-current.*`
- `Claim-Ledger-current.*`
- `Source-Registry-current.*`
- `Evidence-Debt-current.*`
- `META/Evidence-Task-Ledger-current.*`
- `Office-Card-Index-current.*` and `OFFICE-CARDS/`
- `Longform-Registry-current.*` and `LONGFORM/`
- governance ledgers needed for authority, permission state, takedown, and review boundaries

## Generated or historical surfaces

Report families that only restate canonical data should be generated on demand, not treated as permanent current truth. Rev0104 starts this by moving the evidence-debt execution queue / work packet / work order / trace family to history.

## Working rule

A file earns current status only if it helps a human reviewer make a bounded decision, preserves a necessary boundary, or delivers readable synthesis. Otherwise it belongs in history, a generated-view cache, or deletion review.
