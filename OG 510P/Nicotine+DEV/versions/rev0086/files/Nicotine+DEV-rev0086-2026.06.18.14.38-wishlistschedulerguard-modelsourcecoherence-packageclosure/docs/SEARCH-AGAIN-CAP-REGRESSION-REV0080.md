# Search Again result-cap regression — rev0080

## Source-backed state transition

| Stage | Token admission | Stored rows | Requests | New rows |
|---|---:|---:|---:|---:|
| Page reaches cap | may be allowed until next response | cap | prior search | 0 remaining capacity |
| Over-cap response | removed | cap | 0 | 0 |
| Search Again click | re-added | cap | 1 or recipient fan-out | 0 |
| First returning response | removed again | cap | already emitted | 0 |

The cap gate lives in the parent `Searches` dispatcher, before `Search.file_search_response()`. It therefore runs before the repeated-username check and before any row mutation.

## Bounded waste model

`data/rev0080_search_repeat_cap_waste.csv` enumerates click and recipient counts. Its largest control is:

```text
32 clicks × 100 recipients = 3,200 outgoing request objects
new display rows = 0
retire cycles = 32
```

This is a deterministic local request-count result, not traffic capture. Server coalescing, queue rejection, disconnect, recipient availability, and remote processing were not measured. The correct claim is bounded local work with no possible display benefit while the page stays at cap.

## Why the old clear path matters

The feature-introducing snapshot contained a separate **Clear All Results** action. That action reset `num_results_found`, cleared user tracking, re-allowed the token, and made a later resend capable of displaying rows. The wishlist overhaul removed this escape hatch.

Reintroducing it would repair usability but would not provide epoch separation. A delayed response from before the clear carries the same token and can enter the empty page. The cube therefore records manual clear as historical context, not as the selected fix.

## Test roles

```text
test_result_cap_regression.py
  first-response retirement, repeated fan-out, cap-before-username ordering

test_current_retry_merge.py
  retained rows, existing-user suppression, unseen-user merge

test_same_token_clear_counterexample.py
  capacity restoration versus delayed-response ambiguity

test_fresh_token_replacement.py
  old-token rejection, new capacity, explicit view-state carry

test_source_ownership.py
  exact current source predicates
```
