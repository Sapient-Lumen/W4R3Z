# Scenario — `thiserror` public code and `anyhow` app context are not the same identity contract

This scenario exists to stop future passes from flattening these distinct surfaces into one fake “stable error API” claim:

- a library-level public error code or variant policy,
- application-layer `anyhow` context strings,
- and internal troubleshooting prose.

A stable public identity needs its own receipt.
