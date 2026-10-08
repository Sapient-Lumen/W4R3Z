# Current public context — rev0084

Observed on 2026-06-18:

```text
public master head:       a96406e7aa285a3fb2a3e35900686d164a22bf02
bundled executable proxy: f4e17d59783dbc48ea31d2e899a681e2dd1ed500
visible distance:         6 commits / 8 changed files
```

The public head remains dated 2026-06-15. Current public source retains the
flow that matters here:

- manual wishlist actions call `do_search(..., mode="wishlist")`;
- `do_search()` creates a normal `SearchRequest`;
- persistent wishes use `WishSearchRequest`;
- wishlist result notifications carry the page's stringified wire token;
- activation parses that string back to an integer and performs exact-token
  lookup;
- generic Gio notifications are sent with no application notification ID.

The six intervening commits account for all eight changed files: three project
documents, one website workflow, one website configuration file, one
translation catalog, the Windows packaging script, and
`pynicotine/gtkgui/__init__.py`. None is one of the six candidate patch targets
or an upstream unit-test file. It is therefore reasonable to infer that the
candidate's target-file baseline is unchanged at `a96406e…`; this is still not
a local hash or whole-tree execution claim.

The executable claims remain bound to the supplied `f4e17d5…` proxy. Public
source and commit-scope review confirms the relevant ownership and notification
flow, but the cube does not claim exact whole-tree execution of `a96406e…`.

Public issue #3326 describes Search Again as refreshing the respective search.
Rev0084 makes no novelty claim for the feature; its contribution is the
wire-token/logical-page/desktop-notification identity split, lifecycle model,
and executable research prototype.

Online-source inventory: `manifests/web-references-rev0084.md` and `.json`.
