# Refactor audit — rev0070

Substantive refactors in this revision:

1. `population_cells_from_summary_rows` now treats present-but-empty rows as incomplete when the score is missing, non-finite, or has zero games. This closes a semantic-completeness gap where a row could exist without usable evidence.
2. `population_precision_gate_rows` adds a conservative lower-bound gate over the complete empirical-game matrix. It reports underpowered, imprecise, low-floor, and candidate-promotable states separately.
3. `evidence_index` now distinguishes active references from historical generated-data mentions, preventing old audit summaries from falsely blocking evidence migration.
4. The rev0070 population runner samples C++ transition parity evenly when full shadowing would dominate runtime, while still reporting the full generated transition count.

Remaining refactor risk: `scripts/audit_cube.py` is still a long chronological audit script. rev0070 adds targeted checks to it but does not yet decompose it into revision-local audit modules.
