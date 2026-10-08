# rev0636 configured relay boundary

## Why this revision exists

Rev0635 closed a concrete crash gap: a worker could touch downstream state and crash before terminal evidence was appended. Its relay could later stale-reclaim the lease, observe the downstream row, verify prepared evidence/result digest, and close terminal evidence through the signed transition-intent path.

The remaining risk was that the relay command itself still selected too much security-critical material: downstream path, worker id, lease duration, terminal state, signer key path, signer key id, transition trust profile path, and trust-profile digest. That was acceptable as a harness, but not as the next production boundary. A request or ad hoc invocation should not be the source of those choices.

Rev0636 adds a configured relay path. The command now accepts a relay adapter config path and expected SHA-256 digest. The config must verify before any claim is attempted.

## New configured surface

The configured command is:

```bash
anonsync_core \
  --ledger <ledger.sqlite> \
  --ledger-effect-relay-report <relay.json> \
  --ledger-effect-relay-config <adapter-config.json> \
  --ledger-effect-relay-config-sha256 <lowercase-sha256> \
  --ledger-effect-relay-now-epoch <epoch>
```

The config format is `anonsync-effect-relay-adapter-config-v1`. It binds:

- `adapter_id`
- `adapter_kind` (`local-sqlite-downstream-journal` in rev0636)
- `downstream_store_path`
- `worker_id`
- `lease_seconds`
- `terminal_state`
- `signer_private_key_pem_path`
- `signer_kid`
- `transition_trust_profile_path`
- `transition_trust_profile_sha256`
- an explicit debug flag for the injected-crash test hook

The configured relay report format is `anonsync-sqlite-effect-relay-report-v2-configured-boundary`. Reports include `relay_adapter_config.format`, `adapter_id`, `adapter_kind`, `config_sha256`, and `digest_pin_verified`.

## Behavior now covered

The rev0636 selftest and package validator cover:

1. Config digest mismatch rejection before claim.
2. Injected crash after downstream apply, leaving one inflight row and one downstream observation.
3. Fresh-lease no-double-claim behavior.
4. Stale-lease reclaim through the same configured adapter identity.
5. Existing downstream result digest recomputation before terminal closure.
6. Signed transition evidence whose reason includes the adapter config digest.
7. Capability downgrade rejection from v31 to v30.
8. v31 capability rejection when configured-boundary booleans are missing or false.

## Audit/refactor note

The useful refactor this round was deliberately narrow: report rendering for legacy/configured relay now shares a single implementation with a configured report switch, and validator coverage moved from the direct relay harness to the configured path. This avoids spending the turn on broad file choreography while still reducing drift in a high-risk path.

The larger cleanup remains true: `sqlite_replay_ledger.cpp` and `reporting_selftests.cpp` are still too large and mix production logic, report generation, test key generation, harnesses, subprocess-like orchestration, and hostile corpora.

## Residual risk

This is not yet a production adapter boundary. The config is a local JSON file pinned by a command-line digest, not an authenticated operator object resolved from a stable handle. The local downstream journal is still a deterministic simulation, not an external effect. The relay key is loaded from a filesystem PEM path rather than hardware-backed or service-managed key custody. Unknown external outcomes, real retry budgets, downstream-specific idempotency contracts, and reconciliation against an authoritative remote API remain unfinished.

The next risky work is a narrow production ingress/configuration API: requests should provide authenticated context and an operator-selected config handle, not paths or security material. The configured relay is the first step toward that boundary, not the boundary itself.
