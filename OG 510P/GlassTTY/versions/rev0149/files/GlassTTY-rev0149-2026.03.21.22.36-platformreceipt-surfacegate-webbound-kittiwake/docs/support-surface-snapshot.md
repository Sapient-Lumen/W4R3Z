# Support surface snapshot

`python scripts/support-surface-snapshot.py --pretty` freezes the current support-truth surface into one machine-readable report.

## Why this exists

GlassTTY’s support truth already lives in `docs/support-records/*.md`, but prose alone is easy to overread. This snapshot turns those records into:

- a normalized per-surface summary
- a flattened `surface × workflow × lane` table
- a review queue sorted by rollout priority and weak workflow tier
- a contract report that catches malformed records before support claims drift

The goal is not to replace support records. The goal is to make the current public support surface inspectable, comparable, and safe to freeze before claims or rollout language change.

## Commands

```bash
python scripts/support-surface-snapshot.py --pretty
python scripts/support-surface-snapshot.py capture --output-dir validation/latest/support-surface-capture
python scripts/support-surface-snapshot.py history --pretty
python scripts/check-support-record-contract.py --pretty
```

## Capture bundle

A capture writes:

- `support-surface.json`
- `record-contract.json`
- `SUMMARY.md`
- `capture-history.json`
- `capture-diff.json`

## Working rule

Before changing support tiers, rollout priorities, or surface claims, freeze the current support surface first. That keeps support truth comparable across revisions instead of letting it silently drift in prose.
