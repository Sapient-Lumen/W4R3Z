# Copy-on-write recovery versus external corruption

Simulates an embedded durable store that can automatically recover from ordinary unclean shutdowns, but may still need explicit integrity checking or repair after external mutation/corruption.

Why this matters:
- redb documents automatic recovery from crashes, power loss, and other unclean shutdowns, while also exposing `check_integrity()` for suspected external modification or corruption.
- A persistence-surface crate should let maintainers distinguish those failure models instead of collapsing them into one flat “crash safe” badge.

What this scenario should force:
- a failure-model profile that distinguishes unclean shutdown from external modification
- a recovery-posture report that can say `automatic_recovery` for one class and `repair_tool_available` or `manual_review_required` for another
- a doctor warning such as `recovery_claim_exceeds_evidence`
