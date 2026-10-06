# LLM-facing interfaces (design for automated reasoning)

DeriveBSD should be buildable and maintainable with heavy LLM assistance without ever trusting LLMs with:
- secrets
- privileged execution
- authority to deploy

This doc defines the “interfaces that LLMs consume”.

## Mandatory properties
- schema-versioned JSON for all key artifacts (docs/42, docs/80)
- stable `--json` output on every CLI (docs/38)
- diff/explain commands with deterministic minimal output (docs/66, RFC-0042)

## “Patch loop” protocol (concept)
1) `derive lint --json` emits a `lint-report` (issues with stable codes + paths)
   - Schema: `spec/lint.report.schema.json`
2) LLM proposes patch
3) `derive validate --json` confirms schemas
4) `derive diff --json` shows what changed and why
5) (optional) `derive repro-capsule` bundles failure context

## Guardrails
- LLM tools run in least-privilege mode (Capsicum/Casper where possible)
- secrets redaction is automatic and enforced by schema (no secret fields in core artifacts)

Last updated: 2026-02-23

## Output invariants pointer

LLM tooling depends on the stable `--json` contract in `docs/87-structured-output-contract.md`.

## DevShell tooling

Because DevShells are a primary human interface, they must also be first-class in the LLM “patch loop”:
- `derive devshell plan --json`
- `derive devshell explain --json`
- `derive devshell diff --json`

These outputs must obey `docs/87-structured-output-contract.md`.
