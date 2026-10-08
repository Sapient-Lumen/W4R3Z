# Attestation packs are not oracles

`attestationpack.py` packages typed component report digests so later lanes can carry evidence without repeatedly widening every function signature.

A pack may contain roles like:

```text
effect_reconcile
dead_letter
retry_quorum
recovery_mesh
side_effect_journal
settlement
tombstone
redress
audit_quorum
```

The pack does not prove truth. It only says: these report digests were observed together at this exact boundary by this signer, sequence, family, and path family.

The risk tests reject:

```text
bad signature
expired/future packs
replay
sequence rollback/fork
previous-link mismatch
boundary drift
duplicate role inside one pack
expected digest drift
hard-negative pressure
low family/path diversity
```

That keeps packs as carriage, not authority.
