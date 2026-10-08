# Scenario — JoinHandle timeout drops waiting but task keeps running until abort

This scenario keeps one common task-level lie visible:

> wrapping a `JoinHandle` in `timeout` means the task itself timed out.

Tokio maintainer guidance says that when the timeout triggers, dropping the `JoinHandle` does **not** stop the task.
The lane should therefore emit a `timeout-aftermath.receipt` that records `wait_stopped_only`, `task_still_running`, and `manual_abort_still_required`.
