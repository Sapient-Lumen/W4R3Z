# Exec integrity policy + verified execution (MAC/veriexec backend)

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, supply-chain, operability  
**Patterns:** Plan→Apply→Receipt, Registry→Diff→Gate  

DeriveBSD already makes **artifacts immutable** and **inputs explicit**, but a system can still lose if arbitrary bytes can execute at runtime.
This lane makes “what is allowed to execute” a **typed, reviewable, compilable policy** with receipts.

The archive now fixes the authority boundary:

- `exec.integrity.policy` is the authoritative policy object,
- `exec.integrity.plan` is the compiled activation plan,
- `exec.integrity.receipt` is the authoritative activation result,
- `exec-verify-snapshot` / `exec-verify-event` are backend observation artifacts,
- and `exec.verify.policy.diff` is the drift surface for authoritative policy changes.

See: `docs/486-exec-integrity-authority-and-verified-execution-boundary.md`.

## Goals

- Provide a uniform policy object that answers:
  - **What bytes may execute?** (entrypoints, interpreters, dynamic loaders)
  - **In which scopes?** (host, service jail, AppVM, builders)
  - **What is the enforcement mode?** (`off` / `warn` / `enforce`)
- Compile the policy into one or more enforcement backends.
- Bind execution-integrity planning to runtime composition so launch evidence can answer:
  - which runtime manifest was active
  - which stratum stack / mount view owned interpreter + loader resolution
  - what backend enforced the result
- Emit receipts so incidents can answer:
  - what policy was active
  - what exceptions existed (and why)
  - whether execution drift was policy drift or backend-state drift

## Non-goals

- Building a new “Linux IMA clone” with bespoke kernel hooks.
- Preventing all in-memory code injection (this lane is about executable *origin* and *integrity*).
- Reintroducing ambient host fallback through scripts, loaders, or convenience symlinks.

## Background (why MAC/veriexec is interesting)

FreeBSD’s MAC Framework supports loadable policies. A notable policy is **MAC/veriexec**, a verified execution environment that can verify file integrity using metadata mappings. NetBSD Veriexec is the older conceptual anchor for “deny unexpected bytes,” and HardenedBSD’s Integriforce showed the same intent in a whitelist shape.

Official / primary references:
- FreeBSD MAC/veriexec review trail: https://reviews.freebsd.org/D8554
- NetBSD Veriexec guide chapter: https://www.netbsd.org/docs/guide/en/chap-veriexec.html
- HardenedBSD Integriforce overview: https://hardenedbsd.org/article/shawn-webb/2015-03-11/call-testing-secadm-integriforce
- FreeBSD verifying loader for `mac_veriexec`: https://reviews.freebsd.org/D16575

## Core idea

Introduce an **authoritative exec integrity policy** object:

- `exec.integrity.policy` (reviewed intent)
- `exec.integrity.plan` (compiled activation object)
- `exec.integrity.receipt` (authoritative activation result)

Schemas (v0.1):

- `spec/exec.integrity.policy.schema.json`
- `spec/exec.integrity.plan.schema.json`
- `spec/exec.integrity.receipt.schema.json`

Legacy alias objects remain only for compatibility with older archive material:

- `spec/exec.verify.policy.schema.json`
- `spec/exec.verify.receipt.schema.json`

## Policy model (v0)

### Scopes

A policy can target one or more scopes:

- `host`
- `service`
- `appvm`
- `builder`

### Allowed exec sources

Policy is expressed as a small set of sources:

- `store-only`
- `signed-bundle`
- `policy-allowlisted`
- `breakglass-only`

### Exceptions (must be explicit)

- allowlisted paths or digests (bounded)
- TTL-bound overrides
- each exception carries a reason and optional approval receipts

## The hard narrow rule for interpreters and loaders

The archive now decides the operable v0 rule:

- entrypoint bytes must come from an allowed source
- interpreters must resolve **within the active `mount.view`**
- dynamic loader resolution is **ABI-anchor-only**
- writable/quarantined bytes are denied in enforce mode unless an explicit exception says otherwise

That means script execution does **not** get to reopen host fallback.
The runtime-composition boundary from `docs/485-stratum-stack-and-runtime-composition-boundary.md` is part of execution-integrity planning now, not an unrelated concern.

## Compilation to a backend

An `exec.integrity.plan` compiles:

1. a backend-specific manifest / ruleset
2. a controlled activation step
3. a binding to runtime composition:
   - `runtime_manifest_digest`
   - `stratum_stack_digest`
   - `mount_view_digest`

Key constraints to keep:

- manifest update should be atomic with the activation boundary
- plan/receipt objects must be able to explain which runtime composition was enforced
- “attach a new binary somewhere writable and try again” is not the supported update story

## Drift and evidence

Authoritative policy drift is reviewed through `exec.verify.policy.diff`:

- the historic diff artifact name stays stable
- but the compared objects are `exec.integrity.policy` digests

Backend observation remains useful and separate:

- `exec-verify-snapshot`
- `exec-verify-event`

That separation is deliberate:
policy drift and backend-state drift are different operator problems.

## Interactions with other lanes

- **No mystery bytes:** origin/quarantine metadata becomes an execution guardrail, not just UI hints.
  See: `docs/280-origin-labels-and-quarantine-attributes.md`.
- **Runtime composition:** loader and interpreter resolution inherit `stratum.stack` / `mount.view`.
  See: `docs/485-stratum-stack-and-runtime-composition-boundary.md`.
- **Portable service bundles:** attaching a bundle updates the allowlist via plan+receipt, never by copying binaries into ad-hoc paths.
  See: `docs/265-portable-service-bundles.md`.
- **Kernel module policy:** “no surprise kernel code” pairs naturally with “no surprise userland code”.
  See: `docs/276-kernel-module-policy-and-loading-as-evidence.md`.
- **Breakglass:** emergency exceptions are leases with approvals and receipts.
  See: `docs/236-breakglass-and-recovery-mode.md`, `docs/288-multiparty-approvals-and-separation-of-duties.md`.

## Related docs

- `docs/486-exec-integrity-authority-and-verified-execution-boundary.md`
- `docs/233-verified-execution-as-evidence.md`
- `docs/442-exec-verify-policy-diff-as-review-surface.md`
- `spec/exec.integrity.policy.schema.json`
- `spec/exec.integrity.plan.schema.json`
- `spec/exec.integrity.receipt.schema.json`

Last updated: 2026-03-07r215
