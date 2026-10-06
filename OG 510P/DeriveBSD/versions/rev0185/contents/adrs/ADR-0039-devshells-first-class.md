# ADR-0039: DevShells are first-class artifacts (nix-shell parity)

- Status: **accepted**
- Date: 2026-02-23

## Context
DeriveBSD must be usable as a primary computing environment. Nix pros treat `nix-shell` / `nix develop` as essential.

If DeriveBSD only produces “system images” and “workload images” but cannot provide fast, reproducible dev environments, it will fail to replace Nix for serious users.

## Decision
Introduce **DevShells** as a first-class Derive artifact type:

- DevShells are derived via Spec→Lock→Plan and produce evidence objects.
- Default executor is **jail-backed** (fast path).
- Optional executor is **microVM-backed** (higher isolation), using the same DevShellPlan.

Default posture:
- deny network unless policy grants
- no secrets in the shell; secret-bearing operations go through the credential broker
- store view minimization applies

## Consequences
- CLI must include `derive develop`, `derive shell`, and `derive run`.
- DevShell plan/explain/diff must be LLM-friendly (`--json` stable outputs).
- DevShells become part of the “non-negotiable behaviors” contract.

See: `docs/159-devshells.md`.
