# WISHLIST-CAP-01 current disposition — rev0086

```text
status: open-subscription-cap-lifecycle-research
selected patch: none
security route: not applicable
```

## Confirmed behavior

A persistent wishlist result page has finite display capacity, but the
scheduler does not know that the page is full. Each later scheduler turn can:

1. set the wish active;
2. add response admission;
3. send a server `WishlistSearch`;
4. reach the GUI with an otherwise-admissible peer response;
5. have that response discarded at the cap and admission removed again.

The rev0086 model exercises twelve repeated turns after capacity and observes
thirteen scheduled requests in total, twelve capacity drops, and no additional
visible row.

## Impact boundary

This supports a low-severity subscription lifecycle and resource-hygiene
finding: recurring request/parse/UI work can continue while the open inbox has
no capacity. It does not establish remote control of the schedule, material
amplification, or a practical denial-of-service threshold.

## Missing policy

A correct fix needs an explicit user-visible lifecycle:

- pause the wish while its delivered batch is full;
- archive/close a reviewed batch and resume into a new batch;
- evict old rows under a bounded, explained rule; or
- another design that preserves unread results and durable seen history.

Automatic clearing is not selected because it can discard unread results.
Pausing is not selected because resume/reconnect/persistence behavior is still
undefined. Native GTK and long-running workload evidence are also missing.
