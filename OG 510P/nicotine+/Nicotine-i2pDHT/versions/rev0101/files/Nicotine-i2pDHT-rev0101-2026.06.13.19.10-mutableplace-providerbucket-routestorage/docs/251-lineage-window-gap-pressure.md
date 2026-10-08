# Lineage window gap pressure

Mutable heads need history pressure. A higher sequence can be signed by the right writer and still be operationally unsafe if the local node cannot connect it to known memory.

`lineagewindow.py` adds:

- `HeadMemoryAnchor` for local highest-known sequence and digest.
- `HeadLineageObservation` for signed head observations carrying scope, writer key, sequence, head digest, previous digest, payload digest, source family, and path family.
- `LineageWindowPolicy` for direct-gap and family-diversity rules.
- `analyze_lineage_window()` for local decisions.

The important outcomes are:

```text
accept_linked_advance
accept_refresh
continue_missing_prev
continue_under_diverse
quarantine_rollback
quarantine_same_sequence_fork
quarantine_prev_mismatch
quarantine_scope_mix
quarantine_bad_signature
```

The riskiest case is a valid high-sequence observation with an unknown previous digest. rev0026 does not accept it. It emits a repair request for the missing predecessor window.

This is still not consensus. It is local memory pressure before accepting mutability.
