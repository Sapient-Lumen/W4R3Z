# Research — installed-lane runtime health verdicts

Current Linux service/session tooling suggests a straightforward next lesson for
VHK.

## What current tooling/docs are teaching

- `ExecCondition=` lets a service be skipped for a reviewed reason instead of
  being treated like a normal crash. That is useful, but it only answers one
  question: whether startup should proceed.
- `systemctl show` is still the structured property lane for unit state, so
  operator tooling should prefer fields such as `ActiveState`, `SubState`,
  `Result`, `ConditionResult`, and restart counters over scraping formatted
  status output.
- systemd keeps distinguishing **start-limit** conditions from ordinary exit
  failure, which means “the lane is churning” deserves its own operator-facing
  verdict instead of being folded into a generic failed/inactive bucket.
- socket-owned services can be healthy even when the backing service process is
  idle, so a Linux-native operator surface should not assume “inactive service”
  automatically means “broken product.”

## Product lesson for VHK

A Linux-native AHK-like system should keep lightweight operator truth at two
levels inside the installed lane:

1. **readiness** — should the lane be started in this live session?
2. **runtime health** — given ownership and nearby unit facts, does the lane
   look healthy, skipped, stopped, missing, unavailable, or degraded by restart
   churn/failure?

That combination is more honest than a generic “service active or inactive”
story, and it is much closer to how Linux operators actually debug background
user-session tools.
