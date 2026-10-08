# Bridge quench lane

Public bridge records are sticky.  A single refresh can look valid while repeated windows reveal stale announcements, false service, refusal-only loops, or captured witness families.  `bridgequenchlane.py` turns those repeated observations into typed local pressure.

Quench observations include:

```text
publication_accepted
publication_watch
stale_public_replay
false_service_proof
hard_negative
appeal_watch_loop
refusal_only
withdrawal_confirmed
```

The lane can accept continuation, accept continuation with watch, hold for cooldown, or accept quench.  Quench is local control-plane evidence.  It does not delete DHT truth; it stops or delays a local public bridge publication path until better evidence arrives.

The hardest tests in rev0047 catch stale-public replay, hard-negative quench, repeated watch/refusal cooldown, replayed observations, and one-family capture over multiple windows.
