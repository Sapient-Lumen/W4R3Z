# rev0838 research notes

## JSON interoperability

RFC 8259 recommends unique object member names because duplicate-name behavior differs among parsers, and identifies the inclusive integer range bounded by 2^53−1 as the range where common implementations agree exactly. That supports two rev0838 choices: duplicate-key rejection remains parser-level policy, and every authority-bearing heartbeat integer is restricted to exact JSON interoperability rather than rounded through binary64.

Source: https://www.rfc-editor.org/rfc/rfc8259.html (sections 4 and 6)

## Fencing belongs at the resource recipient

The Chubby paper describes passing a lock acquisition count with a write and having the file server reject a lower count, specifically to guard against delayed packets. The analogous AnonSync rule is that a heartbeat cannot grant takeover by itself: the consumer compares the exact durable owner generation and release evidence before acting.

Sources:
- https://research.google/pubs/the-chubby-lock-service-for-loosely-coupled-distributed-systems/
- https://storage.googleapis.com/gweb-research2023-media/pubtools/4444.pdf (section 2.1)

## Heartbeats are supervision observations

The systemd watchdog contract associates notifications with the configured process and timeout, and recommends keep-alives at half the timeout. This is a useful operational pattern, but it is a liveness/supervision contract—not proof of exclusive ownership. AnonSync should continue to keep heartbeat freshness separate from durable owner fencing.

Source: https://www.freedesktop.org/software/systemd/man/latest/sd_watchdog_enabled.html

## Failure suspicion and incarnation

SWIM separates failure detection from membership-update dissemination, introduces a suspicion phase to reduce false positives, and uses incarnation numbers to distinguish successive lives of one member. AnonSync is not implementing SWIM here, but the design suggests two future improvements: represent “suspected stale” separately from “authorized takeover,” and bind the heartbeat to an OS process-incarnation token rather than a PID observation alone.

Source: https://www.cs.cornell.edu/projects/Quicksilver/public_pdfs/SWIM.pdf

## Speculative direction

A future heartbeat v2 could contain a narrow signed or MACed observational envelope, a boot/process-incarnation identifier, and a monotonic observation sequence. Even then, recipient-side durable generation fencing should remain the authority. Cryptographic authenticity would answer “who minted these bytes,” not “does this process still own the checkpoint now.”
