# Wake from amnesia — rev0033

Read in this order:

1. `docs/329-rev0033-negotiationlane-migrationseal.md`
2. `docs/330-protocol-negotiation-downgrade-pressure.md`
3. `docs/331-state-migration-hard-negative-preservation.md`
4. `docs/332-safe-start-joined-boundary.md`
5. `docs/333-negotiationfold-audit-refactor.md`

Remember the active bug class:

```text
individually valid report -> joined side effect
```

rev0033 adds another version:

```text
individually compatible peer -> safe future session
```

Not true. Compatibility must be exact, selected, feature-bound, policy-bound, state-bound, and transport-shadow-bound before it becomes sticky.
