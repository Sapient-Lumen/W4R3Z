# rev0062 refactor and audit note

## Refactor

Added `src/muc5/library_buffer_sweep.py` to move legal-size buffer controls out of one-off script logic. The module now owns:

```text
LibraryBufferArm
all_island_deck()
scale_deck_to_legal_size()
rev0062_library_buffer_arms()
library_buffer_specs()
annotate_library_buffer_rows()
library_buffer_summary_rows()
library_buffer_mechanism_rows()
compare_library_buffer_by_life()
compare_forensic_library_buffer_by_life()
library_buffer_gate_report()
```

This keeps the revision script mostly orchestration and makes later threat-closure panels reusable.

## Deck-scaling audit

The scaled controls are deterministic largest-remainder legal-size analogues, not new deck-construction doctrine.

Current scaled decks:

```text
counter60 seed:  (60, 31, 16, 7, 5, 1)
counter40 ctrl:  (40, 21, 10, 5, 3, 1)

threat40 seed:   (40, 21, 7, 4, 2, 6)
threat60 ctrl:   (60, 32, 10, 6, 3, 9)
```

Positive card categories are preserved so a singleton Overlord shell does not become an illegal or degenerate no-win-condition analogue solely through rounding.

## Evidence retention

rev0062 generated 39,887 C++ chosen-transition rows for parity checking but ships only a 240-row compact sample. Full raw transition CSVs remain intentionally excluded from the linked revision.

## Tests

`tests/test_rev0062_library_buffer_sweep.py` covers deck scaling, arm/spec construction, comparison deltas, forensic comparison deltas, and gate behavior.
