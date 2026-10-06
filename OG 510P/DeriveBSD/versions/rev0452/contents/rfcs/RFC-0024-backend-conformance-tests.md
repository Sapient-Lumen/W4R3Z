# RFC-0024: Backend conformance tests

Status: Draft

## Summary

Define a conformance suite so that different hypervisor backends/adapters implement the same semantics:
- mapping determinism
- policy enforcement
- structured evidence outputs

See `docs/44-backend-conformance-tests.md` and `docs/88-conformance-tests-kyua-atf.md`.

## Goals

- Prevent backend drift.
- Make “supporting a backend” a testable claim.

## Non-goals

- Performance benchmarking (separate topic).
