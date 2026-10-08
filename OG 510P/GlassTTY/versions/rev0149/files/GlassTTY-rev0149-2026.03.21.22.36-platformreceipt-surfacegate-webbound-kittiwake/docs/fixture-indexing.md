# Fixture indexing

GlassTTY fixture capture is more useful when saved fixtures can be summarized quickly.

## Index saved fixtures

```bash
./scripts/index-fixtures.py fixtures --pretty
./scripts/index-fixtures.py "$GLASSTTY_HOME/fixtures" --pretty
python -m glassttyd.cli index-fixtures fixtures --pretty
```

The script scans JSON fixture envelopes and extracts:
- adapter
- title
- URL
- prompt/latest/selection lengths
- top input and output selector hints

## Compare fixtures

```bash
./scripts/compare-fixtures.py LEFT RIGHT --pretty
python -m glassttyd.cli compare-fixtures LEFT RIGHT --pretty
```

Use comparison before changing adapter heuristics. It surfaces whether prompt or output length shifted and whether the top selector hints drifted.


## Plan interactions

```bash
./scripts/plan-fixture.py FIXTURE.json --pretty
python -m glassttyd.cli plan-fixture FIXTURE.json --pretty
```

The planner turns a saved fixture into a generic interaction playbook:
- preferred write/read/submit targets
- normalized planner steps with stable step IDs and value kinds
- role/label/placeholder-first Playwright locator hints plus ranked fallback strategies
- assertion hints and warnings about disabled, readonly, invalid, required, multiple, or grouped controls

Use it before promoting any selector into adapter code. It is deliberately user-facing and locator-first, not CSS-first.
