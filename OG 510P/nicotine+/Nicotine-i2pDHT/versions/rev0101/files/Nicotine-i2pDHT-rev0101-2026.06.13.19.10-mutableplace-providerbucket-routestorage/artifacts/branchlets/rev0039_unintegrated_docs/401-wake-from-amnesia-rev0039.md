# Wake from amnesia — rev0039

The current question is no longer “did one service request pass?”  The current question is “can service remain locally safe across time?”

Read in order:

1. `docs/393-rev0039-continuityjournal-probeloop-successionrepair.md`
2. `docs/394-service-lease-and-session-ledger.md`
3. `docs/395-continuity-journal-restart-memory.md`
4. `docs/396-probe-loop-health-pressure.md`
5. `docs/397-service-epoch-ledger.md`
6. `docs/398-succession-repair-pressure.md`
7. `docs/399-serviceepochfold-audit-refactor.md`

The rule to remember:

```text
Restart memory, repeated probes, lease renewal, and catalog succession are separate permissions.
```
