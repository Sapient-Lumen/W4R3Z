# RFC-0097: User environments (Home-Manager analogue)

## Summary
Define a user-scoped derived environment (packages + dotfiles + small per-user activation) with ZFS-backed generations.

## Motivation
For serious users, “my computing environment is derived” includes userland, not just the host.

## Proposal
- UserEnv is derived via the same closure/policy machinery
- activation affects only user-owned state
- reversible generations via ZFS snapshots

See: `docs/162-user-environments.md`.
