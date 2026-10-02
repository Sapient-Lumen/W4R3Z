# ADR 0290: Add canonical Agent configuration and non-mutating preflight

- Status: accepted and implemented
- Date: 2026-09-01

## Context

The Agent has one mature parser but a deployment can require dozens of route, sync, update, Ratox,
resource, and laboratory options. Copying that argv into service definitions is error-prone. A
second INI/JSON/TOML object model would duplicate option semantics and eventually drift. Calling
`Agent::start()` to validate a candidate is unacceptable because startup prepares the runtime tree,
creates or advances durable identity/incarnation state, recovers stores, may create cgroups, and
constructs network listeners.

## Decision

Add canonical `iotox-agent-config-v1`, `config-lint`, `run --config`, and `run-check`.

The record is a bounded ordered sequence of `argument-NNNN=` fields with no shell evaluation.
No-follow owner-private stable reading precedes decoding. Non-repeatable duplicate options fail;
the five existing repeatable route/bootstrap families remain repeatable. Explicit command-line
groups replace same-named file groups before the existing Agent parser runs. `--config` is reserved
to the outer command and must be first.

Factor side-effect-free derived path normalization through `Agent::normalize_config`. Both `run` and
`run-check` invoke one `preflight_agent_config` after the existing parser. It loads providers,
checks managed path readiness, verifies an existing identity, reads policy stores, resolves terminal
profile executable/working-directory and cgroup prerequisites, and verifies signed route policy
through a new non-mutating `RouteSetStore::inspect`. The latter reads the rollback high-water record
without creating a lock or advancing it. The binary lifecycle process gate restarts the real Agent
through a config file and applies a command-line lifetime override.

`run-check` does not call recovery-capable durable-store opens. Existing authority, command, and
incarnation files receive strict private-shape inspection and are reported as
`runtime-recovery-pending`; only `run` may reconcile/adopt/migrate/advance them under their locks.
Final terminal seccomp/MDWE/Landlock proof also remains in the production child. Successful output
therefore says `ready-for-start`, names both deferrals, and promises no mutation—not successful
startup or future-state stability.

## Consequences

Operators can review, lint, override, preflight, and deploy one exact Agent policy without shell
quoting or parser duplication. Unsafe config ownership, symlinks, provider failures, invalid route
topology, missing policy stores, dead Ratox executables, update/namespace mismatch, and missing
cgroup interfaces fail before startup mutation. The format contains local paths and potentially
sensitive topology, so no automatic export command is provided. Agent/peer framing and authority
semantics are unchanged.
