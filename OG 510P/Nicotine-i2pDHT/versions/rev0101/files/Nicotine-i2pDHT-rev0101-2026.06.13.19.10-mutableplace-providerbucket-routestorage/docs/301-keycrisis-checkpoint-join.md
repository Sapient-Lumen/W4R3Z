# Key-crisis checkpoint join — rev0030

`keycrisisjoin.py` keeps key-crisis recovery from becoming a local bypass around restart memory. A recovery rotation can be signed and witness-backed, but it must still survive checkpoint pressure: tombstones, revocations, and other hard-negative facts must not disappear when a crisis record is processed.

The joined rule is:

> key recovery cannot erase local memory that made the old key dangerous.

The tests exercise recovery acceptance, checkpoint hard-negative loss, and egress-budget refusal after an otherwise plausible recovery record.

Nonclaim: this is not a global key authority, not a global ban system, and not a production key-rotation protocol.
