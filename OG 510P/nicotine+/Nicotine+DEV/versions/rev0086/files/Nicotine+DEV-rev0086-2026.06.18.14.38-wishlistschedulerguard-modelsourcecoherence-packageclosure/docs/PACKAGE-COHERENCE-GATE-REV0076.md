# Package coherence gate — rev0076

The final package must satisfy all of these conditions:

```text
REVISION.txt is rev0076
current disposition ledger is rev0076 and selects no SEARCH-RESP-01B patch
ledger schema and executable validator pass
ledger snapshot equals the current authority
exact-current buddy-search probe passes
26/26 classified matrix rows match expected source-state/test-role outcomes
12/12 source invariants pass
10/10 compile checks pass
baseline and experimental supported units both report 58 passed, 1 skipped, 0 failed
historical active test hash remains intact in docs/archive
active role-classified suite is smaller and has no >100-character lines
revision delta inventory exists
all rev0076 Python files compile
no embedded upstream source tree, unapproved source/archive ZIP, Git metadata, symlink, or Python/pytest cache
manifest covers every package file except itself with matching SHA-256
```

`tools/audit_rev0076_package.py` is the fail-closed implementation. Run it before manifest generation with `--allow-missing-manifest`, then after manifest generation and against a clean extraction of the final ZIP.

Two 211-byte hash-pinned `wrong-source.zip` files are retained as negative-control fixtures from rev0063/rev0064. The package gate allows only those exact paths and hashes; they contain one `not-the-source/README.txt` entry each and are not upstream source bundles.
