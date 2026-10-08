# Current public context — rev0083

Observed on 2026-06-18:

```text
public master head:       a96406e7aa285a3fb2a3e35900686d164a22bf02
bundled executable proxy: f4e17d59783dbc48ea31d2e899a681e2dd1ed500
visible distance:         6 commits / 8 changed files
```

Current public `search.py` retains the relevant distinction: `do_search()` uses
`_add_search()` even for mode `wishlist`, while persistent wishes use
`_add_wish_search()` and `WishSearchRequest`. Current public GUI source retains
wishlist-mode token notifications and exact-token activation. The relevant
flow therefore matches the executable proxy, but executable claims remain bound
to the supplied bundle rather than presented as exact public-head execution.

Public issue #3326 describes Search Again as refreshing the respective search.
Rev0083 makes no novelty claim for that broad feature. Its contribution is the
manual-wishlist hybrid ownership counterexample, a single-owner eligibility
correction, and immutable candidate lineage.

Online-source inventory: `manifests/web-references-rev0083.md` and `.json`.
