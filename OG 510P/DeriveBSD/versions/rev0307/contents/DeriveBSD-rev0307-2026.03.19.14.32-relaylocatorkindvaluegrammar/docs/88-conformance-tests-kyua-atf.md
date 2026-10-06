# Conformance + regression tests (Kyua + ATF)

DeriveBSD needs a test harness to keep the “planned-from-scratch” properties intact:
- determinism and canonicalization
- closure verification
- policy decision purity
- safe defaults (deny network, sandbox builds)
- stable CLI JSON outputs

BSD ecosystems already have a credible harness: **ATF** (test authoring) + **Kyua** (execution + reporting). Kyua was designed to equip BSD OSes with test suites and integrates with CI. (See `docs/32-curated-references.md`.)

## Test suite strata

1) **Schema + canonicalization**
- reject non-I-JSON
- JCS canonicalization determinism
- roundtrip stability (Spec/Lock/Plan)

2) **Builder isolation**
- build jail has no network
- filesystem writes are confined
- builder identity is pinned and logged

3) **Store semantics**
- tree encoding determinism (DAR; docs/82)
- closure completeness proofs

4) **Runtime mapping**
- bhyve manifest → bhyve flags mapping is deterministic
- pf anchor rules match golden output (docs/67)
- rctl/cpuset enforcement is applied and logged (docs/68)

5) **Policy**
- policy decisions are pure and traces are stable (docs/85)

6) **CLI UX invariants**
- `--json` output matches golden schema
- error codes remain stable (docs/87)

## “Golden output” strategy
Prefer:
- minimal canonical JSON fixtures
- content digests instead of large binary blobs
- reproducibility capsules only for failures (docs/81)

## Non-goals (v1)
- re-testing FreeBSD itself; we test DeriveBSD invariants
- huge fixtures in-repo

See RFC-0058.

Last updated: 2026-02-23


## Integration layer: scenario tests

Conformance suites catch regressions in primitives. DeriveBSD should also run **scenario tests** (multi-node microVM topologies) for promotion gates.
See: `docs/188-scenario-tests-multimachine.md`.
