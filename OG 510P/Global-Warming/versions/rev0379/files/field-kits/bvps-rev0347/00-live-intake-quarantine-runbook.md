# BVPS rev0347 live-intake quarantine runbook

Use this lane only for live or anonymized evidence. Do not copy rev0346 synthetic dry-run files into live intake. A packet in `accepted_for_adjudication` is not closed; it is only ready for the adjudication board.

Operator sequence:
1. Put incoming material into the packet's `incoming/` folder.
2. Hash raw/sensitive-annex reference, redacted surrogate, custody record, and QA note.
3. Move the packet to `quarantine/` for validation.
4. Reject synthetic contamination, public-context-only packets, redacted-only packets, hash-only packets, or packets without owner/verifier/counterevidence path.
5. Move only validated candidates to `accepted_for_adjudication/`.
6. Keep the loss cap until CAP/retest/verifier and claim-kernel gates pass.
