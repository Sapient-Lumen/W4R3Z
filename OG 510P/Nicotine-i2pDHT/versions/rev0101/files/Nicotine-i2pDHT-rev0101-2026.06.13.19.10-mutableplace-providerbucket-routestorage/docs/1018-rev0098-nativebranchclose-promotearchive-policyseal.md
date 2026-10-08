# rev0098 — nativebranchclose-promotearchive-policyseal

rev0098 deliberately closes the current GCC/native exploration loop instead of granting native power. The held promotion review from rev0097 can be archived, a local shadow-only native policy can be accepted, and a branch-close capsule can mark the path closed while Python fallback stays authoritative.

Strong sentence:

> A held native review can be archived and a branch can be closed, but neither becomes native permission; future promotion needs a new explicit branch.

Active surfaces:

- `src/i2p_dht_lab/nativepromotearchive.py`
- `src/i2p_dht_lab/nativepromotionpolicy.py`
- `src/i2p_dht_lab/nativebranchclose.py`
- `src/i2p_dht_lab/nativebranchclosefold.py`
- `tests/test_rev0098_nativebranchclose_promotearchive_policy.py`

Nonclaim: no production native ABI, loader, sandbox, parser, crypto, dispatch authority, or promotion protocol is created.
