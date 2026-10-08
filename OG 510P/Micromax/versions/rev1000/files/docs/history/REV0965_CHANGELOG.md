# Micromax revision 0965

## Outcome

Rev0965 derives focused tests, two reproducible wheel builds, installed-artifact
proof, receipt, and two revision archives from one captured source generation.
It also repairs a modern-setuptools license collision and removes caller umask
from wheel identity.

## Release path

- Added `tools/mxrepro.py`, a fail-closed single-capture release lane with
  independent test, wheel-A, wheel-B, archive-A, and archive-B materializations.
- Generated and validated `MICROMAX-CONTEXT.json` once from captured bytes and
  included its row, `SOURCE_DATE_EPOCH`, revision, and epoch origin in the
  sealed source identity.
- Rechecked live source during capture and immediately before publication.
- Added exact builder declarations, deterministic child environment, separate
  homes, offline wheel builds, and normalized source timestamps.
- Normalized snapshot files to 0644 and directories to 0755, then verified modes
  around every phase on POSIX so extraction permissions and umask cannot alter
  wheel metadata.
- Built and independently verified two wheels; publication requires identical
  bytes and verification records.
- Installed the exact publish candidate outside the source tree and ran an
  isolated import/resource/editor-contract probe.
- Added a compact self-digested release receipt and bound it to the archive's
  recomputed source identity.
- Built two independently materialized revision archives and required exact byte
  equality before publication.

## Packaging and CI

- Moved project license metadata to PEP 639 `license = "MIT"` plus
  `license-files = ["LICENSE"]` with a `setuptools>=77.0.3` compatibility floor.
- Removed the duplicate manual license data-file that collided with modern
  `.dist-info/licenses` creation.
- Added `make repro-release` and a small `ubuntu-24.04` GitHub Actions lane.
- Gave the workflow read-only contents permission, disabled persisted checkout
  credentials, and pinned checkout/setup actions to full release commit SHAs.

## Audit/refactor

- Reused the existing process-group-aware subprocess runner instead of adding a
  release-only timeout implementation.
- Removed an alternate duplicate release prototype and one redundant provenance
  payload; the receipt is the single archive-bound result.
- Replaced a third wheel build with a stronger probe of the exact wheel selected
  for publication.
- Added bounded strict receipt reads, duplicate-name rejection, and mode-mutation
  regression tests.
- Made snapshot-verifier test fixtures establish 0644/0755 explicitly, so the
  tests exercise their intended mutations even when the whole release lane runs
  under restrictive `umask 077`.

## Honest boundary

The evidence covers one declared CPython/toolchain/platform class and a focused
release test set. Capture is not an atomic hostile-writer filesystem snapshot;
CI downloads are not hermetic or hash-locked; the receipt is integrity evidence,
not a signature or attestation; and no public package publication, signing,
transparency, SLSA, complete-suite, or universal cross-platform claim is made.
