# BVPS rev0354 append-chain / time-seal runbook

1. Open the latest canonical package only.
2. Verify the receipt-chain root before first evidence drop.
3. For every incoming item, record packet ID, original hash, receipt time, clock source, custody role, and redaction/surrogate status.
4. If offline or delayed, mark deferred hash and do not claim original capture time from hash time.
5. Public meeting material is preliminary context only. Capture audio/video/transcript hashes and keep claim embargo active.
6. Complete-looking packets go to adjudication, not closure.
