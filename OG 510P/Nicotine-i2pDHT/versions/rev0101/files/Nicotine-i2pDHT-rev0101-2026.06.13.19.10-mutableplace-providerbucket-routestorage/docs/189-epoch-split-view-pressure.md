# Epoch split-view pressure

`epochgate.py` answers one lookup: should these signed observations advance local mutable-head memory?

`epochsplit.py` answers the next, harder question: what if several observations across rounds are individually plausible but collectively dangerous?

The module now checks:

- mixed scopes or authorities;
- invalid signature/time observations;
- same-sequence forks;
- newest heads that do not link to local accepted memory;
- stale replay meshes against a locally accepted newer head;
- latest candidates that lack path/source diversity;
- small stale pressure that should be recorded but need not stop a diverse linked advance.

This is intentionally not consensus.  The report proposes a local decision: accept, continue, or quarantine.
