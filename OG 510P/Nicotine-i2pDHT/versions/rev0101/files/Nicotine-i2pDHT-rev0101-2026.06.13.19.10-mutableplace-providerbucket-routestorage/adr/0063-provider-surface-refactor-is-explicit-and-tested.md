# ADR 0063 — Provider surface refactor is explicit and tested

## Decision

Keep `providerpoison.py` as historical/legacy for now, but treat `provider_poison.py` as the canonical provider memory/backoff/quarantine surface and audit the overlap with tests.

## Reason

The cube produced near-duplicate provider module names during fast iteration.  Removing history too early would harm wake-from-amnesia value, but leaving ambiguity implicit harms maintainability.

## Consequence

`provider_refactor.py` records the current canonical/legacy split.  A future revision can turn the legacy module into a compatibility wrapper after callers migrate.
