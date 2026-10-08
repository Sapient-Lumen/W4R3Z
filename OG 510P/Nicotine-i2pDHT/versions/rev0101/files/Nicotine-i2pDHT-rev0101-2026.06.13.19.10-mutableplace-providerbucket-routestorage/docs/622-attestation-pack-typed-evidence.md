# Attestation pack typed evidence

`attestationpack.py` groups component report digests by role. It is a carrier for evidence, not an oracle.

The pack checks role duplication, digest drift, replay, rollback, same-sequence fork, previous-link mismatch, hard-negative pressure, and family/path diversity. A pack can accept with watch when one of its components still carries watch pressure.

The design reason is simple: joined boundaries need to know which component produced which digest. A flat bag of digests is too easy to misuse.
