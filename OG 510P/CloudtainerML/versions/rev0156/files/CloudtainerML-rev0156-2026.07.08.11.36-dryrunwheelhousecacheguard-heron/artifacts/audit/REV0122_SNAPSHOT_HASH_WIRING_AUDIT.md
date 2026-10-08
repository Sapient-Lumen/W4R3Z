# Snapshot hash wiring audit — REV0122

Status: `pass_static_patch`  
Promotion allowed: `false`

Rev0122 makes the optional hash path real: `HASH_WEIGHTS=1 bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh` now forwards hash verification into the materializer and snapshot intake path.

This is still not a performance or trace claim. The next acceptance policy should require the expected SHA-256 before a public trace can promote.
