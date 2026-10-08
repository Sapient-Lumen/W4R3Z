# rev0872 — root-substitution closure and canonical path identity

## Result

This revision does **not** claim another guessed recovery. It closes a more urgent correctness defect in the code that reads and materializes the bytes already recovered.

In rev0871, root validation returned an ordinary pathname. A concurrent rename could then move the validated directory away and install a different directory at the same pathname before the next open. The later operation would validate and use the replacement as though it were the original root.

A deterministic reproduction against the exact rev0871 scripts demonstrated both consequences:

- `materialize_exact_bytes()` reported success and wrote `redirected.txt` into the replacement root, while the directory that had actually passed validation received nothing;
- `snapshot_regular_file()` accepted and hashed `decoy bytes\n` from the replacement root instead of `trusted bytes\n` from the directory that had passed validation.

The tested parent scripts are bound by full SHA-256 in the JSON audit. This is a local integrity and redirection defect, not a claim that an external attacker was present.

## Root identity is now retained across the workflow

`scripts/root_anchor.py` introduces one shared `RootAnchor`: an absolute lexical root pathname paired with the device, inode, and file type captured by a component-by-component no-follow directory walk.

Every later root open must satisfy all of the following:

1. the pathname still names the captured device/inode/type before open;
2. the opened descriptor names that same identity;
3. a fresh no-follow lookup still names that identity after open; and
4. the pathname still names the captured root before a read or write operation returns success.

The same anchor is now carried through canonical coverage, external-target index validation, exact-byte materialization, and the rev0870/rev0871 recovery workflows. A target root exchanged between “index matches” and “write” is rejected rather than silently redirected.

The audit also found an early-success hole inside the new refactor: an already-exact target could return before the final root-identity assertion. rev0872 closes both already-exact return sites and includes a swap regression that proves the original and replacement files remain unchanged.

## One spelling per relative path

The inherited cleaners used `PurePosixPath(...).as_posix()` as both validator and normalizer. That silently mapped `./a` to `a`, `a//b` to `a/b`, `a/./b` to `a/b`, and `a/b/` to `a/b`. Accepting multiple textual names for one logical path weakens duplicate detection, manifest comparison, patch review, and audit receipts.

The shared cleaner now requires the supplied spelling to equal its canonical POSIX rendering; it never normalizes an alias into acceptance. The rule is used by:

- exact-byte materialization;
- canonical coverage and recovery inventory reads;
- the overlay gate and extracted-tree integrity validator;
- the overlay-chain patch parser;
- patch-corpus byte recovery; and
- overlay-history recovery.

The ZIP transport validator was already independently strict about canonical member names and remains unchanged.

## Executable regressions

The rev0872 validator exercises four distinct root-exchange points:

1. after materialization root capture but before root open;
2. after an existing exact file is inspected but before the early success return;
3. after coverage root capture but before the file snapshot; and
4. after an external target's canonical index is validated but before materialization.

All four are rejected. The suite also preserves the stable-root happy path, rejects a symlink root alias, verifies all four inherited exact-recovery tools, and checks live representation/recovery totals.

## Validation cannot mutate the validated tree

Finalization exposed one more concrete defect: the modified integrity entrypoint set `sys.dont_write_bytecode` only **after** importing the shared root module. Its first validation run therefore created `scripts/__pycache__/root_anchor...pyc`, immediately making the live file set diverge from the manifest it was checking.

The six affected entrypoints now activate the no-bytecode policy before any local import. The rev0872 validator copies the script set to an isolated sandbox, removes any inherited bytecode-control environment variables, executes nine active entrypoints, and rejects any `__pycache__` directory or `.pyc` file. This makes non-mutation an executable release property rather than a convention.

## Recovery work performed without admitting fiction

The session also rechecked the retained sibling bundles and patch/history evidence for novel exact canonical bytes, tested the adjacent tiny OCF output family only against path-specific full SHA-256 identities, and searched publicly for the distinctive OCF/StreamFold names. No candidate satisfied path, size, and complete digest together, so **zero new bytes were admitted**.

Coverage therefore remains **109 exact current-path files** and **125 rehydratable files / 4,973,641 bytes**. That unchanged number is preferable to manufacturing progress from plausible content.

## Remaining priority

The external-decision and external-byte blockers remain dominant: an owner-approved root/component rights decision, all 17 selected StreamFold payloads, and canonical `README.md`. Further local revisions should continue to require either exact recovered bytes, a demonstrated correctness defect, or direct closure of those blockers.
