# Verified execution (NetBSD veriexec / FreeBSD MAC/veriexec): research notes

Status: research / optional hardening, not required for v1.

Idea: strengthen “immutable intent” by having the kernel **refuse to execute or load unexpected bytes**.
This complements:
- sandboxing (jails/microVMs)
- signature verification at deploy time
- closure proofs / explainability

## Why this is interesting for DeriveBSD

DeriveBSD already makes the *desired* filesystem tree explicit (closure manifest).
Verified-exec style mechanisms offer a second line of defense:
- even if something writes a new binary onto disk, it can’t be executed
- even if root is compromised, the integrity policy can still block tampering (depending on mode)

## Prior art

- NetBSD’s Veriexec: in-kernel file integrity subsystem, with a signatures/fingerprints database and “strict levels”.
  - Guide chapter: https://www.netbsd.org/docs/guide/en/chap-veriexec.html
  - Man page: https://man.netbsd.org/veriexec.4

- FreeBSD MAC/veriexec: verified execution implemented as a MAC policy module.
  - Review trail / design notes: https://reviews.freebsd.org/D8554
  - Verifying manifest loader work: https://reviews.freebsd.org/D16575
  - TrustedBSD MAC framework overview: https://docs.freebsd.org/en/books/arch-handbook/mac/

## DeriveBSD direction (if adopted)

### 1) The allowlist is *derived* (not hand-authored)

- Generate a “verified exec manifest” from the **closure manifest** of a host generation / microVM bundle.
- Bind it to:
  - the generation id
  - the closure digest
  - the policy decision record digest

### 2) Keep the surface small

Start with a narrow scope:
- host base sets + DeriveBSD control-plane tools
- optionally: critical workload entrypoints (not every file)

### 3) Make exceptions explicit

If we need to allow runtime-produced executables (rare), require a policy-gated exception that shows up in:
- `derive explain`
- blast-radius diffs

## Open questions / risks

- Interaction with dynamic linking (how strict should library allowlists be?)
- Update/rollback UX when the integrity database is out of sync
- Operational recovery paths (forensics mode vs locked mode)

See also: `docs/103-runtime-verified-execution.md`.

Last updated: 2026-02-25
