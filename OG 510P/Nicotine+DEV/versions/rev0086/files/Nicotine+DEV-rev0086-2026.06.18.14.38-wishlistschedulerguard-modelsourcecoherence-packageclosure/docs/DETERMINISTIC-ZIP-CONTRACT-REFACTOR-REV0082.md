# Deterministic ZIP contract refactor — rev0082

## Problem

Previous revisions audited the extracted package tree but relied on ad hoc ZIP creation. That left archive-level ambiguity outside the current authority system: duplicate central-directory names, Unicode normalization collisions, case-only collisions, traversal components, symlink entries, host timestamps, file-mode drift, and member-order drift could all make two extractions or two builds behave differently.

## Correction

`data/current_zip_contract.json` is now the package-format authority. `tools/build_current_package.py` and `tools/audit_current_zip.py` enforce:

```text
one top-level directory whose name equals the ZIP stem
one directory entry: the top-level root
lexicographically ordered regular-file members
portable POSIX paths already normalized to NFC
no raw, normalized, or case-folded name collisions
no absolute paths, backslashes, NULs, or parent traversal
no symlinks or special files
fixed 1980-01-01 00:00:00 member timestamps
canonical 0644/0755 file modes and 0755 root mode
DEFLATE level 9 for files; stored root entry
empty ZIP comment and deterministic metadata
```

## Mutation controls

A synthetic package is built twice and compared byte-for-byte. The auditor then rejects four deliberately malformed archives:

```text
duplicate member name
case-folding collision
parent-traversal member
extra directory entry
```

The final full-package gate exposed two defects that the original synthetic fixture did not cover:

1. The auditor retained the raw `bytes` value of the ZIP comment in a diagnostic row, so its command-line JSON renderer failed after completing otherwise-successful checks. The diagnostic now records a JSON-safe byte count and hexadecimal form, and the self-test serializes the complete audit result.
2. The builder sorted `Path` objects component-wise, while the contract and auditor require lexicographic POSIX member names. These orderings diverge for prefix cases such as `name.file` and `name/member`. The builder now sorts the final normalized relative-name rows, and the fixture contains an explicit prefix-sensitive case.

These controls close the gap between in-process function testing and the actual full-package release gate.

Result: 10/10 contract checks pass and 4/4 malformed archives are rejected.

The final release ZIP is built twice from the completed manifest-bearing tree, compared by SHA-256, audited against the filesystem, extracted cleanly, and audited again before it is linked.
