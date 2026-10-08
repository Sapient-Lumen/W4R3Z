# Rev280: expose a boot-stdlib change-impact map next to reverse users

Rev279 made reverse stdlib usage machine-readable, but there was still one small
manual step between “who depends on this word?” and “what should I rerun after
changing it?”

This rev keeps the follow-up tiny: reuse the same parsed `core.mx` dependency
edges plus the existing portability manifest, and let `mxportable` name a small
impact set directly.

## What changed

- `boot_stdlib_word_specs()` in `src/micromax/portability_suite.py` now also
  records, for each boot-stdlib word:
  - `impact_words`
  - `impact_word_count`
- `selected_boot_stdlib_word_inventory(...)` now also records:
  - `impact_case_names`
  - `impact_case_count`
- `tools/mxportable.py --stdlib-manifest` now accepts `--show-impact`
  - human mode prints impacted boot-stdlib words and portability case names
  - JSON mode keeps the same `source_inventory` payload, now with impact rows

## Example commands

```bash
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word keep --show-impact
PYTHONPATH=src python tools/mxportable.py --stdlib-manifest --word ensure --show-source --show-impact --json
```

## Why this matters

Rev275–rev279 already made it easy to answer:

1. which portability cases cover a word,
2. where the word lives in `core.mx`,
3. what it directly/transitively depends on, and
4. which higher-level boot words use it.

The missing operational question was the next one:

> after changing this word, what is the smallest honest retest set?

This rev answers that without pretending Micromax needs a richer dependency
engine or a smarter test scheduler. It only joins two tiny things the repo
already knows:

- source-derived boot-stdlib dependency edges, and
- explicit manifest case names.

That means future Python/Rust/WASM hosts and future LLMs can now jump straight
from a changed boot word to a small list of impacted boot words and portability
cases, instead of manually joining the reverse-user view against the manifest.
