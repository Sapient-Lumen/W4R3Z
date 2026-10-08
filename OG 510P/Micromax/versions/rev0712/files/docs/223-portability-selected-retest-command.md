# Rev281: expose exact retest commands for selected boot-stdlib impact slices

Rev280 made change impact machine-readable, but there was still one tiny manual
step left between “which portability cases are affected?” and “rerun exactly
those cases now.”

This rev keeps the follow-up intentionally small: reuse the already-selected
impact case names, and let the shared inventory plus `mxportable` emit one exact
copy-pasteable replay command.

## What changed

- `src/micromax/portability_suite.py` now also provides:
  - `portability_case_name_args(...)`
  - `portability_retest_command(...)`
  - `stdlib_impact_summary(...)`
- `selected_boot_stdlib_word_inventory(...)` now also adds top-level:
  - `impact_summary.impact_words`
  - `impact_summary.impact_word_count`
  - `impact_summary.impact_case_names`
  - `impact_summary.impact_case_count`
  - `impact_summary.retest_command`
  - `impact_summary.retest_json_command`
- `tools/mxportable.py --stdlib-manifest --show-impact`
  - human mode now prints a combined `Selected impact summary`
  - JSON mode now carries the same `impact_summary` payload

## Example commands

```bash
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word keep --show-impact
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word keep --word ensure --show-impact --json
```

Typical combined replay output now looks like this:

```bash
PYTHONPATH=src python tools/mxportable.py --name stdlib-keep --name stdlib-bi --name stdlib-tri
```

## Why this matters

Rev275–rev280 already made it easy to answer:

1. which portability cases cover a word,
2. where the word lives in `core.mx`,
3. what it directly/transitively depends on,
4. which higher-level boot words use it, and
5. which words/cases are impacted by a change.

The missing operational question was the last mile:

> what exact command should I run for this selected impacted slice?

This rev answers that without pretending Micromax needs a richer test runner,
pytest plugin, or dependency scheduler. It only turns already-explicit case
names into the exact `--name ...` command line Micromax already understands.

That means future Python/Rust/WASM hosts and future LLMs can now go straight
from a changed boot word—or a small selected set of changed words—to one
copy-pasteable portability replay command instead of reconstructing the exact
`mxportable` invocation by hand.
