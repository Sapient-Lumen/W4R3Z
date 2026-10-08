# SEARCH-AGAIN-EPOCH-01 current disposition — rev0078

## Decision

```text
current Search Again semantics:
  same wire token
  no result clear
  one accepted response per username for the page lifetime
  response admission reopened until the normal result-limit path closes it

replacement refresh requires:
  stable logical search identity
  replaceable wire epoch token
  explicit token-to-logical route
  old/new parser-admission ordering
  result and per-user dedup clear at a defined commit point
  page-close, disconnect, reconnect, and rapid-repeat semantics

selected implementation: none
status: open public design research
security route: not applicable
```

## Confirmed source behavior

The bundled master proxy and current public master use one search token for several distinct roles: network request/response capability, core search-dictionary key, GUI page key, page instance field, notification target, show/remove argument, and self-search authorization bookkeeping. `Search Again` resends the existing page token and does not invoke the model-clearing path.

Neither obvious partial change is sound:

1. Clear while reusing the token: a late response from the prior request is indistinguishable from a new-epoch response.
2. Rotate only the token: core, GUI, notification, removal, and event owners that still use the old key become inconsistent or unreachable.

The public feature request described Search Again as a refresh, and its discussion already recognized that a real repeat needs removal and a different token. Rev0078 makes no novelty claim for that broad requirement. Its narrower contribution is the owner map, executable countermodels, and cross-thread lifecycle boundary.

## Result-cap edge case

At the displayed-result cap, Search Again re-allows the existing token. The first repeated response then reaches the cap check, removes admission, and returns before page processing. A full page therefore cannot meaningfully refresh under current same-page/no-clear behavior.

This is an ordinary product-correctness observation, not a security finding.

## Why no patch is selected

Three ordinary queue events—remove old admission, add new admission, send the new request—have no transaction result. When network queue processing is disabled, the callback silently ignores them.

The rev0078 model first strengthens this to one composite enqueue:

```text
try_enqueue_epoch(EpochBatch(remove_old, add_new, fanout))
  -> accepted | rejected
```

That supports immediate rollback when enqueue is rejected and preserves ordering when accepted. It is still insufficient. Upstream disables and drains the outgoing message queue on disconnect and clears response admissions. A batch can therefore be accepted, the main thread can clear and switch state, and the batch can disappear before network application.

A viable design needs at least one of these explicit contracts:

```text
network-applied acknowledgement before main-thread commit
pending-epoch replay/reconciliation after reconnect
an equivalent generation-aware state reconciliation protocol
```

The model preserves the accepted-then-cleared counterexample rather than disguising queue acceptance as durable publication. Selecting production code before this boundary is resolved would create pseudo-atomic behavior.

## Validation

```text
source invariants:       24/24 pass
research/model tests:    33/33 pass
compile checks:          13/13 pass
upstream units:          60 passed, 1 skipped
selected patch:          none
```

`test_i18n.py` was explicitly excluded because `msgfmt` is unavailable.

## Missing evidence and decisions

A maintainer still needs to choose Retry, Merge, or replacement Refresh semantics. A replacement design also needs native GUI tests, plugin/event compatibility review, wishlist behavior, reconnect restoration, close/cancel semantics, rapid-repeat policy, buddy-recipient epoch policy, and an applied-acknowledgement or reconciliation mechanism.

All generated files are research-only and are not contribution material.
