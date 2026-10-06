# Scenario tests as first-class artifacts (multi-machine, bhyve-native)

DeriveBSD already treats *provenance* and *policy decisions* as digestable evidence objects.
The missing operational ergonomic is **integration testing that matches reality**:
multiple machines, realistic networking, and “did the generation actually work?” checks.

NixOS’s VM testing framework is a good “ecosystem lesson”: tests run inside VMs and can orchestrate multi-VM scenarios with a driver script.  
References:
- NixOS VM tests overview: https://wiki.nixos.org/wiki/NixOS_VM_tests
- Nixpkgs manual (“NixOS tests run in a VM”): https://nixos.org/nixpkgs/manual/

## DeriveBSD direction

Add a *derived* artifact type:

`test.scenario.manifest` (hashable, diffable)
- produced by `derive plan` (or explicitly by `derive test plan`)
- consumed by `derive test run`
- binds the scenario to the same **Lock + Plan** digests used for deployments

### What a scenario describes

A scenario is a graph of nodes + links:

- **nodes**: each node points at a system artifact digest (host generation, microVM image, or a service closure)
- **links**: explicit L2/L3 connections and firewall policy (pf anchor digest)
- **roles**: “db”, “api”, “client”, etc. to keep scripts readable
- **runner**: the harness image digest + sandbox profile
- **script**: test logic, ideally as content-addressed source (or a digest of a compiled test bundle)

### Evidence outputs

Running a scenario emits **test receipts** (see `docs/166-test-receipts-and-promotion-gates.md`):
- one receipt per node (local checks)
- optionally a receipt for the *scenario* as a whole (distributed assertions)

Policy can then say:
- “promotion to stable requires scenario X to pass”
- “prod requires scenario X + health-gated boot”

## Why this matters

- Prevents “works on my laptop / fails in the microVM topology”.
- Makes integration tests reviewable at the same level as code changes:
  `caproute diff + pf diff + scenario diff`.
- Enables a disciplined rollout pipeline:
  canary → staged → stable, each with explicit scenario gates.

## Safety invariants

- Scenario runner is a **separate compartment** (jail or microVM).
- Network access is explicit; default deny.
- Test scripts must not be ambiently privileged (no “ssh into host as root” escapes).
- All artifacts referenced by the manifest are digest-pinned.

See also:
- `docs/88-conformance-tests-kyua-atf.md` (harness strata)
- `docs/112-health-gated-updates.md` (boot health checks)
- Interactive driver + artifact capture ergonomics: `docs/405-interactive-vm-tests-and-artifact-capture.md`

### Deterministic time/entropy (reduce flake)

Scenario manifests may optionally pin a **time/entropy profile digest** so that:

- timers behave consistently across runs
- wall clock does not introduce time-of-day drift
- record/replay artifacts can be compared across machines

See: `docs/197-time-and-rng-authority.md`.
