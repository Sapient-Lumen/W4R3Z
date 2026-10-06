# RFC-0123: Scenario tests as first-class artifacts (multi-machine)

Status: **draft**

## Motivation

DeriveBSD already has unit-like conformance tests (Kyua/ATF) and a `test.receipt` evidence object.
Operational failures typically happen at the **integration boundary**:
- multiple machines
- realistic networking + firewalling
- distributed boot order / readiness constraints
- dynamic service discovery + credentials

We need a standard way to describe and run such scenarios so promotion gates are not ad-hoc.

## Goals

- Define a canonical manifest for scenario tests (`test.scenario.manifest`).
- Make scenario execution produce digest-bound evidence (receipts).
- Keep scenarios reproducible and policy-governable.

## Non-goals

- Replacing Kyua/ATF for unit/regression tests.
- Defining one universal test DSL (the manifest references a script bundle by digest).
- Running heavyweight “full internet” end-to-end tests by default.

## Proposal

### Artifact: `test.scenario.manifest`

A manifest binds:
- inputs (Lock digest, Plan digest, referenced artifact digests)
- topology (node roles + network links + pf anchor digests)
- runner identity (harness digest + sandbox profile digest)
- test logic identity (script/bundle digest)

The manifest is produced deterministically from planning inputs.

### Execution

`derive test run <manifest>`:
- starts each node as a bhyve microVM (or jail where allowed by profile)
- applies networking (epair/VNET) and pf anchors derived from the manifest
- runs the test script in the runner compartment
- emits receipts

### Evidence

Reuse `test.receipt` for node-level results.
Optionally add a scenario-level wrapper:
- `artifact_digest`: the manifest digest
- `node_receipts`: list of receipt digests
- `result_summary`

(If needed later, this wrapper can become `test.scenario.receipt`.)

## Open questions

- How to represent timeouts/readiness and distributed retries without becoming a full orchestration language?
- Should the runner script be restricted to a “capability RPC” substrate (preferred) rather than ad-hoc SSH?

## References

- NixOS VM testing framework: https://wiki.nixos.org/wiki/NixOS_VM_tests
- Nixpkgs manual note on VM-based NixOS tests: https://nixos.org/nixpkgs/manual/
