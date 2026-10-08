# Truth-surface warnings

`python scripts/truth-surface-warnings.py --pretty` turns the full truth-surface register into a smaller warning queue.

The register answers lineage questions for every family. The warning view answers a narrower operator question:

> which current frozen truth surfaces are stale, foreign-root, or not citation-ready right now?

## Warning kinds

The warning ledger currently surfaces three main families of trouble:

- **foreign-root latest heads** — the newest frozen bundle belongs to some older archive root
- **missing current-root heads** — the family has history, but nothing frozen for the current archive root
- **current-root but not citation-ready** — the family exists for this root, but its cleanliness rule still fails

## Why keep this separate from the full register?

The full register is the right place for lineage detail.
The warning ledger is the right place for fast attention routing, control-plane fusion, and handoff packaging.

## Capture path

Freeze the current warning surface with:

```bash
python scripts/truth-surface-warnings.py capture --output-dir validation/latest/truth-surface-warnings
```
