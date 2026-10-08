# Scenario: Embassy profile is docs-strong, but board scope still needs imported measurement

The project uses `embassy-executor` and can confidently classify itself as a no-`alloc`, static-task, integrated-timer executor from upstream docs.
However, the product still has board-specific interrupt and power-state assumptions that have not yet been imported from target measurements.

The receipt therefore keeps the target scope board-specific and leaves explicit manual-review zones.
