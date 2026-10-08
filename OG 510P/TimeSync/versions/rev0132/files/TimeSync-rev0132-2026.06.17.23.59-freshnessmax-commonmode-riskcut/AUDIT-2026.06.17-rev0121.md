# TimeSync rev0121 audit — mission compass, exact time, and release integrity

## Scope

This revision deeply reviewed the incoming rev0120 archive, ran all advertised checks, measured corpus composition, traced the charter through later specs, tested timestamp edge cases, and compared the project with current NTPv5, Roughtime, NIST PNT, NTP YANG, chrony, IEEE 1588, reproducible-build, and provenance material.

## Findings corrected in this revision

- Replaced microsecond-truncating timestamp comparisons with exact RFC 3339 fractional arithmetic.
- Added a nanosecond-inverted interval negative fixture, derivation `DF-0121-001`, and semantic vector `TV-N343`.
- Replaced hard-coded validator/linter revision identity with `REVISION-RECEIPT.json` as the source of truth.
- Added receipt checks for immediate baseline, release filename, timestamp/name alignment, expected output, and frontier transitions.
- Added manifest v2 identity fields and made the manifest cover every release file except itself.
- Removed 31 generated `.pyc` files and made generated cache/build artifacts release errors.
- Added `tools/build_release.py` for sorted, normalized, timestamp-fixed ZIP output.
- Closed the long-running FT-0090 internal-hardening frontier and opened FT-0121 around a real adapter plus reference evaluator.
- Added `MISSION-COMPASS-2026.06.17-rev0121.md` with the mission, missing pieces, waste analysis, external research, and speculative direction.

## Important limitations not corrected yet

- No real timing-system capture is ingested.
- No reference evaluator derives TimeState from observations.
- No cryptographic signature verification is performed.
- The 124 acceptance scenarios are still documentary/shape-checked, not executed.
- Dependencies remain range-pinned rather than fully locked.
- No project license, contribution policy, security policy, or CI workflow has been chosen.
- Leap-second/smear/timescale semantics remain a declared frontier; current exact parser fails closed on `:60`.
- The full archive remains large and repetitive; rev0121 documents a split/generation strategy but does not destructively prune history.

## Validation target

```text
TimeSync rev0121 validation passed.
Validated 362 semantic vectors, 6 profile maps, 6 transport adapters, and 25 evidence classes.
```
