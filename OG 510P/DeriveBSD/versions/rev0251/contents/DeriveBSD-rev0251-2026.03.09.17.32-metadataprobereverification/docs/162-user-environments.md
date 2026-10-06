# User environments: Home-Manager-like, derived and reversible

Nix pros often treat the *user environment* as part of the system:
- dotfiles
- per-user packages
- per-user services

DeriveBSD should support this as a derived artifact type without weakening the host security posture.

## Concept

A **UserEnv** is a derived object similar to a DevShell, but intended to be:
- persistent for a user
- reversible (generations)
- activated without mutating the base host closure

## v0 shape (recommended)

- A per-user ZFS dataset with **generations** (snapshots) managed by Derive.
- UserEnv activation updates:
  - a profile directory (symlink or mount) and
  - a small set of user-facing entrypoints (PATH, shells, editor integration)

UserEnv is *not* privileged system configuration.

## Safety defaults

- no elevation: UserEnv cannot grant new system authority
- no secrets by default: secret use goes through the credential broker
- provenance is recorded: “why is this tool here?” is answerable

## Relationship to DevShell

- DevShell is ephemeral and project-scoped.
- UserEnv is persistent and user-scoped.

They should share the same closure and policy machinery.

See also: portable home areas + embedded user records (`docs/269-portable-home-areas-and-user-records.md`).

## Non-goals (v0)

- replacing all of FreeBSD user management
- making user envs a backdoor to host mutation

Last updated: 2026-02-27r109
