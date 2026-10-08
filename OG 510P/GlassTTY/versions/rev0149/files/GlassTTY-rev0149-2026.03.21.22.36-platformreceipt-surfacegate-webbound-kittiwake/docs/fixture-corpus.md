# Fixture corpus

GlassTTY carries a deterministic sample corpus under `fixtures/corpus/`.

Why it exists:
- gives future sessions concrete evidence even without a live browser
- exercises fixture indexing and comparison tools
- keeps the project generic while still carrying a Claude-shaped example

Tools:
- `./scripts/seed-fixture-corpus.py [DIR] --force` writes or refreshes the sample corpus
- `./scripts/index-fixtures.py [DIR]` summarizes saved fixtures
- `./scripts/compare-fixtures.py LEFT RIGHT` reports length and selector-hint deltas
- `./scripts/plan-fixture.py FIXTURE.json` turns one saved fixture into a write/read/submit playbook with normalized steps, ranked locator strategies, and assertion hints
- `python -m glassttyd.cli seed-fixture-corpus ...`, `index-fixtures`, `compare-fixtures`, `plan-fixture`, and `native-message-budget` expose the same flows from the CLI

Offscreen HTML tools:
- `python -m glassttyd.cli offscreen-dom FILE.html --base-url ...` returns a browser-native DOM summary from the hidden offscreen document
- `python -m glassttyd.cli offscreen-fixture FILE.html --base-url ...` returns a generic fixture-like capture, which gives future sessions a way to compare saved HTML against visible-tab fixture captures once a live extension session is available

## Budget checks

Rich fixture captures eventually have to cross Chromium native messaging. Before promoting a fixture-shape change, run:

```bash
python scripts/native-message-budget.py fixtures/corpus --pretty
```

That keeps the archive honest about whether richer capture metadata still fits the live bridge budget.
