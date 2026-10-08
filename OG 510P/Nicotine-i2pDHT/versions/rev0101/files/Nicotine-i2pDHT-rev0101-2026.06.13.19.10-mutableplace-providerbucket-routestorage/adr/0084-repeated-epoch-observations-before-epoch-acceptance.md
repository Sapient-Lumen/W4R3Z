# ADR 0084 — repeated epoch observations before epoch acceptance

Accepted for rev0021.

A mutable epoch that validates in one lookup may still be part of a split view or stale replay pattern.  The DHT lab therefore adds `epochsplit.py` to evaluate repeated observations, same-sequence forks, previous-link splits, stale replay meshes, and path/source diversity without claiming global consensus.
