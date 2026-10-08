# rev0013 SEARCH-RESP-01 current-behavior probe

All checks passed across the three archived source lanes. This is a current-behavior witness, not a fixed-behavior test.

## Summary table

| check | github-tag-3.3.10 | github-branch-3.3.x | github-branch-master |
|---|---:|---:|---:|
| `u163_room_scoped_search_accepts_unvetted_peer` | pass | pass | pass |
| `u163_token_shape_reduced_initial_range_then_linear_increment` | pass | pass | pass |
| `u163_user_scoped_search_accepts_unrequested_peer` | pass | pass | pass |
| `u262_private_result_rows_are_parser_materialized_before_display_policy` | pass | pass | pass |
| `u266_support_accepted_response_parser_materializes_full_public_list` | pass | pass | pass |
| `u267_invalid_token_decompresses_username_prefix_before_reject` | pass | pass | pass |

## Notable measured values

- github-tag-3.3.10: invalid-token probe compressed 1004 bytes into a declared 1000000-byte username prefix; `tracemalloc_peak_bytes=2042258`, elapsed `3.799` ms.
- github-branch-3.3.x: invalid-token probe compressed 1004 bytes into a declared 1000000-byte username prefix; `tracemalloc_peak_bytes=2042258`, elapsed `3.761` ms.
- github-branch-master: invalid-token probe compressed 1004 bytes into a declared 1000000-byte username prefix; `tracemalloc_peak_bytes=2042360`, elapsed `3.807` ms.
- github-tag-3.3.10: sampled starting tokens were within `0..4294967` and `increment_token(123456)` returned `123457`.
- github-branch-3.3.x: sampled starting tokens were within `0..4294967` and `increment_token(123456)` returned `123457`.
- github-branch-master: sampled starting tokens were within `0..4294967` and `increment_token(123456)` returned `123457`.

## Interpretation

- U-163 is confirmed as a source/scope binding issue at the search-response acceptance boundary: user-scoped and room-scoped search records were accepted from unrequested/unvetted peers as long as the response token was allowed.
- U-262 is confirmed only as a parser-ordering support fact: private rows are materialized before the GUI display preference decides whether to show them.
- U-267 is confirmed only as a parser-budget support fact: invalid-token rejection happens after the compressed username prefix has been decompressed enough to read the token.
- U-266 is confirmed only as a parser/materialization support fact: an accepted response can materialize 256 public rows before the UI cap path sees the row list.
