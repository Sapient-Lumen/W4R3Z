# rev0074 population raw-lineage audit

rev0074 targets the next brittle point after rev0073: the population gate was now exact, but it still trusted inherited arm-summary CSVs as the source of truth.  A stale or edited summary row could silently change the security conclusion while the raw game rows disagreed.

The new runner reads the raw rev0069 and rev0070 population game files, adds an archive-global `source_qualified_game_id`, recomputes all 72 source-revision arm summaries, and compares those summaries back to the shipped rev0069/rev0070 arm-summary tables.

Primary artifacts:

```text
scripts/run_rev0074_population_lineage_audit.py
src/muc5/population_lineage.py
data/rev0074_population_lineage_audit_summary.json
data/rev0074_population_lineage_index.csv
data/rev0074_population_raw_recomputed_arm_summary.csv
data/rev0074_population_raw_fine_security.csv
data/rev0074_population_raw_fine_gate.csv
```

## Results

```text
raw games:                         432
lineage index rows:                432
recomputed arm summaries:           72
source summary rows:                72
summary mismatch rows:               0
seed duplicates:                     0
transition seed duplicates:          0
agent seed duplicates:               0
local cpp_shadow_game_id duplicates: 1
source-qualified game duplicates:    0
truncations:                         0
non-terminal clean rows:             0
seat/start-player balance groups:   72
imbalanced groups:                   0
```

The one local `cpp_shadow_game_id` collision is not a simulator error; it is a lineage-key error.  rev0069 and rev0070 each number their local C++ shadow rows from the beginning of the run, so a bare local id cannot serve as an archive-global primary key.  The new key format is:

```text
source_revision:cpp_shadow_game_id
```

Example:

```text
rev0069:g00000_A_legacy_vs_closure_counter40_vs_threat40_life20_seat0_sp0_r0
rev0070:g00000_A_legacy_vs_closure_counter40_vs_threat40_life20_seat0_sp0_r0
```

These are distinct source-qualified games and have distinct seeds.

## Fine-stratum guard

The raw audit also recomputes a fine-grained `source_revision × size_axis × starting_life` security surface.  That produces 12 complete population cells, but each fine cell is intentionally treated as underpowered under the promotion rule because rev0069 contributes 4 games per arm and rev0070 contributes 8 games per arm at this granularity.

```text
fine cells:                  12
complete fine cells:         12
gate-passed fine cells:       0
underpowered fine cells:     12
best point floor:          0.75
best conservative LCB:     0.07094924212969023
```

This is the useful caution: some tiny strata have high point floors, but the raw evidence is far too thin to promote them.  rev0074 therefore preserves the rev0073 quarantine while showing exactly which raw rows produced the summaries.

## Scientific read

The quarantine conclusion is stronger because it no longer depends only on derived summary tables.  The raw games are seed-disjoint, balanced by seat and starting player, terminal-clean, truncation-free, and exactly reproduce the inherited arm summaries.  The remaining risk is strategic, not lineage: generate a new row policy against the weak fine strata or deliberately spend new games on the high-point underpowered strata before interpreting them.
