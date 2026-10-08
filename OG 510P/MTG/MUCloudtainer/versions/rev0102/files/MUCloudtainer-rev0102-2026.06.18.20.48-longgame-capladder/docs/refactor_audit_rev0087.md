# rev0087 refactor audit

## Refactor

The candidate-transfer decision logic is now centralized in `population_candidate_gate.py` rather than being encoded in prose across rev0084–rev0086 summaries.

## Why it matters

The project's usual failure mode is not lack of commentary; it is letting a local result become eligible evidence through a side door. The new gate makes the exclusion executable:

- reads the paired-delta panel;
- recomputes score-transfer and same-score mechanism-drift components;
- audits pool flags in source game rows;
- emits a single status and hard-fail reasons.

## Ballast control

rev0087 does not ship new raw games, transition traces, or replay logs. It ships compact gate rows only.
