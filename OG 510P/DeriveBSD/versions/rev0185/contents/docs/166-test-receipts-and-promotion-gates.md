# Test receipts as evidence (Kyua/ATF): promotion gates without hand-wavy “it passed CI”

DeriveBSD already treats provenance, SBOMs, closure proofs, and policy decisions as **digestable evidence objects**.
Testing should follow the same rule: a “pass” is only meaningful if it is bound to:
- the artifact digest being tested
- the exact test suite identity
- the execution environment and authority profile

## The concept: `test.receipt`

Related: fuzzing receipts + crash cases follow the same pattern (`docs/274-continuous-fuzzing-farm.md`).

A **test receipt** is a small canonical object emitted by a test runner compartment (jail/microVM):
- `artifact_digest` (what was tested)
- `testsuite_digest` (what tests were run)
- `runner_digest` (the runner image / harness)
- `sandbox_profile_digest` (authority boundary)
- `result_summary` (pass/fail + counts)
- pointers to detailed reports (content-addressed)

The receipt is signable and can be attached as an in-toto-style attestation.

## Why this matters

- “We ran tests” becomes verifiable, reviewable, and explainable.
- Promotion rules can be explicit:
  - “production channel requires test suite X to pass in runner profile Y”
- It reduces accidental “tested the wrong thing” failures.

## Scenario tests (multi-machine)

Unit/regression tests are necessary but not sufficient. DeriveBSD should also support **scenario tests** (multi-node, realistic networking) that still emit digest-bound receipts.

See: `docs/188-scenario-tests-multimachine.md` (and RFC-0123).

For operability, scenario runs should be driven by a reproducible VM test driver that
keeps VMs alive for debugging and exports serial logs/screenshots as content-addressed evidence.
See: `docs/405-interactive-vm-tests-and-artifact-capture.md`.

## Where it plugs into the pipeline

### Plan → Artifact
Optional policy rule:
- build step emits an artifact
- test step consumes that artifact digest and emits `test.receipt`

### Cache / Distribution
Optional policy rule:
- only publish/promote artifacts if required receipts exist

### Activation / Launch
Optional policy rule:
- only launch workloads in certain zones if required receipts are present and verified

## Execution environment

- v0: test runner is a jail-backed harness (fast)
- v1+: microVM-backed test runner (preferred for hostile-code isolation)

Tests should be able to run with network denied by default.

## Using Kyua/ATF (BSD-native)

BSD ecosystems already have credible testing tooling:
- ATF for authoring tests
- Kyua for execution and reporting

DeriveBSD does not need to invent a runner; it needs to standardize the receipt object and make it policy-addressable.

## References

- Kyua overview/man page: https://man.freebsd.org/cgi/man.cgi?query=kyua
- FreeBSD TestSuite notes (ATF/Kyua): https://wiki.freebsd.org/TestSuite
- ATF project (test authoring libraries): https://github.com/freebsd/atf

See also: `docs/88-conformance-tests-kyua-atf.md`, `docs/93-policy-decision-records.md`.

Last updated: 2026-02-27r118
