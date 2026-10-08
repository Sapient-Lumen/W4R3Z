# Session-resume joined gate

`sessionresume.py` treats resume as a new joined boundary rather than an undo button.

A resume needs exact-scope agreement from:

- the accepted service-exit resume report;
- breaker recovery;
- session ledger;
- service lease;
- public announcement if public exposure is required;
- relay ticket if bridge mode is involved;
- router-session shadow;
- hard-negative scan.

It rejects drift across service/scope/request/session, repeated signal replay, withdrawn announcements, hard-negative pressure, same-kind report forks, and one-family monoculture.

The design guess is that resume is often riskier than pause. A paused garden service is quiet; a resumed one starts emitting reachability, metadata, and resource commitments again.
