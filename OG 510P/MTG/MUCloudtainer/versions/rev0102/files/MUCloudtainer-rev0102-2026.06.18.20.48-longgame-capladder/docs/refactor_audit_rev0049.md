# rev0049 refactor/audit

Refactor added:

```text
src/muc5/terminal_clean.py
```

This separates terminal-clean scoring/audit labels from one-off rescue scripts.
The helper is small by design: it annotates rows, summarizes truncation/terminal
status, and produces seat-symmetric truncation summaries by strategy.

The revision also adds:

```text
terminal_clean_yield_ranker_bundles(...)
```

in `strategy_sets.py`, so future scripts can reuse the rev0049-style terminal
clean yield-ranker panel without copy-pasting strategy definitions.
