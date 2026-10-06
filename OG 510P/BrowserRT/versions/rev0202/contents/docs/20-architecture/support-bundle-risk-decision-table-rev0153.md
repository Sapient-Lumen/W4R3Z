# Support-bundle risk decision table — rev0153

Runtime head remains rev0125 / `0.0.125` / OPFS Raw Composite AbortSignal. This linked rev0153 table is product guidance, not a runtime promotion.

The table compresses the recovery product into rows an operator can act on. Each row should eventually become a generated fixture and verifier result.

| State | Evidence required in support bundle | Safe automatic retry? | Required verification before retry | Stop/manual-review condition | Non-claim that must be shown |
| --- | --- | --- | --- | --- | --- |
| Pre-mutation admission rejection | admission row, budget/quota/posture refusal reason, no OPFS mutation receipt | yes, after caller changes budget/input/posture | prove no mutation receipt and no quarantine row for the operation id | missing admission row or ambiguous operation id | no quota reservation or persistent-storage grant |
| Provider abort before grant | AbortSignal fired before provider grant, no staged write, no digest | yes, if caller still wants operation | prove provider grant never happened and lane health is still healthy | abort/grant ordering is missing | AbortSignal is cancellation intent, not durability evidence |
| Provider abort after grant | provider grant timestamp, staged or raw OPFS attempt, digest/prefix or quarantine evidence | no automatic retry | Web Lock drain; verify committed digest/prefix or quarantine ledger; require idempotent caller review | digest mismatch, missing prefix, or unsettled quarantine | no rollback/no-mutation-after-dispatch/exactly-once claim |
| Quota/storage posture refusal | `navigator.storage.estimate()`/posture row, quota or persistence refusal, no mutation receipt | maybe, only after user frees space or changes policy | repeat storage posture and verify no partial OPFS mutation | quota failure after write attempt without digest/prefix evidence | no eviction survival or quota reservation claim |
| Web Lock timeout before mutation | lock request timeout, no provider grant, lock query/drain evidence | yes, with backoff and unchanged operation id | verify no holder mutation and no quarantine entry | lock holder unknown or query unavailable | no Web Lock fairness/starvation-freedom claim |
| Web Lock timeout after provider dispatch | holder identity, timeout, later settlement/quarantine candidate | no automatic retry | Web Lock drain plus digest/prefix verification; require quarantine review fingerprint | timed-out candidate exists without review fingerprint | timeout is not provider cancellation |
| Service Worker fetch response returned while `waitUntil` work continues | fetch response timestamp, Service Worker route, waitUntil marker, Web Lock holder record | no automatic retry | wait for lock drain; verify waitUntil late-failure marker and storage digest/prefix or quarantine row | response is treated as success without waitUntil settlement evidence | fetch response is not storage settlement |
| Service Worker update race | v1/v2 worker identity, `updateViaCache: 'none'`, old holder state, v2 put/read evidence | no automatic retry | close/drain old worker target, verify v2 write result and absence/presence of timeout marker | old worker still holds lock or identity is ambiguous | no Service Worker update algorithm completeness claim |
| Service Worker shutdown boundary | browser process/profile teardown evidence, lock query after relaunch, recovery/verify row | no automatic retry | relaunch, query locks, verify OPFS digest/prefix, then mark reviewed | profile/process cleanup is ambiguous or lock state cannot be queried | no browser-shutdown durability claim |

## Implementation wedge

The next useful product slice is a tiny verifier that accepts one support-bundle row and returns:

- `retry`: pre-mutation refusal only, no mutation/quarantine evidence.
- `verify-first`: mutation may have happened; require digest/prefix or quarantine review before retry.
- `stop/manual-review`: evidence is missing, ambiguous, stale, or contradicts itself.

## Non-claims

This table is not a production runbook and does not prove cross-browser behavior, Service Worker lifetime guarantees, OPFS fsync/power-loss durability, quota/eviction survival, persistent-storage retention, provider rollback, no-mutation-after-provider-dispatch, or exactly-once semantics.
