# Python surface — rev0018

New modules:

```text
src/i2p_dht_lab/livenessbudget.py
src/i2p_dht_lab/tombmesh.py
src/i2p_dht_lab/provider_compat.py
```

New tests:

```text
tests/test_rev0018_livenessbudget_tombmesh_providercompat.py
```

New evidence:

```text
artifacts/process/micro_simulation_report.json
artifacts/process/rev0018_cube_audit.json
artifacts/process/rev0018_local_verification.json
```

Primary executable decisions:

```text
LivenessBudgetDecisionKind.PROCEED_BOUNDED
LivenessBudgetDecisionKind.HOLD_FOR_REFUSAL_BACKOFF
LivenessBudgetDecisionKind.QUARANTINE_FAST_CAPTURE
LivenessBudgetDecisionKind.REDUCE_METADATA_EXPOSURE

TombMeshDecisionKind.BLOCK_RESURRECTION_MESH
TombMeshDecisionKind.ASK_MORE_INDEPENDENT_WITNESSES
TombMeshDecisionKind.QUARANTINE_HEAD_AFTER_COMPROMISE
TombMeshDecisionKind.QUARANTINE_TOMBSTONE_FORK

ProviderCompatActionKind.REEXPORT_CANONICAL
ProviderCompatActionKind.ADAPT_LEGACY_NAME
ProviderCompatActionKind.KEEP_HISTORICAL_ONLY
```
