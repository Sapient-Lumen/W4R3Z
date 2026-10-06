# Browser OPFS abrupt-kill boundary slice

Current revision: rev0060.

Task id: `browser:opfs-abrupt-kill-boundary-proof`.

This slice is intentionally runtime-heavy and browser-tier only. It launches managed Chromium twice against the same local origin and the same temporary browser profile. The first launch writes and verifies acknowledged async OPFS content-addressed blocks, then creates one intentionally unclosed `FileSystemWritableFileStream` candidate and the harness kills the browser process group with `SIGKILL`. The second launch reuses the same profile and origin, verifies that acknowledged blocks are still readable and checksum-valid, inspects the unclosed candidate, deletes any present candidate, and cleans the namespace.

## Claims checked

- Same local origin and same temporary profile are reused across two managed Chromium launches.
- Acknowledged OPFS block-store writes whose `close()` and readback completed before `SIGKILL` are readable and checksum-verifiable after relaunch.
- The first browser launch is torn down with explicit `SIGKILL`, not clean browser shutdown.
- An intentionally unclosed in-flight OPFS write is not silently accepted as corrupt content-addressed data after relaunch. The accepted dispositions are absent, complete-valid, or read/checksum rejected.
- Cleanup removes acknowledged blocks and any interrupted candidate observed after relaunch.

## Non-claims

This is not a cross-browser conformance claim, not organic quota or eviction evidence, not a Storage Buckets or persistent-storage retention claim, not a multi-tab coordination claim, not an OPFS fsync or power-loss durability guarantee, not a browser crash-recovery guarantee, and not a production storage policy.

The interrupted write is a single bounded `FileSystemWritableFileStream` case. It exercises a risky cloudtainer/browser boundary, but it does not prove all partial-write timings, operating-system crashes, kernel panics, disk-cache flush behavior, quota eviction, or mobile/background lifecycle behavior.

## Evidence

The validation artifact records:

- browser/CDP harness process teardown mode and `SIGKILL` signal evidence;
- same-origin and same-profile observations;
- acknowledged block digests, readback digests, verify results, delete results, and cleanup result;
- interrupted-candidate hash, intended byte length, first written chunk length, and restart inspection disposition;
- OPFS block-store trace kinds including put/get/has/delete/cleanup;
- explicit non-claims so future sessions do not inflate this into durability doctrine.
