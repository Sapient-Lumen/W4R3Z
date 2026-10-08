# Truth-surface register

`python scripts/truth-surface-register.py --pretty` summarizes the latest known heads for GlassTTY's core truth surfaces.

## Why this exists

By rev0125, GlassTTY had multiple useful frozen surfaces:

- readiness reports,
- control-plane reports,
- install receipts,
- support-surface snapshots,
- and operator handoff bundles.

That was good, but it still left one subtle failure mode: a packaged archive could carry a frozen `latest` bundle whose payload still points at an older archive root.

The truth-surface register makes that drift visible by distinguishing:

- the latest **operational head** for each surface,
- the latest **current-root** head,
- and the latest **citation-ready** head when the family-specific cleanliness checks pass.

## Family-specific rules

- support-surface snapshots need a clean support-record contract to count as citation-ready;
- operator handoff bundles need zero missing required artifacts to count as citation-ready;
- opening-surface conformance needs the declared opening reads/commands to match the actual startup doc;
- readiness, control-plane, and install surfaces are still citable when they report blockers, but only when the capture belongs to the current archive root.

## Commands

```bash
python scripts/truth-surface-register.py --pretty
python scripts/truth-surface-register.py capture --output-dir validation/latest/truth-surface-register
```
