# Web references — rev0083

Observed 2026-06-18. Executable claims remain bound to the supplied source
bundle; public sources establish current flow and feature intent.

| ID | Source | Use |
|---|---|---|
| `master-commit-history` | `https://github.com/nicotine-plus/nicotine-plus/commits/master/` | observed public head and proxy distance |
| `current-search-source` | `https://raw.githubusercontent.com/nicotine-plus/nicotine-plus/master/pynicotine/search.py` | `SearchRequest`, `WishSearchRequest`, `do_search`, and response ownership |
| `current-wishlist-dialog` | `https://raw.githubusercontent.com/nicotine-plus/nicotine-plus/master/pynicotine/gtkgui/dialogs/wishlist.py` | manual wishlist actions call `do_search(..., mode="wishlist")` |
| `current-search-gui` | `https://raw.githubusercontent.com/nicotine-plus/nicotine-plus/master/pynicotine/gtkgui/search.py` | wishlist mode, notifications, filters, and seen-history token check |
| `current-application-gui` | `https://raw.githubusercontent.com/nicotine-plus/nicotine-plus/master/pynicotine/gtkgui/application.py` | notification activation performs exact token lookup |
| `search-again-issue-3326` | `https://github.com/nicotine-plus/nicotine-plus/issues/3326` | public feature intent: refresh the respective search |
| `contribution-policy` | `https://github.com/nicotine-plus/nicotine-plus/blob/master/CONTRIBUTING.md` | research-only AI-use boundary |

Machine-readable mirror: `manifests/web-references-rev0083.json`.
