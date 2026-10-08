# BVPS rev0355 media quarantine runbook

Purpose: admit first-drop files without allowing malware, active content, replayed synthetic hashes, hidden metadata, or public-context-only material to become readiness proof.

Sequence:
1. Receive through the media quarantine lane only.
2. Capture provenance before opening content.
3. Make a safe copy or use write-blocked acquisition.
4. Hash original and copy.
5. Run malware/active-content/archive-bomb checks.
6. Route sensitive material to annex review and create public-safe surrogate only after approval.
7. Move the packet only to candidate-for-adjudication.
8. Keep claim embargo active until adjudication, CAP/retest/verifier and claim kernel pass.

A scan pass is not evidence closure.
