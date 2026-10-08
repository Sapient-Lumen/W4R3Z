# Research notes: runtime-health drift and resettable systemd counters

Two systemd facts matter here:

1. `systemctl show` exposes structured per-unit state such as `Result`,
   `ActiveState`, `SubState`, and `NRestarts`, which makes it a good source for
   one installed-lane runtime snapshot.
2. `systemctl reset-failed` resets both the failed state and the service restart
   counter, which means one live snapshot is not enough to preserve a longer
   operator story about whether a lane is repeatedly degrading.

That combination argues for a bounded VHK-side runtime-health history:
- keep the live snapshot grounded in current systemd truth
- preserve a short local memory so operators can still see chronic restart churn,
  repeated failed state, recovery to healthy, or flapping across multiple status
  captures
- surface that drift summary in the same lightweight installed/support/report
  surfaces where maintainers already look first
