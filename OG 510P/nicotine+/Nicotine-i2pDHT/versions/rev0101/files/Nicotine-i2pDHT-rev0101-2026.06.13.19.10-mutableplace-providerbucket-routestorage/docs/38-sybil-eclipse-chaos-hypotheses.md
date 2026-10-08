# Sybil, eclipse, and chaos hypotheses

## Starting honesty

An open anonymous DHT cannot assume honest majority near every key.  Sybil resistance is not solved by proof-of-work or signatures.  The design should still remove cheap attacks and make better attacks noisier.

## Low-hanging defenses

- destination/key/nonce-bound node IDs;
- signed RPC envelopes and records;
- challenge-response over the advertised I2P Destination;
- old-contact preference plus replacement caches;
- disjoint lookup paths;
- no unsafe provider early termination;
- quorum and entry correction for mutable records;
- local-only reputation based on useful responses and uptime;
- optional small proof-of-work for routing-table admission;
- sweep-based redundant publication when a key looks attacked.

## What a sentinel role does

A sentinel is not a censor and not a global authority.  It is a local power-user mode that spends more budget on cross-checks:

- repeat lookups from different seed sets;
- compare path outcomes;
- notice false-provider clusters;
- notice stale mutable heads after a newer signed head has been seen;
- publish local diagnostics for the operator;
- optionally feed anonymized aggregate metrics in a later, separate design.

## Chaos lab seeds

Future tests should simulate:

- all Sybils close to one target;
- false providers that trigger early stop;
- stale mutable record replay;
- empty responses from one path family;
- high churn around canonical replicas;
- hot-key overload;
- malicious gate/seed contacts;
- adversarially delayed but not failed responses.

## Python surface

`adversary.py` is a small beginning: it classifies observed path behavior and flags semantic poisoning or empty-response clusters.  It is intentionally tiny so the next revision can replace it with a richer simulation harness.
