# WISHLIST-SCHED-01 current disposition — rev0086

## Disposition

```text
behavior: confirmed on exact public-master file content
impact: low-severity preference-enforcement, privacy, and recurring resource hygiene
remote trigger: none established
security threshold: not established
selected research correction:
  maintainer_artifacts/wishlist-scheduler-01/wishlist_scheduler_enabled_only_rev0086.patch
status: closed-research-disposition
```

This is research evidence, not upstream contribution material.

## Current behavior

`Search._do_next_wishlist_search()` rotates through at most the full wishlist and
breaks when it finds an item with `auto_search=True`. The post-loop dispatch,
however, tests only whether a request was encountered:

```python
if search is not None:
    search.is_ignored = False
    self._do_wishlist_search(search)
```

When every item is disabled, `search` is the final rotated item. The method
therefore reactivates and transmits a disabled term once per server-provided
wishlist interval. With a single disabled wish, that wish is transmitted every
interval.

The exact-source witness establishes:

```text
single disabled request:
  current selected:   disabled
  candidate selected: none

three disabled requests, four intervals:
  current selected:   c, c, c, c
  candidate selected: none, none, none, none
```

The current full rotation preserves mapping order, so the same final disabled
item is repeatedly selected rather than round-robin scheduling all disabled
items.

## Narrow correction

The selected research correction changes only the final eligibility test:

```diff
-if search is not None:
+if search is not None and search.auto_search:
```

It preserves the existing bounded scan, mapping rotation, first-enabled
selection, and enabled-item round robin. It prevents a request that failed the
eligibility search from becoming the fallback dispatch.

## Evidence

```text
source/model differential checks: exact parity in current and candidate states
research tests:                 30/30 pass
baseline upstream units:        60 passed, 1 skipped
candidate upstream units:       60 passed, 1 skipped
candidate production files:     1
candidate source hunks:          1
```

The relevant behavior was introduced with the wishlist overhaul commit
`91296257c7a5cba0c1b2cc6da905b92616e3dfa6` and remains in exact public-master
content `a96406e7aa285a3fb2a3e35900686d164a22bf02`.

## Scope and severity

The user controls `auto_search`; the defect violates that local preference and
causes recurring query disclosure and traffic for one disabled term. No remote
party was shown to toggle the setting, accelerate the server interval, or turn
this into a material denial-of-service condition. It should therefore remain a
normal correctness/privacy/resource-hygiene fix rather than a security claim.

## Public-overlap boundary

A bounded search of current public issues and the wishlist-overhaul history
found adjacent wishlist notification, seen-state, and scheduler discussions but
not this all-disabled fallback. This is not a novelty claim; it is only the
record of the bounded search performed for rev0086.
