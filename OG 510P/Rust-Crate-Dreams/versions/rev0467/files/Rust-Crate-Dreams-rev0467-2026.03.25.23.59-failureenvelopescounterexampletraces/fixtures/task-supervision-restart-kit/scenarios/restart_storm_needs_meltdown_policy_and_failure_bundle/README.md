# Scenario: restart storm needs meltdown policy and a compact failure bundle

A background poller restarts repeatedly under one-for-one supervision. The policy needs to make the restart window explicit and emit a small support bundle when the meltdown threshold is crossed.

