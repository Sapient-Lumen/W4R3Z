# SEARCH-RESP room-scope coherence refactor — rev0043

## Refactor decision

Rev0043 finishes the held search-response source-set split by promoting a narrow room-mode sub-invariant. The room row is now explicitly modeled as a membership-snapshot gate, not a blanket room-response rejection policy.

## Canonical split after rev0043

```text
SEARCH-RESP-01A / U-163A: direct user-source binding — production-gated rev0039
SEARCH-RESP-01B-BUDDY / U-163B: buddy-source snapshot binding — production-gated rev0040
SEARCH-RESP-01C-ROOM / U-163C: room membership-snapshot binding when available — production-gated rev0043
SEARCH-RESP-PARSE-BUDGET-A: compressed username-prefix cap — production-gated rev0041
SEARCH-RESP-PARSE-BUDGET-B: accepted public/private result-list budget — production-gated rev0042
U-138: general ID3v2 advertised-frame materialization — deferred
```

## Boundaries maintained

- **Not parser budget:** rev0043 touches source admission in `search.py`, not compressed payload parsing in `slskmessages.py`.
- **Not UI display cap:** the room gate decides whether a peer response belongs to a room search token before display policy matters.
- **Not buddy mode:** buddy mode is local fan-out; room mode is server-mediated and uses a local membership snapshot only when available.
- **Not global/wishlist:** broad global and wishlist behavior remains outside this patch.
- **Not private-room authorization:** private-room membership/ownership/operation semantics remain in the chatroom state model. This patch only uses the current joined-room user set as an admission snapshot for a room search token.

## Audit effect

The strict/front lane now has no held search-response split rows. The only explicit deferred row left from the current queue is U-138, the general ID3v2 advertised-frame materialization target from the media-parser backlog.
