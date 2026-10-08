# rev0011 PB-01 compatibility baseline

The PB-01 reproducer now deliberately includes compatibility baselines before bug-reproducer cases.

## Preserved behavior covered by tests

```text
- first direct P/D PeerInit is accepted;
- valid PierceFireWall with no direct primary becomes primary;
- valid PierceFireWall can replace an unestablished direct attempt;
- valid PierceFireWall secondary can remain open behind an established direct primary.
```

## Reproduced behavior that should change

```text
- later direct PeerInit can replace an established primary and migrate queued messages;
- secondary P/D/F connection can promote itself after post-init activity;
- valid PierceFireWall secondary kept for compatibility can later promote after an ordinary P message.
```

Run log: `evidence/rev0011-pb01-maintainer-reproducer-run.txt`.
