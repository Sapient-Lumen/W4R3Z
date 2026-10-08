# WISHLIST-INBOX-01 research packet

This packet distinguishes a persistent `WishSearchRequest` subscription from a
page-owned search request.

It contains:

- `wishlist_inbox_model.py`: bounded state-machine model of scheduler, parser,
  core, GUI-cap, read, close, and seen-user transitions;
- `test_wishlist_inbox_model.py`: executable counterexamples and policy tests;
- `test_wishlist_inbox_source_semantics.py`: source-backed ownership checks.

The rev0085 cumulative candidate remains research-only. It hides and guards the
inherited **Search Again** action for persistent wishlist pages while retaining
fresh-token refresh for ordinary and manual-wishlist `SearchRequest` pages. It
does not solve the independent long-lived scheduler-at-cap lifecycle problem.
