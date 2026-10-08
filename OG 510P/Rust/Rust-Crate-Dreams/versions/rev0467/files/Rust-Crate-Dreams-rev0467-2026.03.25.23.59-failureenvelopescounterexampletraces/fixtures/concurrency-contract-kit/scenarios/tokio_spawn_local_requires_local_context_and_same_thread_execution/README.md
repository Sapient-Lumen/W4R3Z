# Scenario: Tokio `spawn_local` requires local context and same-thread execution

This scenario proves that “supports local tasks” is not the same claim as “works from any runtime task”.

The important facts are:
- the spawned future stays on the calling thread;
- the API panics outside `LocalSet` or `LocalRuntime`;
- and `tokio::spawn` inside a `LocalSet` does **not** preserve local-context affinity.
