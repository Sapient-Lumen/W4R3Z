# Scenario — index visible but docs.rs still queued means only partial public visibility

This scenario exists so **P-0477** does not silently treat docs availability as immediate once the release is present in the index.

`cargo publish` may finish its upload and later observe the index, while docs.rs still reports queued work because builds happen asynchronously and depend on the queue.

The visibility report should therefore distinguish:

- Cargo-facing readiness via index visibility,
- docs.rs queue/pending state,
- and whether the public story is only partially converged.
