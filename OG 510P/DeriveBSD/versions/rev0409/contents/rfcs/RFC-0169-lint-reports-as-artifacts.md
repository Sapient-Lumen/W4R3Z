# RFC-0169: Lint reports as artifacts

- Status: draft
- Author(s):
- Created: 2026-02-25
- Last updated: 2026-02-25

## Summary

Standardize a single typed output object: `lint-report`.

This makes quality signals:
- machine-readable
- diffable
- attachable to change receipts, health gates, and incident bundles

## Motivation

DeriveBSD relies on tooling and compilation (svcdb, caproute, promise profiles, policies).
If linting output is unstructured, we can’t:

- gate rollouts reliably
- track quality regressions
- integrate with LLM tooling safely

## Goals

- A stable schema for `derive lint --json` output.
- A format flexible enough for subsystem-specific linters.
- Avoid bespoke output formats for every tool.

## Non-goals

- A universal static analysis format for all languages.

## Proposal

### 1) Add `lint-report` schema + example

- Schema: `spec/lint.report.schema.json`
- Example: `spec/examples/lint.report.json`

### 2) Core fields

- tool identity (name, version)
- target identity (what was linted)
- issues array:
  - `code`, `severity`, `message`
  - optional `path`, `span`, `hint`, `refs`
- summary counters

### 3) Where lint reports show up

- `derive lint` produces a report for the whole repo/config.
- svcdb compiler produces a report for graph + policy mismatches.
- caproute linter produces a report for dangerous edges.

## Backwards compatibility

- Additive.

## Security considerations

- Lint reports may contain sensitive paths/metadata; treat them as evidence governed by capability.

See: `docs/237-lint-reports-and-contract-testing.md`, `docs/81-llm-facing-interfaces.md`, `docs/87-structured-output-contract.md`.
