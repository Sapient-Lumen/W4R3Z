# Security model (ridiculously secure from day 0)

DeriveBSD treats security as a **first-order design constraint**, not a hardening pass.

## Threat model (initial)

We assume:
- network paths and mirrors can be hostile (MITM, cache poisoning attempts)
- some upstream sources are compromised or malicious
- some builders may be compromised (untrusted CI, hostile build host)
- local users may be untrusted (multi-user machines)

We aim to:
- prevent untrusted binaries/sources from entering the store silently
- constrain build-time compromise from becoming runtime compromise
- enable strong auditability and rapid rollback
- reduce ambient authority of tools and services

## Core security invariants

See also: `docs/97-non-negotiable-behaviors.md` (day-0 defaults).

1. **No unauthenticated artifacts** (hash-verify; cache artifacts signature-verify)
2. **Policy is explicit and enforced**
3. **Builders are treated as adversarial by default**
4. **Activation is atomic and safe**
5. **Least privilege everywhere**

## Secure-by-default means

- Sandbox on by default (jail backend on FreeBSD).
- Network denied for builds by default (except declared fetchers).
- Trust roots are minimal and user/org controlled.
- No implicit downloads; sources pinned in Lock with hashes.
- Provenance metadata for every artifact.

Pointers:
- verification checklist: `docs/92-verification-matrix.md`
- hostile builder stance: `docs/91-hostile-builders.md`
- closure proofs: `docs/90-closure-proof.md`

Last updated: 2026-02-23
