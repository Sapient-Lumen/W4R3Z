# Scenario — proc-macro stdout becomes explicit foreign output

This scenario exists because Cargo’s own docs say `--message-format=json` does not control arbitrary output from procedural macros or other tools.

The point of this fixture is to keep **native Cargo/rustc events** separate from **foreign output contamination**.
