# BVPS rev0362 watchpager / exception bridge runbook

This runbook is for the evidence-capture operator. It does not make a readiness claim.

1. Run the live watchdog.
2. If any alarm fires, open the corresponding exception bridge ticket.
3. Require owner acknowledgement within the SLA.
4. Escalate silent alarms to the backup owner and incident commander proxy.
5. Carry unresolved P0 alarms through shift handoff.
6. Keep public claim language frozen until adjudication, CAP/retest/verifier, and claim-kernel gates pass.

Correct successful state: **capture-ready / claim-frozen / alarms routable / acknowledgement required**.
