# rev0638 profile-bound ingress reservation

## Why this revision exists

Rev0637 made the relay handle-bound, but the reservation side still looked like a local harness: the caller could invoke the core runner with controls, contracts, backend capability pins, ledger path, ledger mode, policy envelope, reset behavior, and synthetic time. That was useful for testing and restore work, but it was the wrong boundary for a production-shaped authorization-to-effect path.

The next risky step was therefore to create a narrow ingress reservation surface that accepts an already authenticated context plus a caller-facing handle, while the operator-owned profile supplies all paths, digests, backend choices, and policy constraints before any durable append occurs.

## New ingress surface

The new command is:

```bash
anonsync_core \
  --ingress-profile <profile.json> \
  --ingress-profile-sha256 <lowercase-sha256> \
  --ingress-request <request.json> \
  --ingress-report <report.json>
```

The profile format is `anonsync-ingress-reservation-profile-v1`. Each enabled handle binds:

- `controls_path` and `controls_sha256`
- `contracts_path` and `contracts_sha256`
- `ledger_path`
- `ledger_backend`
- `ledger_commit_mode`
- `ledger_backend_capabilities_path` and `ledger_backend_capabilities_sha256`
- `policy_envelope_key`
- `ledger_mode`

The request format is `anonsync-ingress-reservation-request-v1`. It may contain only:

- `format`
- optional `revision_id`
- `request_id`
- `config_handle`
- `authenticated_context`
- `case`

The `authenticated_context.transport_authenticated` flag must be true. Rev0638 does not claim to perform transport authentication; it requires evidence from the caller boundary and binds the full request digest into the ingress report.

The report format is `anonsync-ingress-reservation-report-v1`. A successful report binds:

- profile SHA-256
- request SHA-256
- controls, contracts, and backend capability digests
- kernel report digest
- pending-effect report digest
- durable ledger head and line count
- prepared row sequence/hash
- effect idempotency key
- reserved outbox state

## Behavior now covered

The rev0638 package validator covers:

1. Successful profile-bound durable reservation with one reserved outbox row.
2. Duplicate replay rejection without increasing durable line count.
3. Profile digest mismatch rejection before append.
4. Disabled handle rejection before append.
5. Duplicate handle rejection before append.
6. Request operator-field injection rejection before append.
7. Request metadata attempting to select a failure ledger mode rejected before append.
8. v32 backend capability downgrade rejection before append.

The command also rejects request-selected failure injection, replay preseed, stale-JWKS selection, top-level operator fields, controls/contracts/capability digest drift, non-`sqlite-wal` durable reservation backend, and non-`normal` production-boundary ledger mode.

## Audit/refactor note

The useful refactor was deliberately narrow. Rev0638 centralizes the ingress profile selection object, common case-insensitive JSON field helpers, a top-level ingress request allowlist, and shared ingress report rendering. This reduces the chance that later code reintroduces path/clock/proof-secret selection through request JSON.

The larger cleanup remains true: `sqlite_replay_ledger.cpp` and `reporting_selftests.cpp` are still too large and mix production logic, report generation, test key generation, relay harnesses, and hostile corpora. Broad file splitting was deferred behind the more important request-to-reservation boundary.

## Residual risk

This is still not a deployed service. The profile is a local JSON file pinned by a command-line digest, not a signed operator control plane. The command does not terminate TLS, verify client proof-of-possession, enforce a trusted runtime clock, or own distributed replay horizons. It still relies on fixture HMAC proof binding rather than DPoP/mTLS-style sender possession. It returns a local reservation and outbox evidence, not proof that an external downstream system performed an effect.

The next risky work is to move from CLI/file ingress toward a real service or library API boundary with authenticated operator configuration, sender possession, resource limits, and real downstream unknown-outcome semantics.
