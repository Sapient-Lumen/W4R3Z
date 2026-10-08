# Differential native corpus

`nativecorpus.py` keeps the Python XOR oracle at the center.

The corpus lane evaluates native results against deterministic vectors after native provenance has accepted. It requires enough vectors, enough bucket diversity, bounded inputs, and exact native/Python agreement.

This is not a fuzz engine. It is a persistent parity-corpus boundary: a cheap way to catch semantic drift before a native leaf remains selectable.
