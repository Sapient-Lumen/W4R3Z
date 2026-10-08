# Persistent wishlist inbox ownership — rev0085

## Heart of the finding

A persistent wishlist entry is not merely a search page that happens to run
periodically. Three owners overlap:

| State | Owner | Lifetime |
|---|---|---|
| wish term, filters, auto-search setting, `ignored_users` | `WishSearchRequest` | persistent subscription |
| scheduler permission and `WishlistSearch` timing | core/server protocol | one scheduled turn at a time |
| rows, selection, unread importance, finite display capacity | GTK search page | one delivered result batch |

The inherited **Search Again** action belongs to the third surface but invokes
the ordinary page-search path. It re-allows the persistent token and sends a
normal global `FileSearch`, whereas automatic wishlist delivery uses the
server-throttled `WishlistSearch` path. It neither resets the subscription nor
creates a new page-owned request epoch.

## Why a generic refresh is wrong

The January 2026 wishlist overhaul deliberately made seen-result suppression
durable and exposed **Reset Seen Results** as a separate destructive command.
When a wishlist page is marked read, the current implementation stores sender
usernames in `ignored_users`. Future responses from those senders are rejected
in core before the GUI can compare individual files.

Consequences:

- clearing rows is not equivalent to resetting seen state;
- clearing `ignored_users` would silently invoke the separate reset command;
- rotating the persistent token would also require scheduler, reconnect, JSON
  persistence, close/reopen, and unread-result semantics;
- retaining the token and rows is only a resend, not the refresh requested by
  the original Search Again feature.

The source already provides the coherent manual alternative: the wishlist
dialog's **Search for Item** command creates an independent
`SearchRequest(mode="wishlist")` page. That page is page-owned, can use the
fresh-token rekey design, and does not mutate the persistent subscription's
seen history.

## Rev0085 candidate policy

```text
ordinary SearchRequest page
  Search Again visible
  fresh wire token
  same logical page and stable notification identity
  clear result-derived page state

manual wishlist SearchRequest page
  Search Again visible
  same fresh-token page refresh
  persistent wish state untouched

persistent WishSearchRequest result page
  Search Again hidden and callback guarded
  scheduler token and seen history untouched
  manual alternative remains Wishlist > Search for Item
```

This is a research candidate, not a selected upstream patch. Native GTK3/GTK4
validation and maintainer acceptance remain mandatory.

## Independent cap lifecycle defect

Removing the inherited manual action does not solve the deeper long-lived
subscription problem. At the display cap:

1. the scheduler reactivates the persistent request;
2. core adds response admission and sends `WishlistSearch`;
3. the first otherwise-admissible response reaches the GUI;
4. the GUI sees no capacity, removes response admission, and adds no row;
5. a later scheduler turn repeats the cycle.

The executable model demonstrates twelve such turns with twelve requests and
zero visible progress. This is bounded recurring waste and a stalled inbox, not
a demonstrated denial-of-service condition.

A separate policy must choose among pause-at-cap, explicit batch archive and
rollover, bounded eviction, or another visible lifecycle. Automatically
clearing unread rows is not acceptable evidence-based behavior.

## Coarse seen-state boundary

Current seen suppression is sender-level, not file-level. Once a visible result
from `alice` is marked read, a later response from `alice` containing a newly
shared or different matching file is rejected until **Reset Seen Results**.
This appears consistent with the implemented overhaul, but it is an important
product tradeoff and prevents the cube from describing `ignored_users` as an
ordinary deduplication cache.
