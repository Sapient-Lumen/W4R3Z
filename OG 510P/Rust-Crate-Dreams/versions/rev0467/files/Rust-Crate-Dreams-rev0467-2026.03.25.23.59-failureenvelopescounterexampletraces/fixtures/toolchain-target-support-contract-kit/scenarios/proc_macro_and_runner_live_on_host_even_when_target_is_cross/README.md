# Scenario — proc macros and runners live on the host even when the target is cross

This scenario exists to keep **host-target topology** separate from vague “cross-target CI” claims.

The crate is built for `aarch64-unknown-linux-gnu` from an `x86_64-unknown-linux-gnu` host.
Build scripts and proc macros still compile for and run on the host.
The produced test binary targets AArch64 and only executes through a custom runner / emulator lane.

A serious support-contract crate should record those phases explicitly so “CI passed” does not silently mean only the host helper phases passed.
