# Dioxus dependency edit falls outside tip-crate hotpatch

This scenario exists to force **P-0537** to record that a Rust logic edit may still fall off the fast path simply because it happened outside the current tip-crate patch scope.

Current Dioxus and `subsecond` docs both say hotpatching currently tracks only the tip crate.
That means a dependency or workspace edit may still need rebuild/restart even when the logic change itself would otherwise look patch-friendly.
