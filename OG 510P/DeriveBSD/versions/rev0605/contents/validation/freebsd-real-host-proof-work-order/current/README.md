# DeriveBSD real FreeBSD host-proof work order

This directory is the next concrete work packet for the highest-risk unfinished
item: the cube still has no checked-in primary-production real FreeBSD host
proof import.

Files:

- `PREFLIGHT_ON_FREEBSD.sh`: run on the real FreeBSD host before collection; it verifies the kit and runs the root-required host preflight through root or sudo.
- `RUN_ON_FREEBSD.sh`: run on the real FreeBSD host from a checked-out tree after preflight is green.
- `IMPORT_IN_CLOUDTAINER.sh`: run after bringing the sealed handoff archive back.
- `VERIFY_WORK_ORDER.sh`: run before either step to ensure this kit still matches the tree.
- `real-host-proof-work-order.json`: machine-readable target, status, and success criteria.

Current target:

- Primary: `15.1-RELEASE` / `kern.osreldate >= 1501500` / `primary-production`.
- Supported floor: `14.4-RELEASE` / `kern.osreldate >= 1404000` / `supported-legacy-floor`.

Manifest digest: `sha256:ca4a9677e3f8e3bb2085e046a18e64df81c47d703b5244ccc2887a812c006393`

The manifest also binds the runnable work-order script digests and the exact
repo proof-tool digests that the scripts execute.  Verification is deliberately
first in runnable scripts so a stale copied kit fails before scarce host
time or returned proof is spent.  The FreeBSD-side preflight can now be run
by itself and is invoked through root/sudo before collection, closing the
earlier sudo/preflight split.  Cloudtainer import also runs the sealed-import
preflight before publish so target-tier/collision failures are caught without
writing an import.  Cloudtainer reruns use `--reuse-existing-import`, so an
interrupted session can verify and reuse the already-published matching sealed
digest import instead of failing as a duplicate or replacing evidence.  The
sealed importer also takes an exclusive sibling import-root lock around the
publish/reuse/replace decision, so concurrent cloudtainer retries fail before
they can interleave with scarce proof publication.

Do not use checker-simulation or refusal flags for this work order.  A successful
run must make `report_removable_media_local_fallback_host_proof_imports.py
--fail-if-incomplete` exit zero.
