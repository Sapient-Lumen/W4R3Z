# Exec integrity policy + verified execution (MAC/veriexec backend)

DeriveBSD already makes **artifacts immutable** and **inputs explicit**, but a system can still lose if arbitrary bytes can execute at runtime.
This lane makes “what is allowed to execute” a **typed, reviewable, compilable policy** with receipts.

This is a greenfield opportunity to fix a classic gap:
- Nix-like systems verify *builds* and *closures*.
- Traditional OSes often **do not** enforce “only verified code executes” (they rely on admin discipline).

DeriveBSD can keep the Nix ergonomics while optionally compiling a strong runtime enforcement layer using BSD-native primitives.

## Goals

- Provide a uniform policy object that answers:
  - **What bytes may execute?** (binaries, interpreters, dynamic loaders)
  - **In which scopes?** (host, service jail, AppVM, builders)
  - **What is the enforcement mode?** (off / warn / enforce)
- Compile the policy into one or more enforcement backends.
- Emit receipts so incidents can answer:
  - what policy was active
  - what backend enforced it
  - what exceptions existed (and why)

## Non-goals

- Building a new “Linux IMA clone” with bespoke kernel hooks.
- Preventing all in-memory code injection (this lane is about executable *origin* and *integrity*).

## Background (why MAC/veriexec is interesting)

FreeBSD’s MAC Framework supports loadable policies (LSM-adjacent, but BSD-native). A notable policy is **MAC/veriexec**, a verified execution environment that can verify file integrity using metadata mappings (fsid/fileid/etc.).

- FreeBSD MAC/veriexec review trail: https://reviews.freebsd.org/D8554
- FreeBSD verifying manifest loader for mac_veriexec: https://reviews.freebsd.org/D16575
- HardenedBSD Integriforce (hash-based verified execution): https://hardenedbsd.org/article/shawn-webb/2015-03-11/call-testing-secadm-integriforce

DeriveBSD can treat these not as “cool hardening knobs”, but as a **compile target** for a first-class policy.

## Core idea

Introduce an **exec integrity policy** object:

- `exec.integrity.policy` (typed, signed via the trust policy)
- compiled to a backend-specific representation (e.g., a veriexec manifest)
- activated alongside the host generation / workload launch
- evidenced by receipts

Schemas (v0.1):
- `spec/exec.integrity.policy.schema.json`
- `spec/exec.integrity.plan.schema.json`
- `spec/exec.integrity.receipt.schema.json`

## Policy model (v0)

### Scopes

A policy can target one or more scopes:
- `host`: global host exec rules
- `service`: per-service jail rules
- `appvm`: desktop AppVM rules
- `builder`: builder environments (usually **warn** only)

### Allowed exec sources

Policy should be expressible as a small set of “sources”:

- `store-only`: executable bytes must be in the Derive store (and therefore content-addressed)
- `signed-bundle`: executables may come from attached bundles (portable services, incident bundles), but only if bundle digest is authorized
- `quarantine-never`: any file with quarantine/origin flags is denied execution by default
- `breakglass-only`: temporary emergency exception path (lease-based)

### Exceptions (must be explicit)

- Allowlisted paths or digests (bounded)
- TTL-bound overrides (leases)
- Each exception must carry a *reason* and optional approval receipts

## Compilation to MAC/veriexec (backend sketch)

A `exec.integrity.plan` can compile:

1) A **manifest** mapping file identifiers to expected digests.
2) A backend activation step:
   - load/replace the manifest in a controlled moment (boot/activation)
   - switch host generation, then commit when health gate passes

Key constraints to bake in:
- Manifest update must be **atomic** with bootenv switching (`docs/284-bootenv-switching-as-evidence.md`).
- Write access to monitored binaries should be treated as suspicious: strict modes typically deny execution after modification until metadata refresh.
  - DeriveBSD can avoid footguns by making the manifest derive from the closure, not from ad-hoc admin tooling.

## Evidence objects

- `exec.integrity.policy`: what we intended
- `exec.integrity.plan`: what we compiled + which backend we targeted
- `exec.integrity.receipt`: what was actually active

Receipts should include:
- policy digest
- backend name + version
- enforcement mode
- compiled manifest digest (if applicable)
- activation boundary (host generation id / bootenv id / service instance id)

## Interactions with other lanes

- **No mystery bytes**: origin/quarantine metadata becomes an execution guardrail, not just UI hints.
  - See: `docs/280-origin-labels-and-quarantine-attributes.md`.
- **Portable service bundles**: attaching a bundle updates the exec allowlist via a plan+receipt, never by copying binaries into ad-hoc paths.
  - See: `docs/265-portable-service-bundles.md`.
- **Kernel module policy**: “no surprise kernel code” pairs naturally with “no surprise userland code”.
  - See: `docs/276-kernel-module-policy-and-loading-as-evidence.md`.
- **Breakglass**: emergency exceptions are leases with explicit approvals and receipts.
  - See: `docs/236-breakglass-and-recovery-mode.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`.

## Open questions

- How far should enforcement go for interpreters (scripts)? Options:
  - enforce interpreter path only (minimum)
  - enforce script bytes via xattrs/sidecars + loader mediation (stronger)
- How do we represent “exec-from-memory” patterns (JITs)? Likely allow but constrain by promise profiles + W^X posture.
- Which backends should exist besides mac_veriexec?
  - “exec broker” mediation for platforms without mac_veriexec
  - optional per-jail capsicum mode (prevent opening/execing outside store view)

Last updated: 2026-02-26r92
