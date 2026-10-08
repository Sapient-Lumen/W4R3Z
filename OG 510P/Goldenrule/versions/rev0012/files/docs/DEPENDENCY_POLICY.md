# Dependency Policy

Concord uses a tranche-based dependency hygiene posture.

## Policy

- Dependency/security checks run via adapter scripts under `scripts/tools/`.
- Missing tools are warnings in `make gate` and failures in `make gate-strict`.
- Allowlist entries require expiration dates and auditable rationale.

## Cadence

- Perform periodic dependency review in dedicated tranches.
- Keep release-candidate runs in environments with strict security tools available.
