# v841 release-builder negative-control fast-fail refactor

**Track:** Shared / Release engineering

Status: synthetic release-gate hardening. This is not election evidence, certification, legal advice, or live-pilot authorization.

## What changed

`build_manifest.py` now separates release-scope discovery from member hashing. It first walks the release tree, rejects unsafe paths, symlinks, special files, and other non-regular governed members, and only then hashes ordinary candidate files.

The previous behavior still failed on unsafe members, but it could discover an unsafe governed member and then continue hashing the rest of the cube before raising the failure. On large revisions that made negative-control probes look like hangs and wasted release-gate time.

## Why this matters

Release gates should fail closed and fail early. A safety check that eventually fails after scanning and hashing the whole archive is easier to interrupt, misdiagnose, or bypass under time pressure. This is especially risky for the filesystem-policy gate because its purpose is to prove that special files, symlinks, and unsafe paths cannot enter the manifest or deterministic ZIP path.

## Verification path

Run:

```bash
python3 scripts/check_release_builder_filesystem_policy.py
python3 scripts/build_manifest.py --check
```

The first check exercises CRLF control-file rejection, symlink rejection, FIFO/special-file rejection, unsafe path rejection, ambiguous source-root rejection, symlink-routed root rejection, source-member swap rejection, and ZIP-output route rejection. The second check proves the checked-in `MANIFEST.sha256` still matches the release tree after the refactor.

## Boundary

This refactor improves release-gate reliability and operator time cost. It does not change packet semantics, source freshness, cryptographic trust, legal status, election certification, or live-pilot readiness.
