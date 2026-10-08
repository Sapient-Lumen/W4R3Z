# Exact digest recovery and ZIP-container hardening — rev0868

## Material byte recovery

The surviving v242 demo report records this credential identity:

```text
sha256:28e4012b5e0d1d34e1ad1222e19ff35ffb6383ba89bdb9e7a4720bd31247829b
```

The indexed `credential_digest.txt` is 72 bytes. The report value plus one LF is
exactly 72 bytes and hashes to the canonical index value
`9027fea3c23dae8180fda581b02836c4f081a730ab2955346b9522d8c9c97ac8`.
rev0868 therefore restores that exact file at its canonical path. This is a
hash-proved reconstruction, not a guessed payload.

At-path exact coverage rises from 100 to **101 files** and from 4,885,267 to
**4,885,339 bytes**. Exact source files rise from 13 to **14**. Including the 16
existing recovery objects, **117 files / 4,973,440 bytes** are now rehydratable;
4,469 files remain unavailable.

## Severe archive-boundary defect corrected

The prior integrity gate begins after extraction. It can prove the extracted
file set, but it cannot prove that the source ZIP was unambiguous. A ZIP may
carry duplicate names, case or Unicode aliases, traversal paths, symlink or
special-file modes, local/central header disagreement, overlapping data ranges,
or extreme compression before an extracted-tree validator gets control.
Different extractors can materialize different trees from such a container.

rev0868 adds two executable controls:

- `scripts/validate_zip_container.py` validates the ZIP before extraction,
  rejects ambiguous or unsafe member structure, streams every member through
  CRC/decompression, and binds archived payload bytes to the embedded overlay
  manifest.
- `scripts/build_deterministic_zip.py` refuses symlinks and special files,
  normalizes member order, timestamps, modes, names, and comments, validates the
  temporary ZIP, pins the published filesystem mode to `0644`, and publishes it atomically outside the source tree.

The targeted validator exercises safe input plus duplicate-name, traversal,
case-collision, symlink, local/central-header disagreement, prefixed-byte, and
trailing-byte fixtures. It also builds the same miniature bundle twice, requires
byte-identical ZIP output, and proves the default builder preserves an occupied
output rather than clobber it.

## Boundaries that did not change

Publication remains blocked because no owner-approved root license or notice is
present. Component conclusions remain `NOASSERTION`. All 17 selected StreamFold
payloads, including the four-file minimum set, remain absent. The recovered
digest file does not recover the corresponding credential, receipt, output, or
private signing material.
