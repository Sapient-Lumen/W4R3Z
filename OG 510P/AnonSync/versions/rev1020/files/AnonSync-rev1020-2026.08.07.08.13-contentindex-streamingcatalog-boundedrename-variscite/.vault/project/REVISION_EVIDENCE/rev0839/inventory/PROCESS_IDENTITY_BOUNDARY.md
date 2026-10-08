# Process-incarnation observation boundary

`SyncProcessIdentityObservation` is deliberately separate from the opaque,
process-local `SyncProcessIncarnation` capability. The new object is serializable,
forgeable, and observational; it cannot authorize checkpoint mutation.

On Linux, one observation is the tuple `(PID, boot UUID, /proc starttime)`. Rev0839
parses `/proc/<pid>/stat` from the final `)` so a command name containing `)` cannot
shift field numbering, treats zombie/dead states as not running, bounds proc reads,
and optionally polls a pidfd before and after proc inspection. The running cloudtainer
kernel returns `ENOSYS` for `pidfd_open`, so the validated runtime lane exercised the
explicit `/proc` fallback rather than claiming pidfd coverage.

The heartbeat document owns the lifecycle decision table. Daemon preflight and
operator status each call that same evaluator. A stale wall-clock deadline is therefore
not enough: durable owner authority must be non-live and the exact recorded process
must be gone or mismatched. Unsupported, indeterminate, invalid, and legacy PID-only
observations fail closed and require operator attention.

The focused sanitizer incident also became an invariant: a source audit now proves that
every focused object compiled with ASan/UBSan belongs to an executable that links the
sanitizer runtime. This prevents an instrumented-object/uninstrumented-link false gate.
