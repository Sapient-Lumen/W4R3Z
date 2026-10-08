# Scenario: `async-compat` keeps Tokio context dependency explicit

This scenario exists to stop another common support lie:

> “We added a compatibility adapter, therefore the runtime dependency disappeared.”

`async-compat` solves real problems, but its own docs say that Tokio types cannot be used outside Tokio context and that the adapter may create or enter a Tokio runtime context on demand.
That is bridge value, but it is not the same thing as erasing the underlying provider/context requirement.
