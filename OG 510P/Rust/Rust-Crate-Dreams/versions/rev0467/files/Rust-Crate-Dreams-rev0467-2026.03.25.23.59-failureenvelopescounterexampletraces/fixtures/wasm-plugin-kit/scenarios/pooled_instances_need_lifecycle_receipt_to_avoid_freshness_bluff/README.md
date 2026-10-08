# Scenario: pooled instances require an explicit lifecycle receipt

This scenario exists because current Wasmtime and Extism docs both make reuse/pooling concrete:

- Wasmtime's pooling allocator keeps warm slots and tracks affinity,
- Extism exposes a `Pool` for limited concurrent access to plugin instances,
- and plugin systems often reuse instances for performance.

A host therefore should not imply fresh isolation per call unless it actually instantiates fresh each time.

