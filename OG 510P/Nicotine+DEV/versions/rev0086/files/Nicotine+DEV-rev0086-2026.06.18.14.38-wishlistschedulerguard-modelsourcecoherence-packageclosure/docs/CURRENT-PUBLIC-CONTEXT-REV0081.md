# Current public context — rev0081

Observed on 2026-06-18:

```text
public master head:       a96406e7aa285a3fb2a3e35900686d164a22bf02
bundled executable proxy: f4e17d59783dbc48ea31d2e899a681e2dd1ed500
visible distance:         6 commits / 8 changed files
```

The visible intervening commits concern platform rendering, translations, website/contribution documentation, and adjacent maintenance. Public master still uses fresh tokens for normal searches, explicit add/remove response admission, mode-specific dispatch, and the GUI's pre-page display-cap check. The flow reviewed here is therefore still present, while executable whole-tree claims remain scoped to the supplied proxy.

Public issue #3326 requested that Search Again refresh the respective search. Rev0081 makes no novelty claim for fresh-token refresh as a broad direction. Its narrower result is the state-ownership proof that ordinary searches can retain one processed request and GUI page while rotating the wire-response token.

The public wishlist design separately establishes seen-result persistence: users are considered seen only when an unread wishlist tab is opened, and Reset Seen Results is the explicit way to admit all results again. That makes automatic wishlist rekey/clear a product-policy change, not a mechanical extension of the ordinary path.

Online-source inventory: `manifests/web-references-rev0081.md` and `.json`.

All generated code, tests, tools, and prose remain research-only under the project's contribution boundary.
