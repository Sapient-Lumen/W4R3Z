# Correction history retained

1. Rev0872 began from a fresh isolated extraction of the verified rev0871 ZIP
   rather than a stale shared workspace, preventing cross-revision residue from
   becoming implicit lineage.
2. The first active-projection computation exposed three generated
   `tools/__pycache__/*.pyc` files. They were removed before sealing and the
   projection was recomputed; they are neither active source nor package
   members.
3. An additional fresh all-target build attempt exceeded command execution
   windows and is not used as a completed-build claim. The retained evidence is
   the already completed all-target build, final current-source dependency
   closure, focused multi-toolchain lanes, and full registered-test coverage.
4. Patch authority comes from the verified parent plus the exact ten-file
   active delta. The patch was applied to a fresh active-only parent checkout
   and all 337 resulting files were compared byte-for-byte.

These corrections are preserved because assurance depends on distinguishing
observed success from cleanup, interruption, and inference.
