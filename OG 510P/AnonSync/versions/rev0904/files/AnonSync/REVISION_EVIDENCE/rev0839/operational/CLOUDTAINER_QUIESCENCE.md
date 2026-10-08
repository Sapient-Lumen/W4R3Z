# Cloudtainer quiescence and evidence ownership

During rev0839 validation, old orphaned command streams repeatedly reappeared against
abandoned work roots under `/tmp` and `/mnt/data`. They compiled unrelated copies,
consumed the same memory budget, killed CTest workers, and attempted to create a
conflicting rev0839 package. Treating those results as one build would have produced
false timing and possibly false artifact lineage.

The authoritative correction was procedural and evidence-oriented:

- one immutable active source at `/tmp/anonsync-r0839/AnonSync`;
- one authoritative GCC Debug build at `/tmp/anonsync-r0839/build-debug`;
- exact active-projection digest checkpoints;
- stale process groups terminated by process group rather than broad cleanup;
- stale work roots atomically moved to explicit read-only quarantine paths;
- incomplete CTest logs excluded;
- 131 tests accounted for by exact, non-overlapping successful ranges;
- final package staged under a new isolated `/tmp` directory and published only after
  directory and ZIP verification.

This does not solve shared-container orchestration generally. Future revisions should
use a small checked-in validation driver with a unique revision lock, parent/child
process ownership, immutable source digest, per-step output paths, and atomic package
publication. Such a driver belongs in the active projection only after it has its own
adversarial tests; this revision records the protocol without changing validated C++
again at seal time.
