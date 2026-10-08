# Opening contract

`OPENING-CONTRACT.json` is the machine-readable answer to a small but important question: **what should a cold-start operator read and run before they start changing GlassTTY or speaking more strongly about support?**

## Why this exists

GlassTTY now has enough canon, enough validation history, and enough truth surfaces that a future session could easily reopen the repo in the wrong order and form a misleading picture from old handoff notes or stale captures.

The opening contract fixes that by naming:

- the minimum required reads,
- the minimum required commands,
- and the doctrine that cold-open truth should be **checkable**, not just written in prose.

## Commands

```bash
python scripts/check-opening-contract.py --pretty
python scripts/check-opening-contract.py write-root
python scripts/check-opening-contract.py capture --output-dir validation/latest/opening-surface-capture
```

## Working rule

Before widening support claims or starting a new runtime theory, first verify that the repo's declared wake-up path still matches the files and commands that actually exist.


rev0130 extends the cold-open path with `SUPPORT-PUBLISH-GATE.json` and `python scripts/support-publish-gate.py --pretty` so future sessions can tell whether held support bundles are blocked by manifest problems, missing direct evidence, or stale publication heads before they strengthen any support claim.

rev0131 extends the cold-open path with `SUPPORT-SOURCE-LOCK.json`, `SUPPORT-SOURCE-BASELINE.json`, and `python scripts/support-source-baseline.py --pretty` so future sessions can inspect the approved authority basis behind support claims before they rely on the publish gate alone.
