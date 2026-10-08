# Canonical-index recovery objects — rev0867

This directory makes 16 exact historical canonical versions self-contained.
Before rev0867, those 88,101 bytes existed only implicitly: an operator had to
reverse a long sequence of incremental overlay patches and notice the one state
whose byte count and SHA-256 matched `INDEX/files.csv`.

`inventory.json` binds each canonical path to a content-addressed object under
`objects/sha256/`. The objects are **not** active replacements for the newer
files at those paths. They are recovery material for a separate canonical tree.

Verify history and stored bytes:

```bash
python3 scripts/recover_indexed_versions_from_overlay_history.py --json
```

Safely materialize the 16 versions into a separate tree that contains a
byte-identical `INDEX/files.csv`:

```bash
python3 scripts/recover_indexed_versions_from_overlay_history.py \
  --target-root ../canonical-tree --write --require-present
```

The materializer never writes inside this bundle, never overwrites a
non-matching target, rejects symlink ancestry, and hash-checks every result.
`README.md` remains the sole same-path canonical mismatch for which no exact
state was recovered from the incremental overlay history.
