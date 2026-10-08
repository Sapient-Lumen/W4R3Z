# Scenario — human default and JSON API must not share the same output-mode receipt

This scenario exists to stop future passes from flattening these distinct surfaces into one fake “supports JSON” claim:

- human-friendly summaries,
- machine-readable JSON records,
- stdout ownership,
- and stderr diagnostics/progress.

The durable automation surface needs its own receipt.
