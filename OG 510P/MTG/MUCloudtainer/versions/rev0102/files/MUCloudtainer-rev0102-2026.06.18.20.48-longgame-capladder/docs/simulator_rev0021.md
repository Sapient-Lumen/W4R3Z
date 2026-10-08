# rev0021 simulator status

The Python simulator remains the authoritative MUC-5 referee.  The C++ layer now covers:

```text
rev0015 deck-probe numeric kernel
rev0016 legal-menu differential harness
rev0017 transition microkernel initial cases
rev0018 stack/choice transition expansion
rev0019 recorded-trace checker
rev0020 Jace ultimate shuffle transport
rev0021 batched trace preparation/finalization seam
```

The engine is working for automated public-agent play and C++ trace parity.  It is still not time to delete the Python referee or let C++ run unverified tournaments.  The next safe acceleration target is batched execution under replayable trace contracts.
