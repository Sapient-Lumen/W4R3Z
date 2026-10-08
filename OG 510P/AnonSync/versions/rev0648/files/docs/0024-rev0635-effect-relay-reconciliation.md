# rev0635 effect relay reconciliation

## Why this was the next risky work

Rev0633 made prepared effects dispatchable by inserting `effect_outbox` rows in the same SQLite transaction as accepted prepared ledger entries. Rev0634 made those rows claimable with worker leases and stale-lease reclaim. The remaining high-risk gap was after dispatch: a worker could claim a row, perform a downstream effect, crash before terminal evidence, and later leave the system with only an expired local lease.

Rev0635 adds a narrow local relay/reconciliation harness to make that gap executable and testable.

## New boundary

The new relay-once path does this in order:

1. Atomically claim one `reserved` or stale `inflight` outbox row.
2. Apply or observe a row in a local downstream SQLite journal keyed by `effect_idempotency_key`.
3. Bind downstream result material to prepared sequence/hash evidence and terminal state.
4. Optionally inject a crash after downstream apply and before terminal evidence.
5. On a later run, stale-reclaim the inflight row, observe the existing downstream row, verify the result digest recomputes, and then close the effect through the existing signed transition-intent verifier.

The relay therefore does not gain a raw mutation path for terminal effects. It still signs and verifies a normal `anonsync-effect-transition-intent-v2-ledger-instance` payload against a digest-pinned trust profile before appending terminal evidence.

## New formats and commands

- Relay report: `anonsync-sqlite-effect-relay-report-v1`
- Downstream journal: `anonsync-relay-downstream-store-v1`
- Downstream result material: `anonsync-relay-downstream-result-v1`
- Active backend capability format: `anonsync-ledger-backend-capabilities-v30`

New CLI surface:

```text
--ledger-effect-relay-report <relay.json>
--ledger-effect-relay-downstream-store <downstream.sqlite>
--ledger-effect-relay-worker-id <worker>
--ledger-effect-relay-now-epoch <epoch>
--ledger-effect-relay-lease-seconds <seconds>
--ledger-effect-relay-terminal-state <applied|failed|compensated>
--ledger-effect-relay-signer-private-key-pem <key.pem>
--ledger-effect-relay-signer-kid <kid>
--ledger-effect-transition-trust-profile <trust.json>
--ledger-effect-transition-trust-profile-sha256 <hex>
--ledger-effect-relay-inject-crash-after-downstream
```

## Audit/refactor performed

The focused refactor was deliberately tied to the risky path. Test-only base64url and RS256 signing helpers in `reporting_selftests.cpp` now call the production helpers in `json_codec_crypto.cpp`. This removes duplicate cryptographic encoding/signing logic from the selftest translation unit while keeping the test fixtures deterministic.

The larger structural problem remains: `sqlite_replay_ledger.cpp` and `reporting_selftests.cpp` are still too broad and should be split by domain once the production API/adapter boundary is no longer moving.

## Tamper check added during review

The first relay implementation treated any lower-hex downstream result digest as acceptable for an existing row. That was too trusting: a local downstream journal tamper could feed an arbitrary digest into terminal signing. Rev0635 now recomputes the expected downstream result digest from the prepared evidence and existing terminal state before signing terminal evidence.

The package validator exercises this by creating a crash gap, modifying the downstream `result_digest_sha256`, and confirming stale-lease recovery refuses to sign the tampered result.

## Residual risk

This is still a local adapter harness, not real external delivery. It does not prove that Stripe, S3, a queue, a webhook receiver, or any other downstream service performed an effect. Production adapters need downstream-specific idempotency keys, response/result verification, timeout and unknown-state handling, retry budgets, credential isolation, path/key configuration from operator policy, and observability around ambiguous terminal outcomes.

The relay also still receives signer key path, trust profile path, time, and downstream path by CLI. That is suitable for a cube selftest but not for the eventual enforcement boundary. The next major step should be a narrow production API and operator-owned configuration handle, not another manifest version.
