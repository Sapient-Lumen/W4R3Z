# Scope journal restart memory

`scopejournal.py` makes public-side-effect memory previous-linked and signed.

A journal entry binds:

- profile and service;
- scope, request, and subject;
- component digest;
- sequence and previous entry digest;
- family and path-family hints.

The journal rejects replay, rollback, same-sequence fork, previous-link mismatch, scope/request/subject drift, missing required component memory, and live hard-negative disappearance.

This keeps local restart state from acting like a cache.  It becomes part of the protocol boundary.
