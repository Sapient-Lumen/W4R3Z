# Self-referential audit correction — rev0073

## Defect

The first revision of `tools/audit_rev0073_research_boundary.py` walked every text file in the cube, then wrote its inventory and summary back into that same tree. On a later run, it scanned those generated files as if they were source evidence.

The generated CSV and JSON repeat one label per inventory row, while the generated summary repeats each label once. As a result, rerunning the audit could increase its own totals without any historical source file changing. The tool still returned `pass`, so this was a silent measurement-corruption defect.

Observed contaminated state after a rerun:

```text
files reported with legacy readiness language: 325
inventory rows: 341
term totals: 22 / 39 / 1,834
```

## Correction

The audit now excludes only its instrumentation and generated outputs:

```text
data/rev0073_submission_language_inventory.csv
data/rev0073_submission_language_inventory.json
data/rev0073_u123_duplicate_semantics.csv
data/rev0073_u123_duplicate_semantics.json
data/rev0073_research_boundary_summary.json
tools/audit_rev0073_research_boundary.py
```

Historical cube evidence remains in scope. The write path now recomputes the inventory after generating its outputs and fails if the second result differs from the first.

Corrected result:

```text
files with historical readiness language: 321
inventory rows: 329
term totals: 4 / 11 / 1,178
idempotence verified: true
```

Two full write runs produced byte-identical inventory CSV, inventory JSON, and summary JSON hashes.

## Why it matters

Self-measuring tools must distinguish source material from their own reports. Otherwise an append-only cube can manufacture apparent growth from observation alone. The same rule should be applied to future inventories, duplicate scans, queue summaries, and package metrics: define generated-output exclusions narrowly, expose them in machine-readable output, and verify rerun idempotence.
