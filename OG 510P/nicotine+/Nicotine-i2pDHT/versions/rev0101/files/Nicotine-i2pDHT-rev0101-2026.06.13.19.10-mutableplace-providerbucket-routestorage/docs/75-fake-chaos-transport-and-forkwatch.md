# Fake chaos transport and forkwatch

rev0009 starts the chaos rig before live I2P/SAM transport.  That is intentional.  Live transport would make tests slower and blur the central question: what should the DHT do when mutable-head answers disagree?

`src/i2p_dht_lab/chaos.py` models fake responders:

```text
honest_latest
stale
fork
empty
```

The rig sorts responses by fake latency/path/source, feeds them to `LocalHeadMemory`, and emits a `HeadLookupTranscript` with:

```text
observations
verdict counts
accepted sequence
fork sources
stale sources
signed witness receipts
```

## Current hardest test

`test_fake_head_lookup_chaos_keeps_asking_on_forks_and_rollback` primes local memory with a latest head, then runs a mixed transcript:

```text
empty responder
stale responder
fork responder
honest latest responder
```

The expected result is not "we found truth".  The expected result is:

```text
accepted_seq remains latest
rollback evidence is preserved
fork evidence is preserved
witness receipts verify
lookup should continue asking more disjoint paths
```

## Why this is valuable before SAM

I2P latency and churn will punish naive lookup behavior.  The fake rig lets us optimize the decision algebra before wiring transport details.  Later, SAM Streaming or Datagram tests can reuse the same transcripts as expectations.

## Open design debt

- Add path-isolation scoring, not just responder modes.
- Add malicious gardens that issue misleading witness receipts.
- Add path capture where all fastest answers are stale.
- Add budget pressure: when does a client stop asking?
- Add time-varying revocation knowledge.
