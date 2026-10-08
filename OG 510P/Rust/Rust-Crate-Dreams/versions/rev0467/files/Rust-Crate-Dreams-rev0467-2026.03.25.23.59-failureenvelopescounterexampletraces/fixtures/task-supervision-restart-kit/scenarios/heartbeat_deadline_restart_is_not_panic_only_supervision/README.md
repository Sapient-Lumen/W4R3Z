# Scenario: heartbeat deadline restart is not panic-only supervision

A worker can hang without panicking. The supervision contract needs to say that hung-task detection is based on heartbeats/deadlines, not merely task exit.

