# RFC-0101: Test receipts as evidence + policy promotion gates

Status: **draft**

## Problem

“Passed CI” is not a verifiable property unless it is bound to the artifact and the execution environment.
DeriveBSD already treats many properties as evidence objects; tests should be the same.

## Proposal

Introduce a canonical `test.receipt` object that records:
- artifact digest
- test suite digest
- runner identity
- sandbox profile digest
- summary and report pointers

Policy can require receipts for promotion or activation.

## Implementation notes

- Use Kyua/ATF as the default runner tooling where possible.
- Receipt should be signable and attachable as an in-toto attestation.

## References

- Kyua man page: https://man.freebsd.org/cgi/man.cgi?query=kyua

See: `docs/166-test-receipts-and-promotion-gates.md`.
