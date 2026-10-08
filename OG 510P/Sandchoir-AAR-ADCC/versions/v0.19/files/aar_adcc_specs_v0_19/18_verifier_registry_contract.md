# 18 — Verifier Registry Contract (v0.19)

A Verifier is a named, callable check that returns an Evidence Card.

## Verifier entry fields
- `name`
- `kind`: test|build|lint|proof|repro|bench
- `cost`: cheap|medium|expensive
- `cmd_template` or internal hook
- `expected_signal`
- `caching`: allowed? key?
- `notes`

## Why verifiers
They are the bridge between “votes win” and “evidence moves votes.”
They keep counterexample certification cheap and legible.

See also: 36_verifier_economics_and_default_registry.md

See also: 53_execution_plugin_protocol.md
