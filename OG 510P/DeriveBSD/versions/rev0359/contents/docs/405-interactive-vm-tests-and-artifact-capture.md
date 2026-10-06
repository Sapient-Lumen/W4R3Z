# Interactive VM tests and artifact capture (NixOS/openQA-shaped)

**Tier:** C (Optional lane)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, operability
**Patterns:** Capsule, Plan→Apply→Receipt  

DeriveBSD already has the *conceptual* pieces for serious testing:
- Kyua/ATF for unit/regression tests (`docs/88-conformance-tests-kyua-atf.md`)
- digest-bound `test.receipt` objects (`docs/166-test-receipts-and-promotion-gates.md`)
- multi-node scenario manifests (`docs/188-scenario-tests-multimachine.md`, `spec/test.scenario.manifest.schema.json`)

What’s missing is an ecosystem-level ergonomic: a **reproducible test driver** that makes
“run the scenario, inspect the VMs, export the evidence” a one-command habit.

NixOS’s VM test driver is the right *shape*: spin up VMs from a declarative description,
run a driver script, and optionally drop into an interactive session for debugging.
openQA is the complementary *shape*: treat boot/install/GUI validation as OS-level tests
with rich artifact capture (serial logs, screenshots, video) and reproducible replay.

This doc tightens the plan: DeriveBSD’s test driver is itself a derived artifact,
and its outputs are receipts + content-addressed evidence blobs.

## Goals

- Run the same test (same inputs) locally, in CI, and in a lab.
- Make failures debuggable without “SSH and poke”.
- Make promotion gates depend on **receipted** test outcomes.
- Make artifact capture (console logs, screenshots) default and reproducible.

## The test driver (a derived, pinned runner)

Define a runner lane (conceptual name): **`test.driver`**.

A driver instance is a *system artifact* (closure digest) that contains:
- the VM orchestrator (bhyve/QEMU as needed)
- harness glue (node control, log capture, export)
- a small scripting interface (Python/Lua/JS — pick one and freeze it)

The driver is invoked by:
- `derive test run <test.scenario.manifest>`

The important part is not the language; it’s the contract:
- driver identity is digest-pinned
- driver authority is sandboxed (no ambient host root)
- driver always emits receipts + evidence bundles

## Interactive mode (turn flakes into fixes)

Borrow the NixOS “interactive driver” posture:

- `derive test run --interactive <manifest>`
  - run the scripted scenario
  - **drop into a driver shell** afterward with the VMs still running

Interactive mode should allow:
- attach to a VM console
- run commands in a VM (via a controlled channel)
- snapshot/export VM state *as evidence artifacts*

Interactive mode is a developer workflow, but it must remain receipted:
- interactive commands are logged as a `debug.session` transcript (content-addressed)
- exports are explicit, not implicit

## Artifact capture (default-on, content-addressed)

At minimum, capture per-node:
- serial console log (always)
- dmesg snapshots at key phases
- service logs for declared services

Optional lanes (GUI/boot/install shaped; openQA inspiration):
- screenshots at named checkpoints
- short video segments around failures
- bootloader/early-boot capture (screen/serial)

All captured artifacts should be stored as content-addressed blobs and linked from:
- `test.receipt` (per node)
- `test.scenario.receipt` (optional scenario-level summary)

## Receipts and gates

A scenario run should emit:

- `test.receipt` per node
  - binds the **node artifact digest** to the **suite/script digest** to the **runner digest**
- optional `test.scenario.receipt`
  - binds the manifest digest + the set of per-node receipts

Promotion gates then become mechanically simple:
- “stable requires scenario X receipts from runner profile Y”
- “prod requires scenario X + boot health gate receipts”

See: `docs/166-test-receipts-and-promotion-gates.md`, `docs/112-health-gated-updates.md`.

## Relationship to Kyua/ATF

Kyua/ATF remains the *authoring + execution* substrate for many suites.
The driver’s job is orchestration and evidence capture.

A common pattern:
- node boots
- Kyua test suite runs inside the node
- driver pulls Kyua reports + logs and emits a `test.receipt`

## Safety invariants

- The driver runs in a dedicated compartment (jail/microVM) with explicit grants.
- VMs are isolated via VNET and explicit pf anchors.
- Export channels are explicit; default deny network.
- Test scripts do not get ambient host privilege.

## Prior art references

- NixOS VM tests overview: https://wiki.nixos.org/wiki/NixOS_VM_tests
- Nix.dev tutorial: integration testing with NixOS VMs: https://nix.dev/tutorials/nixos/integration-testing-using-virtual-machines.html
- openQA docs (OS installation/boot/GUI testing with artifact capture): https://open.qa/docs/
- Kyua man page (BSD test runner): https://man.freebsd.org/cgi/man.cgi?query=kyua
- ATF intro/man page: https://man.freebsd.org/cgi/man.cgi?query=atf&sektion=7

Last updated: 2026-02-27r118
