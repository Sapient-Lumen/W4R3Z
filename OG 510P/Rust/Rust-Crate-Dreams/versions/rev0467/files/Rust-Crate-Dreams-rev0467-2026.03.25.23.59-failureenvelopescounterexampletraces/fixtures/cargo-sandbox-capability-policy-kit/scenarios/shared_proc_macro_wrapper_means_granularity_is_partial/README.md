# Scenario: shared proc-macro wrapper means granularity is partial

The chosen backend can sandbox build scripts separately, but proc macros only through a shared rustc lane.
One macro needs filesystem access, which means the backend cannot honestly claim per-macro isolation.

This scenario exists so the kit records backend granularity as a first-class truth rather than burying it in caveats.
