# Current public context — rev0082

Observed on 2026-06-18:

```text
public master head:       a96406e7aa285a3fb2a3e35900686d164a22bf02
bundled executable proxy: f4e17d59783dbc48ea31d2e899a681e2dd1ed500
visible distance:         6 commits / 8 changed files
```

The visible head commit changes Windows packaging and GTK initialization, not search code. The intervening commits shown in public history concern translations, website/contribution documentation, and adjacent platform maintenance. Current public `pynicotine/search.py` retains fresh-token creation, token-keyed request lookup, mode-specific dispatch, and response lookup. Current public `pluginsystem.py` retains token-free outgoing search hook signatures.

Public issue #3326 describes Search Again as refreshing the respective search. Rev0082 makes no novelty claim for the broad idea of a refresh; its contribution is a source-backed token-consumer closure, a packet split between ordinary mechanics and wishlist semantics, and package-governance corrections.

Nicotine+ protocol documentation warns that the protocol is old, rigid, and compatibility-sensitive. The candidate therefore remains narrow: it does not alter wire formats or invent a new protocol message.

Online-source inventory: `manifests/web-references-rev0082.md` and `.json`.

All generated code, tests, patches, and prose remain research-only under the project's contribution boundary.
