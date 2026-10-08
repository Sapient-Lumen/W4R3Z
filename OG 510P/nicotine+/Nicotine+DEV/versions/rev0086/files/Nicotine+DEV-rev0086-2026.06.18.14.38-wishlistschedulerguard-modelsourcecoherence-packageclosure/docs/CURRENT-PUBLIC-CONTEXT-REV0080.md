# Current public context — rev0080

Captured on 2026-06-18.

## Source state

Public `master` visibly remains at `a96406e7aa285a3fb2a3e35900686d164a22bf02`, dated 2026-06-15. The bundled executable proxy is `f4e17d59783dbc48ea31d2e899a681e2dd1ed500`, dated 2026-06-12. The visible intervening changes do not alter the Search Again, result-cap, username-deduplication, or new-search flow used here.

References:

- <https://github.com/nicotine-plus/nicotine-plus/commits/master/>
- <https://github.com/nicotine-plus/nicotine-plus/compare/f4e17d59783dbc48ea31d2e899a681e2dd1ed500...a96406e7aa285a3fb2a3e35900686d164a22bf02>
- <https://github.com/nicotine-plus/nicotine-plus/blob/master/pynicotine/gtkgui/search.py>
- <https://github.com/nicotine-plus/nicotine-plus/blob/master/pynicotine/search.py>

Executable claims remain scoped to the bundled proxy. Public-head statements are relevant-flow review rather than whole-tree execution.

## Public intent and overlap

Issue #3326 requested that Search Again “simply refresh” the respective search. Public discussion also states that a real repeat needs the current search removed and a new one added with a different token. The broad fresh-token replacement direction is therefore public prior art.

Reference: <https://github.com/nicotine-plus/nicotine-plus/issues/3326>

Rev0080 makes no novelty claim. It identifies the current result-cap dead end, validates its cross-commit history, and distinguishes best-effort page replacement from failure-atomic in-place migration.

## Contribution boundary

Nicotine+ permits AI tooling for learning and guided codebase research but disallows generated or AI-coauthored contribution content. Every generated test, model, script, patch, and document in this cube remains research-only.

Reference: <https://github.com/nicotine-plus/nicotine-plus/blob/master/CONTRIBUTING.md>
