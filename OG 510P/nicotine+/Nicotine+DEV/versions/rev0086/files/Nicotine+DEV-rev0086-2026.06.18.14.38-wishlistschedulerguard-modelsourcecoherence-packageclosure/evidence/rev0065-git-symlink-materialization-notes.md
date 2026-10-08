# Git symlink materialization notes — rev0065

The Git tree comparison initially surfaced ten blob mismatches. All ten were Git mode `120000` entries, meaning the Git object stores symlink target text. In the uploaded source bundle these paths appear as regular materialized file contents rather than symlink entries.

rev0065 therefore records these rows separately in:

```text
data/rev0065_git_symlink_materialization.csv/json
```

This is a source-bundle packaging-shape exception, not strict/front packet drift:

```text
materialized symlink rows: 10
non-symlink mismatches: 0
missing tracked files: 0
extra source files: 0
strict/front touched files exact Git blob matches: 15/15
```

Affected paths are packaging/license helper paths only; none are the strict/front touched files:

```text
pynicotine/downloads.py
pynicotine/transfers.py
pynicotine/slskproto.py
pynicotine/search.py
pynicotine/slskmessages.py
```
