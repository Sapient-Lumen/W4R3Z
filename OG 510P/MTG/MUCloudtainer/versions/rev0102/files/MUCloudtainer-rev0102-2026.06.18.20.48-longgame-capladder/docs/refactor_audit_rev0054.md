# Refactor / Audit rev0054

New code:

```text
src/muc5/terminal_matchup_claim.py
scripts/run_rev0054_matchup_claim_dossier.py
tests/test_rev0054_matchup_claim.py
```

The refactor separates concrete-cell claim logic from earlier cell-selection and life-flip modules:

```text
terminal_matchup.py        target/opponent schedule and target-perspective rows
terminal_cell_confirm.py   confluence agenda and confirmation labels
terminal_matchup_claim.py  claim-dossier selection, dimension slices, claim labels, claim gate
```

The audit now checks that rev0054 produced:

- one selected matchup claim agenda row,
- 160 terminal-clean games,
- zero truncations,
- one claim row,
- a life-sensitive or concrete claim candidate,
- clean C++ shadow transitions,
- replay samples that passed,
- required rev0054 docs/scripts/tests/data files.
