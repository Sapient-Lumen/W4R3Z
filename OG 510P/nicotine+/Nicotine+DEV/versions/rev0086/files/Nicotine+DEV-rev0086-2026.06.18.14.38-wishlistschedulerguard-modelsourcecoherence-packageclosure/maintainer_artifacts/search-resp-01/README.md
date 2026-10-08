# SEARCH-RESP active research artifacts — rev0076

The active files classify evidence by role instead of treating one green fixed-behavior suite as a disposition.

## SEARCH-RESP-01A

```text
search_resp_harness.py
  shared request, response, network-filter, and wire PeerInit helpers

test_search_resp_current_behavior.py
  exact-current direct-user behavior witnesses

test_search_resp_rev0039_policy.py
  policy encoded by the historical direct-user expected-set guard

test_search_resp_identity_counterexample.py
  expected username claimed in PeerInit passes the direct-user guard

test_search_resp_token_model.py
  bounded token-range and sequential-allocation observations
```

## SEARCH-RESP-01B

```text
buddy_search_harness.py
  shared buddy list, sender, and request helpers

test_search_resp_buddy_current_behavior.py
  exact-current supported-branch behavior witnesses

test_search_resp_buddy_rev0040_policy.py
  historical buddy snapshot and claimed-name policy

test_search_resp_buddy_identity_counterexample.py
  PeerInit claim and body-username compatibility boundary

test_search_resp_buddy_snapshot_presence.py
  absent versus present-empty snapshot behavior

test_search_resp_buddy_master_resend_epoch.py
  Search Again counterexample after buddy-list mutation
```

The pre-refactor buddy monolith is preserved byte-for-byte under `docs/archive/rev0075-active-search-resp-buddy/`. Historical files named `PRODUCTION-READY`, `SELECTED-PATCH`, or similar are provenance only. Current authority is `data/current_packet_dispositions.json`.

All generated material is research-only and must not be copied into an upstream contribution.
