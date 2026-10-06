# Priority-0 score-separated clean-response custody README — 2026-06-16

Custodian steps after the responder freezes a completed response:

1. Compute the frozen response SHA256 before opening scorer-only material.
2. Complete the custody evidence record template with a custodian ID distinct from the responder ID.
3. Use timezone-bearing timestamps with this chronology: responder run started <= responder run completed <= response frozen <= scorer intake opened.
4. Record only the responder bundle as pre-response material. Do not list scorer intake, answer key, full archive, prior conversation, or response examples as pre-response material.
5. After the custody record is frozen, hand the response and custody record to a scorer. Manual metric scores belong in the separate score sheet, not in the frozen response.

Non-claim: the custody record is admission evidence only; it is not compact-cue confirmation, deletion authority, benchmark authority, or a review court.
