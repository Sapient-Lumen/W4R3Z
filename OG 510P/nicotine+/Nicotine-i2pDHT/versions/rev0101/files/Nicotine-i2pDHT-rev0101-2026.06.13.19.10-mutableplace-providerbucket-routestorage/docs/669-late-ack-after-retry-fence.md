# Late ACK after retry fence

A late ACK can arrive after local repair logic has already fenced retry or withdraw readiness. rev0063 treats that ACK as exact-boundary evidence:

- it is previous-linked;
- it binds original idempotency and retry idempotency;
- it binds the live-send gate and retry fence digests;
- it requires family/path diversity before acceptance;
- it remains watch evidence rather than terminal truth.

This prevents a late ACK from laundering retry memory away, while also preventing a retry attempt from pretending the original ACK never happened.
