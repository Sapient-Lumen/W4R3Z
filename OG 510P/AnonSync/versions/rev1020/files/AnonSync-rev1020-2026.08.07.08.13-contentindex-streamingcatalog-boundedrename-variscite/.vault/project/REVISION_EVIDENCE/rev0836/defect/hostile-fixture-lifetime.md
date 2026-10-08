# Defect: hostile descendant fixtures could outlive a failed test indefinitely

Several process-owner integration fixtures intentionally created a descendant
that called `pause()` forever so the parent could prove topology cleanup. If an
assertion, pipe report, or setup step failed before the test owner performed its
cleanup, the fixture itself had no independent lifetime bound and could become
an orphaned cloudtainer process.

Rev0836 arms every intentionally infinite descendant with a 15-second
`alarm()` before entering the pause loop. This is not the mechanism under test;
it is an independent fixture fail-safe. The structural audits require the alarm
at every hostile pause site so a future test failure cannot silently reintroduce
an immortal fixture.
