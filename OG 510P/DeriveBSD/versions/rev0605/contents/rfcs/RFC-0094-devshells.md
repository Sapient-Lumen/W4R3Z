# RFC-0094: DevShell artifacts and CLI

## Summary
Define DevShell as a first-class artifact type that provides `nix-shell` / `nix develop` parity while preserving DeriveBSD’s verifiability and hostile-code posture.

## Motivation
- day-to-day usability for developers
- reproducible, explainable toolchains per project
- a safe place to run untrusted build scripts

## Proposal

### Artifact types
- `devshell.spec` (schema-versioned; see `spec/devshell.spec.schema.json`)
- `devshell.lock`
- `devshell.plan`
- `devshell.activation` (ephemeral runtime)

### CLI
- `derive develop` (project default)
- `derive shell [pkgs…]` (ad hoc)
- `derive run <tool> -- <args…>`

### Executors
- default: jail-backed devshell
- optional: microVM-backed devshell

### Defaults
- network off unless policy grants
- no secrets in-shell; credential broker only
- store view minimization

## Open questions
- direnv-style integration (`cd` auto-entry)
- caching strategy for plan + env exports
- microVM file channel: virtio-9p vs alternative

See: `docs/159-devshells.md`, ADR-0039.
