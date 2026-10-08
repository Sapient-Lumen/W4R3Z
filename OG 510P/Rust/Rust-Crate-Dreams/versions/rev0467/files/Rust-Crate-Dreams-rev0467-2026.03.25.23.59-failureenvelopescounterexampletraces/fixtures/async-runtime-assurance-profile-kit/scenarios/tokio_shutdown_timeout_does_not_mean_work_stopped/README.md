# Scenario: Tokio shutdown timeout does not mean work stopped

This scenario exists to stop a common support lie:

> “We called shutdown with a timeout, therefore all runtime work stopped.”

Tokio's docs make a narrower claim.
Async tasks are dropped when they next yield during shutdown, while blocking tasks keep running until they return.
Timeout-based shutdown can unblock the caller while work continues.
