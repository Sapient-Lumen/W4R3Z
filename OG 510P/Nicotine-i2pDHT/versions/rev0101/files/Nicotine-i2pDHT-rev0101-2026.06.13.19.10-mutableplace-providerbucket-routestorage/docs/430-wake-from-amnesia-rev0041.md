# Wake from amnesia — rev0041

Read in this order:

1. `docs/424-rev0041-routerstop-sessionresume-exitjournal.md`
2. `docs/425-router-stop-shadow-boundary.md`
3. `docs/426-session-resume-joined-gate.md`
4. `docs/427-exit-journal-restart-memory.md`
5. `docs/428-controlfold-audit-refactor.md`
6. `tests/test_rev0041_routerstop_sessionresume_exitjournal.py`

Mental model:

```text
operator intent / service breaker / service exit  (rev0040)
  -> router/session stop shadow                   (rev0041)
  -> session resume gate                          (rev0041)
  -> exit/control journal across restart          (rev0041)
```

No live SAM or i2pd operation exists here. The point is to make future side effects boringly exact before they can exist.
