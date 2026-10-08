# Repair path documented but unwitnessed for current surface

Simulates a crate that points to storage-engine recovery or repair documentation, but has not recently witnessed that recovery path for the actual persisted surface and current format it claims to support.

Why this matters:
- redb documents automatic recovery from crashes, power loss, and other unclean shutdowns, and exposes `check_integrity()` to repair when possible after suspected external modification or corruption.
- Those are strong substrate facts, but a receiver-facing persistence contract still benefits from saying whether recovery or repair was only declared, or actually witnessed on a representative artifact.

What this scenario should force:
- a `recovery-witness.receipt` that can say `declared_only`, `integrity_check_observed`, or `repair_path_observed`
- a separation between automatic crash recovery and explicit repair after external mutation
- a doctor warning such as `recovery_path_declared_but_unwitnessed`
