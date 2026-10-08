# Scenario — Subsecond tip-crate and `call` anchors bound what live update can honestly cover

This scenario freezes the fact that Subsecond currently patches only the tip crate and that route-local `call` / `HotFn` participation defines what can actually observe new code.
A successful patch on one anchored route should not masquerade as whole-workspace coverage.
