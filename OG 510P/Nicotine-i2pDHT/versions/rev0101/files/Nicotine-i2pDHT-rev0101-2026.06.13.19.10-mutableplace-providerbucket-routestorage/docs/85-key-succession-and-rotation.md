# Key succession and rotation

Mutable control-plane keys will become precious. Revocation, policy, seed heads, sync rosters, and release channels all need a way to survive key rotation.

## Implemented

`succession.py` adds a co-signed succession record:

```text
old_public_key
new_public_key
sequence
issued_at / expires_at
previous_record_hash
old_signature
new_signature
```

The old key signs transfer. The new key signs acceptance. Local memory remembers the highest succession sequence and detects:

```text
rollback to older succession
same-sequence fork to a different new key
bad co-signature / tampering
```

A succession record can also be wrapped as a mutable head signed by the old key.

## Open design pain

The current prototype treats each old key as the root for succession memory. Real systems may want roots, delegated writers, emergency recovery keys, threshold rotation, or transparency witnesses. The hard test remains the same: a valid old key event must not silently erase a later accepted succession.
