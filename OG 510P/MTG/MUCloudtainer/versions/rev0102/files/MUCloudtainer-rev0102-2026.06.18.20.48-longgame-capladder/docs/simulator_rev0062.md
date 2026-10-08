# rev0062 simulator note

No gameplay semantics changed in rev0062.

The revision adds a legal-size experiment/control layer around existing simulator behavior. The simulator still permits only 40-card and 60-card MUC-5 decks. The new scaling helper exists to build 40/60 controls from existing seed decks; it does not alter `DeckVector.validate()` or the legal deck-size universe.

Validation summary:

```text
pytest: 203 passed
smoke: passed
inherited audit: passed, 176 checks
live artifact audit: passed
buffer-sweep gate: passed
C++ chosen transitions: 39,887
C++ mismatches/skips: 0 / 0
replay samples: 12 / 12 passed
truncations: 0
```

Decision-count reporting remains on the corrected rev0060 contract: `decisions` and `applied_decisions` mean applied choices. The forensic validator still accepts legacy terminal rows that overcounted terminal decisions by one.
