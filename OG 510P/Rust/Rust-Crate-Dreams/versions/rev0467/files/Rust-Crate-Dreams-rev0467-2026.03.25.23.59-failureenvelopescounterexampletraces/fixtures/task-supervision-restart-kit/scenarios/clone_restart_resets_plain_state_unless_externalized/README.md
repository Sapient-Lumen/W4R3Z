# Scenario: clone-based restart resets plain state unless it is externalized

A supervised Tokio task increments local counters and also writes to shared metrics. The important truth is that plain fields reset on restart while shared `Arc` state survives.

