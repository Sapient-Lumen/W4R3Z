# Safe cleanup and hard-negative preservation

`safecleanup.py` treats cleanup as a signed local side-effect rehearsal. Soft fuzz cases, expired witnesses, and crash-cut debris may be compacted, but accepted effect seals and hard-negative evidence must survive.

Cleanup tickets bind recovery report digest, effect-seal report digest, scope, request, removable item digests, preserved hard-negative digests, preserved effect-seal digest, sequence, previous digest, family, and path family.

A cleanup that removes tombstone/revocation/provider-false/fork-style hard negatives is a protocol failure, not housekeeping.
