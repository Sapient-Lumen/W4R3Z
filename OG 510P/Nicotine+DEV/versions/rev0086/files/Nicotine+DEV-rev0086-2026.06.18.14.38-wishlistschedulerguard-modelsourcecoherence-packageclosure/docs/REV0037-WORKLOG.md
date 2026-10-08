# rev0037 worklog

1. Continued from rev0036 and inspected the U-123 production-draft blocker.
2. Prototyped the rev0036 identity-only deactivation patch and reran its fixed-behavior regression.
3. Added a broader active-owner collision regression showing identity-only deactivation is insufficient.
4. Prototyped a selected two-part fix: reject colliding same-user/same-token download requests before dequeue/acceptance, plus identity-aware deactivation.
5. Verified the selected patch shape across all three archived lanes.
6. Updated U-123 report text, fix skeleton, strict-promotion data, queue data, and public-overlap notes.
7. Performed a coherence/refactor audit splitting active-owner collision rejection from stale deactivation cleanup.
