# Key crisis and recovery rotation

Mutability needs a crisis path before users need one. rev0030 adds `keycrisis.py` to distinguish ordinary writer-key succession from compromise recovery.

Ordinary succession requires old-key and new-key co-signature plus monotonic sequence / previous-event linkage. That works when the old key is still trusted enough to retire itself.

Compromise recovery is different. If local policy says the old key is compromised, an old-key signature no longer proves a safe transition. A recovery rotation instead needs a new-key signature plus diverse authorized recovery witnesses. One-family recovery is quarantined even when the recovery keys are otherwise authorized.

Tested local pressures:

- sequence rollback;
- same-sequence fork;
- previous-event mismatch;
- compromised-old-key shortcut;
- under-threshold recovery;
- one-family recovery;
- diverse authorized recovery rotation.

The module is deliberately toy-shaped. It is not a global governance system and not a production key-management protocol.
