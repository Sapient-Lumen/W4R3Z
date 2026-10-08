# Superseded packet index — rev0084

Current authority always comes from `data/current_packet_dispositions.json` and
its revisioned documents.

For Search Again:

```text
rev0081/rev0082 candidate
  search_again_fresh_token_rekey.patch
  superseded: did not separate notification identity

rev0083 candidate
  search_again_mode_owned_rekey_rev0083.patch
  superseded: conservatively trapped all wishlist-mode pages on same-token Retry

rev0084 candidate
  search_again_stable_notification_rekey_rev0084.patch
  current research prototype; unselected
```

Historical artifacts are retained byte-for-byte because prior evidence records
bind their paths and SHA-256 digests. The candidate-lineage contract rejects
silent mutation or ambiguous `current.patch` aliases.
