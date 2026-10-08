# Scenario: `async_executor::LocalExecutor` is creator-thread-bound and explicitly driven

This scenario proves that the locality / liveness vocabulary is portable beyond Tokio.

The important facts are:
- the executor is `!Send` and `!Sync`;
- it can only be run on the thread that created it;
- and progress happens through explicit `run`, `tick`, or `try_tick` style driving.
