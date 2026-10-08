# rev0051 refactor/audit notes

New module:

```text
src/muc5/terminal_deep.py
```

It isolates focused deep-claim utilities from the broader terminal-meta code:

```text
strategy_ids_from_claims(...)
targeted_strategy_pair_specs(...)
annotate_focus_rows(...)
deep_target_summary_rows(...)
deep_pair_rows(...)
deep_claim_gate(...)
```

This separation matters because `terminal_meta.py` should remain the population-table layer, while `terminal_deep.py` is an agenda-following layer for spending extra repetitions on selected strategies.

Audit additions check:

```text
312 focused games
3 target strategies
48 target-pair rows
0 truncations
promotion/statistical/meta/deep gates pass
C++ shadow mismatch count = 0
C++ skipped transition count = 0
replay trace C++ mismatch count = 0
required rev0051 docs/scripts/tests/data are present
```

No card rules, legal action semantics, or agent interfaces changed in this revision.
