# Patched full-source-tree compile gate — rev0070

## Purpose

rev0070 continues the strict/front filing-preflight line without opening a new private packet. The immediate question is whether the selected archived-source split patch stack remains syntactically coherent beyond the five files edited by the patches.

rev0069 compiled and AST-checked the five strict/front touched files. rev0070 extracts each archived source lane from the uploaded `Nicotine-source(1).zip`, applies the four rev0059 split filing-bundle patches, and compiles **every Python file** in the patched tree with Python's `compile()` function. This gives a no-import, no-bytecode, full-tree syntax gate.

## Inputs

```text
source bundle: /mnt/data/Nicotine-source(1).zip
expected source SHA256: feaa8df98bbd0f28ba00eb8d52dcc3b9b9860e8d59039c7d41a98a0117505e5b
source lanes:
  - github-tag-3.3.10
  - github-branch-3.3.x
  - github-branch-master
patch source: handoff/rev0059/patches/<lane>/*.patch
```

## Results

```text
source lanes: 3/3 pass
patch apply rows: 12/12 pass
full-tree compile rows: 439/439 pass
critical touched-file hashes: 15/15 pass
negative controls: 5/5 pass
package hygiene: 5/5 pass
```

The full-tree compile rows are split by lane as follows:

```text
github-tag-3.3.10:    142 Python files compiled
github-branch-3.3.x:  145 Python files compiled
github-branch-master: 152 Python files compiled
```

The gate also crosschecks the five strict/front touched files against the inherited rev0059 patched-file ledger:

```text
pynicotine/downloads.py
pynicotine/transfers.py
pynicotine/slskproto.py
pynicotine/search.py
pynicotine/slskmessages.py
```

## What this proves

This proves that the selected archived-source patch stack does not introduce Python syntax errors in the whole extracted source tree, not just in the edited files. It also binds the resulting five touched files back to the earlier split-patch attribution ledger.

## What this does not prove

This does not import Nicotine+, exercise GTK/runtime dependencies, or replace the separate fresh-current checkout/tarball requirement before live-current external filing. It is an archived-source static compile layer only.
