# imported_build_analysis_session_no_pid_certainty

This scenario exists to keep a tempting but dangerous move out of future implementations:
linking an imported Cargo build-analysis session as if it proves which process blocked the build.

The session is useful supporting context.
It is **not** blocker identity.
