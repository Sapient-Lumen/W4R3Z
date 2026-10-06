# Rust and LLM-centric engineering

DeriveBSD should be engineered so that both humans and LLM-assisted tooling can reliably *modify, validate, and review* it.

## Why Rust
- Strong typing and explicit error handling for “policy + infra” code.
- Great ecosystem for CLIs, JSON schemas, parsing, and concurrency.
- Memory safety is aligned with our security posture.
- Widely studied by LLMs → better automated refactors and test generation.

## “LLM-centric” is not “LLM-dependent”
We build *stable machine interfaces* so automated agents can:
- generate patches that validate
- propose minimal diffs
- emit structured logs
without being trusted with secrets or privileged actions.

## Design constraints (v1)
- All core artifacts have schemas and versions.
- Every CLI command has `--json` structured output.
- All errors are stable codes + machine-readable fields.
- “Repro capsules” capture minimal state to reproduce a failure.

See:
- `docs/38-structured-outputs.md` (RFC-0019)
- `docs/39-repro-capsules.md` (RFC-0020)
- `docs/42-schema-evolution.md` (RFC-0022)

Last updated: 2026-02-23

## Spec frontend pointer

Spec frontend approach: `docs/79-derive-spec-frontends.md` (RFC-0052, ADR-0023).
