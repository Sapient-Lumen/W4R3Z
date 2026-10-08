# Scenario — raw `profraw` is not durable trend input without a profile-compatibility receipt

This scenario protects against treating a pair of raw profile files from different nightly/compiler toolchain builds as if they were automatically safe for long-lived trending.

LLVM's profile-format docs explicitly say raw profiles have no backward or forward compatibility guarantees, and rustc's codegen docs warn that coverage profile formats may change.
A bundle that wants to retain or compare these inputs therefore needs an explicit `profile-compatibility.receipt.json`.
