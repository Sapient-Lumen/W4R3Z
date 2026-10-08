# Wake from amnesia — rev0049

Read these first:

1. `docs/514-rev0049-outboxlane-auditgap-fold.md`
2. `docs/515-public-outbox-side-effect-staging.md`
3. `docs/516-audit-gap-repair-planning.md`
4. `docs/517-outboxfold-audit-refactor.md`
5. `tests/test_rev0049_publicoutbox_auditgap_fold.py`

Remember the posture:

```text
No live network writes.
No production DHT.
No global truth.
No production bridge protocol.
```

rev0049 is about the local seam between a shadowed public side effect and a future live publication outbox.
