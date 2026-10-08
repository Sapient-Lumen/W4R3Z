# Release package path audit (generated)

Generated from `Makefile`, `tools/package_release.py`, and `tools/smoke_package_release.py`. Do not edit directly; run `make index` after changing release tooling.

- Manifest revision: `rev0378`
- Package-path checks: `11`
- Package-path failures: `0`

| Check | Passed |
|---|---:|
| `package-target-depends-on-index` | `true` |
| `package-target-depends-on-lint` | `true` |
| `package-target-builds-zip` | `true` |
| `package-target-smokes-zip-after-build` | `true` |
| `package-excludes-nested-zips` | `true` |
| `package-writes-sorted-path-order` | `true` |
| `package-fixes-zip-metadata` | `true` |
| `smoke-tool-present` | `true` |
| `smoke-extracts-and-lints-package` | `true` |
| `smoke-rebuilds-package-from-extract` | `true` |
| `smoke-compares-package-sha256` | `true` |

## Rule

`make package` is a release boundary, not a convenience zip command. It must regenerate generated surfaces, lint the source tree, build deterministic archive bytes, extract the package, lint the extracted tree, and rebuild byte-identically from the extracted contents. This audit creates no scientific support; it prevents stale or non-replayable cube releases.
