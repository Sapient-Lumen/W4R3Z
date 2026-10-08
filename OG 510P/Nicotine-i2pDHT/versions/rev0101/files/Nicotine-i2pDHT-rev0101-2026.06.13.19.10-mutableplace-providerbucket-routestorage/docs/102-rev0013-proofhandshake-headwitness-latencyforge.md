# rev0013 — proofhandshake-headwitness-latencyforge

rev0013 continues the risk-first implementation sequence from rev0012, but it deliberately works in several different parts of the problem at once.

## Three hard lanes

### 1. Provider proof handshakes

A signed provider record is a claim. It is not availability. It is not correctness. It is not proof that the provider can serve the bytes a consumer needs.

rev0013 adds `proofhandshake.py`, which models:

- signed provider availability claims,
- nonce-bound proof challenges,
- commitment-only or raw-key challenge visibility,
- signed provider proof responses,
- signed useful refusals,
- wrong-content rejection,
- challenge replay rejection,
- response deadline pressure,
- witness evidence digests that omit raw content keys.

The strong guess: provider confirmation should become a transcript algebra before it becomes a transport feature.

### 2. Mutable head witness pressure

Mutable heads remain central, but the question is no longer only whether a head is signed. The hard question is what to do when signed heads disagree.

rev0013 adds `headwitness.py`, which models path-family-aware mutable-head lookup pressure:

- latest head diversity,
- one-family monoculture rejection,
- stale-head pressure,
- same-sequence fork pressure,
- previous-link mismatch pressure,
- garden witness statements,
- accept-with-watch when the path evidence is okay but witness memory is absent.

The strong guess: a valid head is an observation; acceptance requires local history, path-family diversity, and sometimes garden watch.

### 3. Fake latency/churn/retry

I2P transport behavior will be noisy. It should not be the first place the DHT learns that timeouts, useful refusals, lying fast windows, and retry scheduling change lookup outcomes.

rev0013 adds `latencyforge.py`, which tests:

- timeouts,
- useful refusal as a reachable-capacity signal,
- captured fast windows,
- family-diverse retry pressure,
- deterministic transcript digests for fake transport events.

## Audit/refactor lane

The cube also starts auditing itself. rev0013 prunes `.pytest_cache` from the shipped artifact and adds a non-failing audit report that identifies duplicate ADR/doc number history and near-duplicate module names.

This is not bureaucracy. It is wake-from-amnesia scaffolding. A fast speculative cube needs visible entropy accounting.

## Current nonclaims

- No live I2P/SAM transport.
- No production DHT.
- No production provider proof protocol.
- No production mutable-head consensus.
- No private retrieval guarantee.
- No production witness or moderation process.
- No production anonymity or metadata-safety guarantee.
