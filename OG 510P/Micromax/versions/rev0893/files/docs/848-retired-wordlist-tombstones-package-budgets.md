# Retired wordlist tombstones and package fingerprint budgets (rev0890)

## Why this mattered

Rev0889 closed the rollback leak where failed plugin definitions could leave dictionary-keyed word-authority rows behind.  Its largest remaining concrete runtime finding was successful reload/unload retention: old committed plugin wordlists stayed in the VM as executable `Word` objects for historical inspection.  A long reload session could therefore keep every prior generation alive and make future dictionary snapshots larger.

Rev0890 turns that finding into a runtime fix rather than another registry or doctrine layer.

## Runtime change

`PluginManager` now retires a committed plugin wordlist on successful reload or unload:

1. collect compact metadata from the old wordlist;
2. append a bounded `PluginWordlistTombstone` row;
3. remove the old wordlist from `vm.wordlists`, `vm.wordlist_names`, and search order;
4. scrub editor `_word_authority` rows for the retired wordlist;
5. mark the retired `Word` objects so direct saved execution tokens fail clearly if invoked later;
6. touch the VM dictionary only when a live dictionary row was actually removed.

The tombstone keeps plugin name, root, wordlist id, generation, group, reason, word count, sorted word names, source spans when available, package digest, and package file count.  It intentionally stores names and spans rather than `Word` objects, so the diagnostic ledger does not simply move the old executable retention somewhere else.

`plugin info NAME` now reports retired-wordlist count and compacted word count when rows exist.

## Package approval budget

Restricted manual plugin grants compute a package fingerprint so a later helper-file edit makes the grant stale.  That scan previously had no explicit file-count or total-byte ceiling.  Rev0890 adds host-owned budgets:

- `PLUGIN_PACKAGE_MAX_FILES = 512`
- `PLUGIN_PACKAGE_MAX_TOTAL_BYTES = 8 * DEFAULT_PLUGIN_MAX_BYTES`

The manager raises a clear `MicromaxError` before accepting a grant that would require scanning or hashing beyond those limits.  Tests lower the budgets to prove both rejection paths directly.

## Evidence

New focused tests cover:

- repeated successful reloads keeping the live VM wordlist count flat;
- old wordlist ids disappearing from live VM dictionaries, names, search order, and word authority;
- unload retiring the last live plugin wordlist;
- tombstones preserving compact names and counts without retaining executable words;
- a direct saved XT from a retired generation failing with `Retired execution token`;
- package fingerprint rejection for too many files and excessive total bytes.

`mxaudit --check` now guards both the tombstone runtime seam and the package fingerprint budget seam.

## Still not solved

This revision retires dictionary-visible old generations and makes direct saved XTs fail after retirement.  It does not yet prove that callback records, deferred cells, or every resource handle has a perfect stale-generation story.  The next runtime-risk lane should enumerate those remaining reference escape patterns before adding broader revocation behavior.

The broad source/lifecycle transaction still uses `RuntimeRegistrationSnapshot`; rev0890 deliberately attacked the highest measured retention risk first instead of expanding the effect-contract bureaucracy.
