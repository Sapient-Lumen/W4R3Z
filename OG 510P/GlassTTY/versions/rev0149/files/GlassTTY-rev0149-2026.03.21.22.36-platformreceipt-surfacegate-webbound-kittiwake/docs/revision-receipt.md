# Revision receipt

`REVISION-RECEIPT.json` is the archive's compact self-description for the current packaged revision.

It exists because three different truths kept drifting apart across nearby GlassTTY revisions:

- the archive name and manifest identity,
- the actual current-root truth-surface counts,
- and the human explanation of what this revision intentionally changed.

The receipt is meant to be small and explicit:

- which archive this is,
- what previous archive it builds on,
- which imported patterns were actually carried in from comparison datacubes,
- which top-level canon files a future operator should read first,
- which new files define the change,
- and what the current truth-surface register says right now.

## Companion conformance file

`REVISION-RECEIPT-CONFORMANCE.json` is the machine-checked answer to a narrower question:

> does `REVISION-RECEIPT.json` still match the packaged archive identity and the current truth-surface register?

Refresh it with:

```bash
python scripts/check-revision-receipt.py write-root
```

Inspect it with:

```bash
python scripts/check-revision-receipt.py --pretty
```

## Why this matters

A future operator should not have to infer the current revision's intended move only from changelog prose, handoff notes, or the zip filename. The revision receipt keeps the archive's self-description visible and machine-checkable.
