# Package coherence gate — rev0075

The final package must satisfy all of these conditions:

```text
REVISION.txt is rev0075
current disposition ledger is rev0075 and selects no SEARCH-RESP-01A patch
exact-current search-response probe passes
8/8 classified matrix rows match expected pass/fail tuples
8/8 source invariants pass
baseline and experimental upstream unit counts have parity
historical active test hashes remain intact in docs/archive
status audit is self-reference stable
revision delta inventory exists
all rev0075 Python files compile
no embedded upstream source tree, source ZIP, Git metadata, symlink, or Python/pytest cache
manifest covers every package file except itself with matching SHA-256
```

`tools/audit_rev0075_package.py` is the fail-closed implementation. It must be run before manifest generation with `--allow-missing-manifest`, then again after manifest generation and against an extraction of the final ZIP.
