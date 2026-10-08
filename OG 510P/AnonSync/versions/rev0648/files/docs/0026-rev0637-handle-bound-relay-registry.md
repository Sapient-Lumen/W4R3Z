# rev0637 handle-bound relay registry

## Why this revision exists

Rev0636 moved the relay from per-invocation downstream, signer, trust, worker, lease, and terminal-state arguments to a digest-pinned adapter config. That was useful but still left the caller with a config path and config digest. The next risky boundary was therefore not another transition state or restore check; it was reducing the production-facing relay selection surface to a stable handle.

Rev0637 adds a handle-bound relay command. The caller-facing selector is a `config_handle`; an operator-pinned registry resolves that handle to exactly one enabled digest-pinned adapter config. Registry digest mismatch, missing handle, disabled handle, duplicate handle, adapter identity mismatch, and adapter config digest mismatch all fail before any outbox claim.

## New handle-bound surface

The new command is:

```bash
anonsync_core \
  --ledger <ledger.sqlite> \
  --ledger-effect-relay-report <relay.json> \
  --ledger-effect-relay-registry <registry.json> \
  --ledger-effect-relay-registry-sha256 <lowercase-sha256> \
  --ledger-effect-relay-config-handle <handle> \
  --ledger-effect-relay-now-epoch <epoch>
```

The registry format is `anonsync-effect-relay-config-registry-v1`.

Each enabled registry entry maps a printable, control-free handle to:

- `adapter_config_path`
- `adapter_config_sha256`
- optional `adapter_id` consistency check
- optional `adapter_kind` consistency check

The resolved adapter config remains `anonsync-effect-relay-adapter-config-v1`; it still binds downstream store path, worker id, lease, terminal state, signer key path/id, and transition trust profile pin.

The new relay report format is `anonsync-sqlite-effect-relay-report-v3-handle-boundary`. It includes both:

- `relay_config_registry`: registry format, config handle, registry SHA-256, and digest-pin verification result
- `relay_adapter_config`: adapter config format, adapter id, adapter kind, config SHA-256, and digest-pin verification result

## Behavior now covered

The rev0637 selftest and package validator cover:

1. Registry digest mismatch rejection before claim.
2. Crash after downstream apply through the handle-bound path.
3. Fresh-lease no-double-claim behavior.
4. Stale-lease reclaim and downstream replay observation.
5. Signed terminal closure whose reason binds handle, registry digest, adapter id, adapter config digest, worker, and claim id.
6. Registry content drift rejection after digest pinning.
7. Missing, disabled, and duplicate handle rejection.
8. Downstream result-digest tamper rejection before terminal evidence is signed.
9. Capability downgrade rejection from v32 to v31.
10. v32 capability rejection if registry-boundary booleans are missing or false.

## Audit/refactor note

The useful refactor this round was narrow and path-specific: relay report rendering now emits legacy v1, configured v2, and handle-bound v3 from one implementation, with registry evidence controlled by the same report result object rather than a separate JSON-rendering fork. The package validator now targets the handle-bound path as the active production-shaped surface.

The larger cleanup remains true: `sqlite_replay_ledger.cpp` and `reporting_selftests.cpp` are still too large and mix production logic, report generation, test key generation, relay harnesses, and hostile corpora. Broad file choreography was deliberately deferred behind the more important request-to-effect boundary work.

## Residual risk

This is still not a complete production control plane. The registry is a local JSON file pinned by a command-line digest, not a signed, independently managed configuration service. The downstream adapter is still a deterministic local SQLite journal. The relay signer still loads a local PEM file rather than hardware-backed or service-managed key custody. Transport authentication, request possession, unknown external outcomes, remote retry budgets, and authoritative downstream reconciliation remain unfinished.

The next risky work is a narrow ingress/reservation API that accepts authenticated context plus an operator-selected policy/adapter handle and returns a durable reservation decision without allowing requests to choose paths, clocks, trust roots, signer material, proof secrets, or backend mode.
