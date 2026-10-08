# rev0010 — risk-first implementation pass

rev0010 continues the shift from dreaming to executable risk pressure. The DHT is still not live. That is acceptable. The aim is to make the scariest guesses concrete while the system is still small enough to change.

## Implemented first

```text
pathpressure.py       family-aware mutable lookup pressure
witnesspoison.py      receipt diversity and contradiction analysis
seedcapture.py        seed portfolio capture scoring and diverse selection
revocation_pressure.py revocation-head rollback/fork memory
succession.py         co-signed key rotation and succession memory
tests/test_rev0010_risk_first.py
```

## Why these first

The DHT's hardest future problems are not syntax. They are questions like:

```text
Can a fast captured neighborhood make a user accept stale data?
Can one garden flood us with signed but strategically useless receipts?
Can a stale revocation head make a revoked grant look usable again?
Can a seed portfolio become the new central entrance in disguise?
Can a project rotate a mutable-head key without giving attackers a rollback/fork lever?
```

rev0010 turns those into deterministic tests.

## Core posture

```text
A valid signed mutable record is an observation.
A valid witness receipt is an observation.
A valid seed portfolio is an observation.
A valid revocation head is an observation.
A valid succession record is an observation.

Acceptance requires local memory, diversity checks, and pressure-aware continuation.
```

This is the opposite of an IPNS clone. The cube keeps mutable names, but refuses to pretend that signature validity alone means "latest enough".

## What still is not claimed

No live I2P transport exists here. The path families are labels in a deterministic harness, not proof of route independence. The witness analyzer is not a global honesty oracle. The succession format is not final key management. These tests are design weapons, not production guarantees.
