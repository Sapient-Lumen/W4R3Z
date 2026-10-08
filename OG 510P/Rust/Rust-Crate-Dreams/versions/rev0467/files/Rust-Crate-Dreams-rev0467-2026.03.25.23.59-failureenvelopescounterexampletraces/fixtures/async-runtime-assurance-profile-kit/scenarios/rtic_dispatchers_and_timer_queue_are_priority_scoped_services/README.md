# Scenario: RTIC dispatchers and timer queue are priority-scoped services

This scenario exists to stop the flattening move:

> “RTIC is just another async runtime with the same service assumptions as Tokio.”

RTIC’s current docs say something more specific: hardware scheduling is performed directly by hardware, software-task execution is handled by generated async executors, and dispatchers/timer-queue behavior are priority scoped.
The topology receipt keeps those facts visible instead of pretending RTIC provides a general-purpose I/O runtime.
